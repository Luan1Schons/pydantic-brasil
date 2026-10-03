"""Validação, conversão e extração de metadados de Boletos Bancários e Arrecadação (FEBRABAN)."""

from __future__ import annotations

import datetime
import random
from typing import Any, ClassVar, Dict, Optional, cast

from pydantic_brasil.banco import BancoBR
from pydantic_brasil.base import BrazilianType
from pydantic_brasil.exceptions import BoletoInvalidError
from pydantic_brasil.money import DinheiroBRL


class BoletoBancario(BrazilianType):
    """Boleto Bancário e de Arrecadação/Concessionárias (FEBRABAN).

    Recursos:
    - Aceita Linha Digitável (47 dígitos de cobrança ou 48 de arrecadação) ou Código de Barras (44).
    - Conversão automática bidirecional entre linha digitável e código de barras.
    - Validação de dígitos verificadores por Módulo 10 e Módulo 11.
    - Extração do código do banco emissor e instância de `BancoBR`.
    - Extração do valor nominal do boleto como `DinheiroBRL`.
    - Extração do fator de vencimento e cálculo da data de vencimento (com regra FEBRABAN 2025).
    """

    EXPECTED_DIGITS: ClassVar[Optional[int]] = None
    DOC_NAME: ClassVar[str] = "Boleto Bancário / Linha Digitável"

    # Datas base oficiais FEBRABAN para cálculo do fator de vencimento
    BASE_DATE_1: ClassVar[datetime.date] = datetime.date(1997, 10, 7)
    BASE_DATE_2: ClassVar[datetime.date] = datetime.date(2025, 2, 22)

    _raw_digits: str
    _barcode: str
    _is_arrecadacao: bool

    def __new__(cls, value: Any) -> BoletoBancario:
        if isinstance(value, cls):
            return value

        cleaned = cls._clean_input(value)
        digits = cls._extract_digits(cleaned)

        if len(digits) not in (44, 47, 48):
            raise BoletoInvalidError(
                f"Boleto deve conter 44 (código de barras), 47 (linha digitável bancária) "
                f"ou 48 dígitos (linha digitável arrecadação). Recebido {len(digits)} dígitos.",
                value=value,
            )

        if len(set(digits)) == 1:
            raise BoletoInvalidError(
                f"Boleto não pode conter todos os dígitos iguais: '{value}'",
                value=value,
            )

        is_arrecadacao = digits[0] == "8"

        if is_arrecadacao:
            barcode = cls._validate_arrecadacao(digits)
        else:
            barcode = cls._validate_cobranca(digits)

        instance = cast(BoletoBancario, super().__new__(cls, digits))
        instance._raw_digits = digits
        instance._barcode = barcode
        instance._is_arrecadacao = is_arrecadacao
        return instance

    @classmethod
    def _validate(cls, value: str) -> str:
        digits = cls._extract_digits(value)
        if len(digits) not in (44, 47, 48):
            raise BoletoInvalidError(
                f"Boleto deve conter 44, 47 ou 48 dígitos (recebido {len(digits)})",
                value=value,
            )
        if digits[0] == "8":
            cls._validate_arrecadacao(digits)
        else:
            cls._validate_cobranca(digits)
        return digits

    @staticmethod
    def _modulo10(num: str) -> int:
        """Cálculo do dígito verificador via Módulo 10 FEBRABAN."""
        weights = [2, 1]
        total = 0
        w_idx = 0
        for char in reversed(num):
            prod = int(char) * weights[w_idx]
            total += (prod // 10) + (prod % 10)
            w_idx = (w_idx + 1) % 2
        rem = total % 10
        return 0 if rem == 0 else 10 - rem

    @staticmethod
    def _modulo11_cobranca(num: str) -> int:
        """Cálculo do dígito verificador geral do código de barras de cobrança bancária."""
        weights = [2, 3, 4, 5, 6, 7, 8, 9]
        total = 0
        w_idx = 0
        for char in reversed(num):
            total += int(char) * weights[w_idx]
            w_idx = (w_idx + 1) % len(weights)
        rem = total % 11
        if rem in (0, 1, 10):
            return 1
        return 11 - rem

    @classmethod
    def _validate_cobranca(cls, digits: str) -> str:
        """Valida e normaliza boleto de cobrança bancária tradicional."""
        if len(digits) == 47:
            # Linha digitável: AAABC.CCCCX DDDDD.DDDDDY EEEEE.EEEEEZ K VVVVVVVVVVVVVV
            field1, dv1 = digits[0:9], int(digits[9])
            field2, dv2 = digits[10:20], int(digits[20])
            field3, dv3 = digits[21:31], int(digits[31])
            dv_geral = int(digits[32])
            fator_e_valor = digits[33:47]

            if cls._modulo10(field1) != dv1:
                raise BoletoInvalidError(
                    "Dígito verificador inválido no campo 1 da linha digitável."
                )
            if cls._modulo10(field2) != dv2:
                raise BoletoInvalidError(
                    "Dígito verificador inválido no campo 2 da linha digitável."
                )
            if cls._modulo10(field3) != dv3:
                raise BoletoInvalidError(
                    "Dígito verificador inválido no campo 3 da linha digitável."
                )

            # Monta código de barras de 44 dígitos
            barcode = f"{field1[:4]}{dv_geral}{fator_e_valor}{field1[4:9]}{field2}{field3}"
            expected_dv = cls._modulo11_cobranca(barcode[:4] + barcode[5:])
            if dv_geral != expected_dv:
                raise BoletoInvalidError(
                    f"Dígito verificador geral inválido no boleto "
                    f"(esperado {expected_dv}, recebido {dv_geral})."
                )
            return barcode

        elif len(digits) == 44:
            # Código de barras
            dv_geral = int(digits[4])
            base_43 = digits[:4] + digits[5:]
            expected_dv = cls._modulo11_cobranca(base_43)
            if dv_geral != expected_dv:
                raise BoletoInvalidError(
                    f"Dígito verificador geral inválido no código de barras "
                    f"(esperado {expected_dv}, recebido {dv_geral})."
                )
            return digits

        raise BoletoInvalidError(
            f"Tamanho incompatível para boleto de cobrança: {len(digits)} dígitos."
        )

    @classmethod
    def _validate_arrecadacao(cls, digits: str) -> str:
        """Valida e normaliza boleto de arrecadação / concessionárias."""
        if len(digits) == 48:
            # 4 campos de 12 dígitos (11 dígitos + 1 DV)
            c1, dv1 = digits[0:11], int(digits[11])
            c2, dv2 = digits[12:23], int(digits[23])
            c3, dv3 = digits[24:35], int(digits[35])
            c4, dv4 = digits[36:47], int(digits[47])

            # Verifica o tipo de módulo pelo 3º dígito
            id_moeda = digits[2]
            use_modulo10 = id_moeda in ("6", "7")

            val_func = cls._modulo10 if use_modulo10 else cls._modulo11_arrecadacao
            if (
                val_func(c1) != dv1
                or val_func(c2) != dv2
                or val_func(c3) != dv3
                or val_func(c4) != dv4
            ):
                raise BoletoInvalidError(
                    "Dígito verificador de bloco inválido no boleto de arrecadação."
                )

            barcode = f"{c1}{c2}{c3}{c4}"
            return barcode

        elif len(digits) == 44:
            return digits

        raise BoletoInvalidError(
            f"Tamanho incompatível para boleto de arrecadação: {len(digits)} dígitos."
        )

    @staticmethod
    def _modulo11_arrecadacao(num: str) -> int:
        weights = [2, 3, 4, 5, 6, 7, 8, 9]
        total = sum(int(c) * weights[i % len(weights)] for i, c in enumerate(reversed(num)))
        rem = total % 11
        if rem in (0, 1):
            return 0
        if rem == 10:
            return 1
        return 11 - rem

    @property
    def is_arrecadacao(self) -> bool:
        """Retorna True se for um boleto de arrecadação / concessionária / tributo."""
        return self._is_arrecadacao

    @property
    def codigo_barras(self) -> str:
        """Retorna o código de barras canônico com 44 dígitos numéricos."""
        return self._barcode

    @property
    def linha_digitavel(self) -> str:
        """Retorna a linha digitável oficial formatada."""
        if self.is_arrecadacao:
            # 4 blocos de 12 dígitos
            if len(self._raw_digits) == 48:
                d = self._raw_digits
            else:
                b = self._barcode
                id_moeda = b[2]
                fn = self._modulo10 if id_moeda in ("6", "7") else self._modulo11_arrecadacao
                c1 = b[0:11] + str(fn(b[0:11]))
                c2 = b[11:22] + str(fn(b[11:22]))
                c3 = b[22:33] + str(fn(b[22:33]))
                c4 = b[33:44] + str(fn(b[33:44]))
                d = f"{c1}{c2}{c3}{c4}"
            return f"{d[0:12]} {d[12:24]} {d[24:36]} {d[36:48]}"

        # Boleto de cobrança bancária
        b = self._barcode
        c1_base = b[0:4] + b[19:24]
        c1 = c1_base + str(self._modulo10(c1_base))

        c2_base = b[24:34]
        c2 = c2_base + str(self._modulo10(c2_base))

        c3_base = b[34:44]
        c3 = c3_base + str(self._modulo10(c3_base))

        c4 = b[4]
        c5 = b[5:19]
        return f"{c1[:5]}.{c1[5:]} {c2[:5]}.{c2[5:]} {c3[:5]}.{c3[5:]} {c4} {c5}"

    @property
    def formatted(self) -> str:
        """Retorna a representação formatada da linha digitável."""
        return self.linha_digitavel

    @property
    def masked(self) -> str:
        """Retorna a linha digitável com os campos centrais mascarados."""
        ld = self.linha_digitavel
        if len(ld) > 20:
            return f"{ld[:10]}...{ld[-14:]}"
        return ld

    @property
    def codigo_banco(self) -> Optional[str]:
        """Retorna o código COMPE de 3 dígitos do banco emissor (ex: '001', '237')."""
        if self.is_arrecadacao:
            return None
        return self._barcode[:3]

    @property
    def banco(self) -> Optional[BancoBR]:
        """Retorna a instituição financeira emissora como objeto `BancoBR`."""
        if not self.codigo_banco:
            return None
        try:
            return BancoBR(self.codigo_banco)
        except Exception:
            return None

    @property
    def fator_vencimento(self) -> Optional[int]:
        """Retorna o fator de vencimento com 4 dígitos numéricos."""
        if self.is_arrecadacao:
            return None
        fator = int(self._barcode[5:9])
        return fator if fator > 0 else None

    @property
    def data_vencimento(self) -> Optional[datetime.date]:
        """Calcula a data exata de vencimento do título a partir do fator de vencimento FEBRABAN."""
        fator = self.fator_vencimento
        if not fator:
            return None

        # Regra FEBRABAN: Fatores a partir de 1000 começaram em 03/07/2000 (base 07/10/1997)
        # Em 21/02/2025 o fator atingiu 9999 e reiniciou em 1000 a partir de 22/02/2025
        # Comparamos com a data atual para inferir o ciclo correto
        hoje = datetime.date.today()
        data_ciclo_1 = self.BASE_DATE_1 + datetime.timedelta(days=fator)
        data_ciclo_2 = self.BASE_DATE_2 + datetime.timedelta(days=fator - 1000)

        if hoje >= datetime.date(2025, 2, 22):
            # Se a data do ciclo 1 for muito no passado (> 5 anos), assume o ciclo 2
            if abs((data_ciclo_2 - hoje).days) < abs((data_ciclo_1 - hoje).days):
                return data_ciclo_2
        return data_ciclo_1

    @property
    def valor(self) -> Optional[DinheiroBRL]:
        """Retorna o valor nominal do boleto como `DinheiroBRL`."""
        if self.is_arrecadacao:
            # Em arrecadação, o valor está nas posições 4 a 15 do código de barras
            cents = int(self._barcode[4:15])
        else:
            cents = int(self._barcode[9:19])
        if cents == 0:
            return None
        return DinheiroBRL.from_centavos(cents)

    @classmethod
    def generate(
        cls,
        banco: str = "001",
        valor: float = 125.50,
        dias_vencimento: int = 5,
        formatted: bool = True,
    ) -> BoletoBancario:
        """Gera um boleto de cobrança bancária válido para testes e fixtures."""
        banco_code = str(banco).zfill(3)
        moeda = "9"
        cents_str = str(int(round(valor * 100))).zfill(10)

        # Fator de vencimento referente à data desejada
        data_venc = datetime.date.today() + datetime.timedelta(days=dias_vencimento)
        if data_venc >= datetime.date(2025, 2, 22):
            fator = 1000 + (data_venc - cls.BASE_DATE_2).days
        else:
            fator = (data_venc - cls.BASE_DATE_1).days
        fator_str = str(fator).zfill(4)

        # Campo livre (25 dígitos)
        campo_livre = "".join(str(random.randint(0, 9)) for _ in range(25))

        base_sem_dv = f"{banco_code}{moeda}{fator_str}{cents_str}{campo_livre}"
        dv_geral = cls._modulo11_cobranca(base_sem_dv)
        barcode_44 = f"{banco_code}{moeda}{dv_geral}{fator_str}{cents_str}{campo_livre}"

        instance = cls(barcode_44)
        if formatted:
            return cls(instance.linha_digitavel)
        return instance

    @classmethod
    def openapi_schema_extra(cls) -> Dict[str, Any]:
        return {
            "type": "string",
            "title": "BoletoBancario",
            "description": "Linha Digitável (47/48 dígitos) ou Código de Barras (44 dígitos)",
            "examples": [
                "00190.00009 01234.567802 00000.000001 5 100000000000",
                "00195100000000000000000012345678000000000001",
            ],
            "pattern": r"^(\d{44}|\d{47}|\d{48})$",
        }


# Aliases
LinhaDigitavel = BoletoBancario
CodigoBarrasBoleto = BoletoBancario
