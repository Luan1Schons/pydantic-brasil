"""Validação e formatação de códigos de produtos GTIN / EAN (GS1 Brasil)."""

from __future__ import annotations

import random
from typing import Any, ClassVar, Dict, Optional

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.exceptions import GTINInvalidError


class GTIN(BrazilianType):
    """Código Global de Item Comercial (GTIN / EAN) da GS1.

    Recursos:
    - Validação de tamanhos GS1: GTIN-8, GTIN-12 (UPC), GTIN-13 (EAN-13) e GTIN-14 (ITF-14).
    - Verificação de dígito verificador via algoritmo Módulo 10 padrão GS1 internacional.
    - `.is_brazilian`: Identifica se o produto possui prefixo atribuído à GS1 Brasil (789 ou 790).
    - `.gtin_type`: Categoria identificada ('GTIN-8', 'GTIN-12', 'GTIN-13', 'GTIN-14').
    - `.generate(length=13, brazilian=True)`: Gerador para testes.
    """

    EXPECTED_DIGITS: ClassVar[Optional[int]] = None
    DOC_NAME: ClassVar[str] = "Código de Barras GTIN/EAN"

    VALID_LENGTHS: ClassVar[tuple[int, ...]] = (8, 12, 13, 14)

    @staticmethod
    def _calculate_dv(base_digits: str) -> int:
        """Calcula o DV GS1 usando pesos alternados 3 e 1 da direita para a esquerda."""
        weights = [3, 1]
        total = 0
        w_idx = 0
        for char in reversed(base_digits):
            total += int(char) * weights[w_idx]
            w_idx = (w_idx + 1) % 2
        rem = total % 10
        return 0 if rem == 0 else 10 - rem

    @classmethod
    def _validate(cls, value: str) -> str:
        digits = cls._extract_digits(value)

        if len(digits) not in cls.VALID_LENGTHS:
            raise GTINInvalidError(
                f"Código GTIN/EAN deve conter 8, 12, 13 ou 14 dígitos (recebido {len(digits)}).",
                value=value,
            )

        if len(set(digits)) == 1:
            raise GTINInvalidError(
                f"Código GTIN não pode conter todos os dígitos iguais: '{value}'",
                value=value,
            )

        base = digits[:-1]
        given_dv = int(digits[-1])
        expected_dv = cls._calculate_dv(base)

        if given_dv != expected_dv:
            raise GTINInvalidError(
                f"Dígito verificador inválido para o código GTIN '{value}' "
                f"(esperado '{expected_dv}', recebido '{given_dv}')",
                value=value,
            )

        return digits

    @property
    def gtin_type(self) -> str:
        """Retorna o tipo oficial do identificador ('GTIN-8', 'GTIN-12', 'GTIN-13', 'GTIN-14')."""
        return f"GTIN-{len(self.digits)}"

    @property
    def is_brazilian(self) -> bool:
        """Retorna True se o código possuir o prefixo nacional 789 ou 790 da GS1 Brasil."""
        d = self.digits
        if len(d) == 14:
            # Em GTIN-14, o primeiro dígito é o indicador de embalagem/logística
            return d[1:4] in ("789", "790")
        if len(d) == 13:
            return d[:3] in ("789", "790")
        return False

    @property
    def prefix(self) -> str:
        """Retorna os 3 primeiros dígitos do código de barras."""
        d = self.digits
        if len(d) == 14:
            return d[1:4]
        return d[:3]

    @property
    def dv(self) -> str:
        """Retorna o dígito verificador (último caractere)."""
        return self.digits[-1]

    @property
    def formatted(self) -> str:
        """Retorna o código GTIN como string de dígitos numéricos."""
        return self.digits

    @property
    def masked(self) -> str:
        """Retorna o GTIN mascarado preservando o prefixo do país e o dígito verificador."""
        d = self.digits
        if len(d) >= 12:
            return f"{d[:3]}****{d[-4:]}"
        return f"{d[:2]}***{d[-2:]}"

    @classmethod
    def generate(cls, length: int = 13, brazilian: bool = True) -> GTIN:
        """Gera um código GTIN/EAN válido para testes."""
        if length not in cls.VALID_LENGTHS:
            length = 13

        if length in (13, 14) and brazilian:
            prefix = random.choice(["789", "790"])
            if length == 14:
                ind = str(random.randint(1, 8))
                needed = 14 - 1 - 1 - 3  # total 14: ind(1) + prefix(3) + body(needed) + dv(1)
                body = "".join(str(random.randint(0, 9)) for _ in range(needed))
                base = f"{ind}{prefix}{body}"
            else:
                needed = 13 - 1 - 3
                body = "".join(str(random.randint(0, 9)) for _ in range(needed))
                base = f"{prefix}{body}"
        else:
            base = "".join(str(random.randint(0, 9)) for _ in range(length - 1))

        dv = cls._calculate_dv(base)
        return cls(f"{base}{dv}")

    @classmethod
    def openapi_schema_extra(cls) -> Dict[str, Any]:
        return {
            "type": "string",
            "title": "GTIN",
            "description": "Código de Barras GTIN / EAN (8, 12, 13 ou 14 dígitos)",
            "examples": ["7891234567895", "7901234567892"],
            "pattern": r"^(\d{8}|\d{12}|\d{13}|\d{14})$",
        }


# Aliases
EAN = GTIN
EAN13 = GTIN
