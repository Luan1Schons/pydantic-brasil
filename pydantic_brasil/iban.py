"""Validação e formatação de IBAN brasileiro (Resolução Bacen nº 3.400 e Circular nº 3.625)."""

from __future__ import annotations

import re
from typing import Any, ClassVar, Dict, Optional

from pydantic_brasil.banco import BancoBR
from pydantic_brasil.base import BrazilianType
from pydantic_brasil.exceptions import IBANInvalidError


class IBANBrasil(BrazilianType):
    """Código Internacional de Conta Bancária Brasileiro (IBAN).

    Estrutura de 29 caracteres alfanuméricos estipulada pelo Banco Central do Brasil:
    - 2 letras: País ('BR')
    - 2 dígitos: Dígitos verificadores calculados por Módulo 97 (ISO 7064)
    - 8 dígitos: Código ISPB da instituição financeira no Bacen
    - 5 dígitos: Número da agência bancária
    - 10 dígitos: Número da conta bancária
    - 1 caractere: Tipo de conta ('C' para Corrente, 'P' para Poupança)
    - 1 caractere: Identificador de titularidade ('1', '2', etc.)
    """

    EXPECTED_DIGITS: ClassVar[Optional[int]] = None
    SERIALIZE_AS_DIGITS: ClassVar[bool] = False
    DOC_NAME: ClassVar[str] = "IBAN Brasileiro"
    REGEX: ClassVar[re.Pattern[str]] = re.compile(r"^BR\d{2}\d{8}\d{5}\d{10}[A-Z0-9]{2}$")

    @classmethod
    def _calculate_dv(cls, bban_25: str) -> str:
        """Calcula os 2 dígitos verificadores para o padrão brasileiro de 25 caracteres."""
        # Rearranjo com BR00 ao final: BBAN + 'B' (11) + 'R' (27) + '00'
        rearranged = f"{bban_25}BR00"
        numeric_str = "".join(
            str(ord(char) - 55) if char.isalpha() else char for char in rearranged
        )
        rem = int(numeric_str) % 97
        dv = 98 - rem
        return f"{dv:02d}"

    @classmethod
    def _validate(cls, value: str) -> str:
        clean = re.sub(r"[\s\-]", "", value.upper())

        if len(clean) != 29:
            raise IBANInvalidError(
                f"IBAN brasileiro deve ter exatamente 29 caracteres (recebido {len(clean)}).",
                value=value,
            )

        if not clean.startswith("BR"):
            raise IBANInvalidError(
                f"IBAN brasileiro deve iniciar com o código de país 'BR' (recebido '{clean[:2]}').",
                value=value,
            )

        if not cls.REGEX.match(clean):
            raise IBANInvalidError(
                f"Estrutura alfanumérica inválida para o IBAN brasileiro: '{value}'",
                value=value,
            )

        # Validação Módulo 97 (ISO 7064)
        rearranged = f"{clean[4:]}{clean[:4]}"
        numeric_str = "".join(str(ord(c) - 55) if c.isalpha() else c for c in rearranged)

        if int(numeric_str) % 97 != 1:
            raise IBANInvalidError(
                f"Dígitos verificadores do IBAN inválidos pela regra ISO 7064: '{value}'",
                value=value,
            )

        return clean

    @property
    def country_code(self) -> str:
        """Retorna a sigla de 2 letras do país ('BR')."""
        return str(self)[:2]

    @property
    def check_digits(self) -> str:
        """Retorna os 2 dígitos verificadores do IBAN."""
        return str(self)[2:4]

    @property
    def ispb(self) -> str:
        """Retorna o código ISPB de 8 dígitos da instituição financeira."""
        return str(self)[4:12]

    @property
    def banco(self) -> Optional[BancoBR]:
        """Localiza a instituição financeira no catálogo `BancoBR` através do ISPB."""
        results = BancoBR.search(self.ispb)
        if results:
            return BancoBR(results[0].code)
        return None

    @property
    def agencia(self) -> str:
        """Retorna os 5 dígitos do número da agência bancária."""
        return str(self)[12:17]

    @property
    def conta(self) -> str:
        """Retorna os 10 dígitos do número da conta bancária."""
        return str(self)[17:27]

    @property
    def tipo_conta(self) -> str:
        """Retorna o tipo de conta ('C' = Corrente, 'P' = Poupança)."""
        return str(self)[27]

    @property
    def titularidade(self) -> str:
        """Retorna o identificador de titularidade da conta."""
        return str(self)[28]

    @property
    def formatted(self) -> str:
        """Retorna o IBAN formatado no padrão internacional com grupos de 4 caracteres."""
        s = str(self)
        chunks = [s[i : i + 4] for i in range(0, len(s), 4)]
        return " ".join(chunks)

    @property
    def masked(self) -> str:
        """Retorna o IBAN mascarado ocultando agência e número de conta sensíveis."""
        s = str(self)
        return f"{s[:4]} {s[4:8]} **** **** **** {s[20:24]} {s[24:]}"

    @classmethod
    def generate(
        cls,
        ispb: str = "00000000",
        agencia: int = 1,
        conta: int = 123456,
        tipo_conta: str = "C",
        titularidade: str = "1",
        formatted: bool = False,
    ) -> IBANBrasil:
        """Gera um IBAN brasileiro válido para testes e fixtures."""
        ispb_str = str(ispb).zfill(8)[:8]
        agencia_str = str(agencia).zfill(5)[:5]
        conta_str = str(conta).zfill(10)[:10]
        tipo_str = tipo_conta.upper()[:1] or "C"
        tit_str = str(titularidade)[:1] or "1"

        bban_25 = f"{ispb_str}{agencia_str}{conta_str}{tipo_str}{tit_str}"
        dv = cls._calculate_dv(bban_25)
        raw = f"BR{dv}{bban_25}"

        instance = cls(raw)
        return cls(instance.formatted if formatted else raw)

    @classmethod
    def openapi_schema_extra(cls) -> Dict[str, Any]:
        return {
            "type": "string",
            "title": "IBANBrasil",
            "description": "Código Internacional de Conta Bancária Brasileiro (IBAN)",
            "examples": [
                "BR120000000000010000123456C1",
                "BR12 0000 0000 0001 0000 1234 56C1",
            ],
            "pattern": r"^BR\d{2}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?[A-Z0-9]{2}$",
        }


# Alias
IBAN = IBANBrasil
