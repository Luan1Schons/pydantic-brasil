"""Validação e formatação de Chave de Acesso de DF-e (NF-e, NFC-e, CT-e, MDF-e)."""

from __future__ import annotations

import random
from typing import Any, ClassVar, Dict, Optional

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.cnpj import CNPJ
from pydantic_brasil.exceptions import ChaveDFeInvalidError


class ChaveDFe(BrazilianType):
    """Chave de Acesso de Documentos Fiscais Eletrônicos (NF-e, NFC-e, CT-e, MDF-e).

    Valida a chave oficial de 44 dígitos numéricos estabelecida pelo Manual de Orientação
    do Contribuinte (MOC) da SEFAZ, com cálculo e verificação de dígito verificador Módulo 11.
    """

    EXPECTED_DIGITS: ClassVar[Optional[int]] = 44
    DOC_NAME: ClassVar[str] = "Chave de Acesso DF-e"

    UF_IBGE_CODES: ClassVar[Dict[int, str]] = {
        11: "RO",
        12: "AC",
        13: "AM",
        14: "RR",
        15: "PA",
        16: "AP",
        17: "TO",
        21: "MA",
        22: "PI",
        23: "CE",
        24: "RN",
        25: "PB",
        26: "PE",
        27: "AL",
        28: "SE",
        29: "BA",
        31: "MG",
        32: "ES",
        33: "RJ",
        35: "SP",
        41: "PR",
        42: "SC",
        43: "RS",
        50: "MS",
        51: "MT",
        52: "GO",
        53: "DF",
    }
    UF_TO_IBGE: ClassVar[Dict[str, int]] = {v: k for k, v in UF_IBGE_CODES.items()}

    MODEL_NAMES: ClassVar[Dict[str, str]] = {
        "55": "NF-e (Nota Fiscal Eletrônica)",
        "65": "NFC-e (Nota Fiscal de Consumidor Eletrônica)",
        "57": "CT-e (Conhecimento de Transporte Eletrônico)",
        "58": "MDF-e (Manifesto Eletrônico de Documentos Fiscais)",
    }

    @staticmethod
    def _calculate_dv(base_43: str) -> int:
        """Calcula o dígito verificador da SEFAZ para os 43 primeiros dígitos."""
        weights = [2, 3, 4, 5, 6, 7, 8, 9]
        total = 0
        w_idx = 0
        for char in reversed(base_43):
            total += int(char) * weights[w_idx]
            w_idx = (w_idx + 1) % len(weights)
        rem = total % 11
        return 0 if rem in (0, 1) else 11 - rem

    @classmethod
    def _validate(cls, value: str) -> str:
        digits = cls._extract_digits(value)

        if len(digits) != 44:
            raise ChaveDFeInvalidError(
                f"Chave de DF-e deve conter exatamente 44 dígitos (recebido {len(digits)})",
                value=value,
            )

        if len(set(digits)) == 1:
            raise ChaveDFeInvalidError(
                f"Chave de DF-e não pode conter todos os dígitos iguais: '{value}'",
                value=value,
            )

        uf_code = int(digits[:2])
        if uf_code not in cls.UF_IBGE_CODES:
            raise ChaveDFeInvalidError(
                f"Código de UF '{digits[:2]}' inválido na chave de DF-e '{value}'",
                value=value,
            )

        expected_dv = cls._calculate_dv(digits[:43])
        if int(digits[43]) != expected_dv:
            raise ChaveDFeInvalidError(
                f"Dígito verificador inválido na chave de DF-e '{value}' "
                f"(esperado '{expected_dv}', recebido '{digits[43]}')",
                value=value,
            )

        return digits

    @property
    def uf_code(self) -> int:
        """Retorna o código IBGE da UF de emissão (ex: 35 para SP)."""
        return int(self.digits[:2])

    @property
    def uf(self) -> str:
        """Retorna a sigla da UF de emissão (ex: 'SP')."""
        return self.UF_IBGE_CODES.get(self.uf_code, "UNKNOWN")

    @property
    def ano_mes(self) -> str:
        """Retorna o ano e mês de emissão no formato AAMM (ex: '2410')."""
        return self.digits[2:6]

    @property
    def year(self) -> int:
        """Retorna o ano de emissão com 4 dígitos (ex: 2024)."""
        return 2000 + int(self.digits[2:4])

    @property
    def month(self) -> int:
        """Retorna o mês de emissão (1 a 12)."""
        return int(self.digits[4:6])

    @property
    def cnpj_emitente(self) -> CNPJ:
        """Retorna o CNPJ do emitente como objeto CNPJ validado."""
        return CNPJ(self.digits[6:20])

    @property
    def modelo(self) -> str:
        """Retorna o código do modelo fiscal (ex: '55' para NF-e, '65' para NFC-e)."""
        return self.digits[20:22]

    @property
    def modelo_nome(self) -> str:
        """Retorna o nome descritivo do modelo fiscal."""
        return self.MODEL_NAMES.get(self.modelo, f"Modelo {self.modelo}")

    @property
    def serie(self) -> str:
        """Retorna o número de série do documento fiscal (3 dígitos)."""
        return self.digits[22:25]

    @property
    def numero(self) -> str:
        """Retorna o número do documento fiscal (9 dígitos)."""
        return self.digits[25:34]

    @property
    def tipo_emissao(self) -> str:
        """Retorna o tipo de emissão (1=Normal, 2=Contingência FS, etc.)."""
        return self.digits[34:35]

    @property
    def codigo_numerico(self) -> str:
        """Retorna o código numérico aleatório de 8 dígitos gerado pelo emissor."""
        return self.digits[35:43]

    @property
    def dv(self) -> str:
        """Retorna o dígito verificador da chave (44º dígito)."""
        return self.digits[43]

    @property
    def formatted(self) -> str:
        """Retorna a chave formatada no padrão SEFAZ em blocos de 4 dígitos."""
        d = self.digits
        return " ".join(d[i : i + 4] for i in range(0, 44, 4))

    @property
    def masked(self) -> str:
        """Retorna a chave mascarada protegendo a identidade do emitente."""
        d = self.digits
        return (
            f"{d[:6]} {d[6:10]} **** **** **{d[20:22]} {d[22:26]} "
            f"{d[26:30]} {d[30:34]} {d[34:38]} {d[38:42]} **{d[42:]}"
        )

    @classmethod
    def generate(
        cls,
        uf: str = "SP",
        year: int = 24,
        month: int = 10,
        modelo: str = "55",
        serie: int = 1,
        numero: int = 12345,
        cnpj: Optional[str] = None,
        formatted: bool = False,
    ) -> ChaveDFe:
        """Gera uma Chave de Acesso de DF-e válida para testes."""
        uf_code = cls.UF_TO_IBGE.get(uf.upper().strip(), 35)
        aamm = f"{year % 100:02d}{month:02d}"
        cnpj_digits = CNPJ(cnpj).digits if cnpj else CNPJ.generate().digits
        modelo_str = str(modelo).zfill(2)
        serie_str = str(serie).zfill(3)
        numero_str = str(numero).zfill(9)
        tipo_emissao = "1"
        codigo_aleatorio = "".join(str(random.randint(0, 9)) for _ in range(8))

        base_43 = (
            f"{uf_code:02d}"
            f"{aamm}"
            f"{cnpj_digits}"
            f"{modelo_str}"
            f"{serie_str}"
            f"{numero_str}"
            f"{tipo_emissao}"
            f"{codigo_aleatorio}"
        )
        dv = cls._calculate_dv(base_43)
        chave_44 = f"{base_43}{dv}"
        instance = cls(chave_44)
        return cls(instance.formatted if formatted else chave_44)

    @classmethod
    def openapi_schema_extra(cls) -> Dict[str, Any]:
        return {
            "type": "string",
            "title": "ChaveDFe",
            "description": "Chave de Acesso de DF-e (NF-e, NFC-e, CT-e, MDF-e com 44 dígitos)",
            "examples": [
                "352410000000000000550010000123451123456781",
                "3524 1000 0000 0000 0055 0010 0001 2345 1123 4567 81",
            ],
            "pattern": r"^\d{44}$",
        }


# Aliases
ChaveAcessoNFe = ChaveDFe
ChaveNFe = ChaveDFe
