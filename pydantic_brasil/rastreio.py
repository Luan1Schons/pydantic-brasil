"""Validação e formatação de código de rastreamento dos Correios (Padrão S10 UPU)."""

from __future__ import annotations

import random
import re
from typing import Any, ClassVar, Dict, List, Optional

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.exceptions import RastreioInvalidError


class RastreioCorreios(BrazilianType):
    """Código de rastreamento postal dos Correios (Padrão S10 da UPU).

    Composto por 13 caracteres:
    - 2 letras: Tipo de serviço postal (ex: QC, NL, AA, SS)
    - 8 dígitos: Número sequencial da encomenda
    - 1 dígito: Verificador calculado via Módulo 11 com pesos [8, 6, 4, 2, 3, 5, 9, 7]
    - 2 letras: Código do país de origem (ex: BR, CN, US)
    """

    EXPECTED_DIGITS: ClassVar[Optional[int]] = None
    SERIALIZE_AS_DIGITS: ClassVar[bool] = False
    DOC_NAME: ClassVar[str] = "Código de Rastreamento dos Correios"
    REGEX: ClassVar[re.Pattern[str]] = re.compile(r"^[A-Z]{2}\d{9}[A-Z]{2}$")
    WEIGHTS: ClassVar[List[int]] = [8, 6, 4, 2, 3, 5, 9, 7]

    @classmethod
    def _calculate_dv(cls, digits_8: str) -> int:
        """Calcula o dígito verificador segundo a norma S10 da UPU."""
        total = sum(int(digits_8[i]) * cls.WEIGHTS[i] for i in range(8))
        rem = total % 11
        if rem == 0:
            return 5
        if rem == 1:
            return 0
        return 11 - rem

    @classmethod
    def _validate(cls, value: str) -> str:
        clean = re.sub(r"\s+", "", value.upper())

        if len(clean) != 13 or not cls.REGEX.match(clean):
            raise RastreioInvalidError(
                f"Código de rastreamento deve ter 13 caracteres (2 letras, 9 dígitos, 2 letras). "
                f"Recebido: '{value}'",
                value=value,
            )

        serial_8 = clean[2:10]
        given_dv = int(clean[10])
        expected_dv = cls._calculate_dv(serial_8)

        if given_dv != expected_dv:
            raise RastreioInvalidError(
                f"Dígito verificador inválido para o código de rastreamento '{value}' "
                f"(esperado '{expected_dv}', recebido '{given_dv}')",
                value=value,
            )

        return clean

    @property
    def service_code(self) -> str:
        """Retorna o código do serviço postal com 2 letras (ex: 'QC', 'SS')."""
        return str(self)[:2]

    @property
    def serial_number(self) -> str:
        """Retorna o número sequencial de 8 dígitos."""
        return str(self)[2:10]

    @property
    def dv(self) -> str:
        """Retorna o dígito verificador oficial."""
        return str(self)[10]

    @property
    def origin_country(self) -> str:
        """Retorna a sigla de 2 letras do país de origem (ex: 'BR')."""
        return str(self)[11:13]

    @property
    def is_national(self) -> bool:
        """Retorna True se o pacote for de postagem nacional (Brasil)."""
        return self.origin_country == "BR"

    @property
    def tracking_url(self) -> str:
        """Retorna o link oficial para acompanhamento no portal dos Correios."""
        return f"https://rastreamento.correios.com.br/app/index.php?codigo={self}"

    @property
    def formatted(self) -> str:
        """Retorna o código formatado com espaços: `AA 12345678 9 BR`."""
        s = str(self)
        return f"{s[:2]} {s[2:10]} {s[10]} {s[11:]}"

    @property
    def masked(self) -> str:
        """Retorna o código parcialmente mascarado."""
        s = str(self)
        return f"{s[:2]} {s[2:6]}**** {s[10]} {s[11:]}"

    @classmethod
    def generate(
        cls,
        service: str = "QC",
        country: str = "BR",
        formatted: bool = False,
    ) -> RastreioCorreios:
        """Gera um código de rastreamento dos Correios válido para testes."""
        service_clean = service.upper()[:2].ljust(2, "A")
        country_clean = country.upper()[:2].ljust(2, "B")
        serial = "".join(str(random.randint(0, 9)) for _ in range(8))
        dv = cls._calculate_dv(serial)
        code = f"{service_clean}{serial}{dv}{country_clean}"
        instance = cls(code)
        return cls(instance.formatted if formatted else code)

    @classmethod
    def openapi_schema_extra(cls) -> Dict[str, Any]:
        return {
            "type": "string",
            "title": "RastreioCorreios",
            "description": "Código de rastreamento dos Correios padrão S10 UPU (13 caracteres)",
            "examples": ["QC123456785BR", "AA 12345678 5 BR"],
            "pattern": r"^[A-Z]{2}\s?\d{8}\s?\d\s?[A-Z]{2}$",
        }


# Alias
CodigoRastreio = RastreioCorreios
