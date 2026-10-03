"""PIS, PASEP, NIS and NIT validation and formatting."""

from __future__ import annotations

import random
from typing import ClassVar, Optional

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.exceptions import PISInvalidError


class PIS(BrazilianType):
    """Brazilian PIS/PASEP/NIS/NIT document validator and formatter.

    PIS (Programa de Integração Social) and PASEP (Programa de Formação do
    Patrimônio do Servidor Público) share the same 11-digit structure and Modulo 11
    checksum verification.
    """

    EXPECTED_DIGITS: ClassVar[Optional[int]] = 11
    DOC_NAME: ClassVar[str] = "PIS/PASEP"
    MULTIPLIERS: ClassVar[list[int]] = [3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    @classmethod
    def _validate(cls, value: str) -> str:
        digits = cls._extract_digits(value)

        if len(digits) != 11:
            raise PISInvalidError(
                f"PIS must have exactly 11 digits (received '{value}')",
                value=value,
            )

        if len(set(digits)) == 1:
            raise PISInvalidError(
                f"PIS cannot have all repeated digits: '{value}'",
                value=value,
            )

        total = sum(int(digits[i]) * cls.MULTIPLIERS[i] for i in range(10))
        rem = total % 11
        expected_dv = 0 if rem < 2 else 11 - rem

        if int(digits[10]) != expected_dv:
            raise PISInvalidError(
                f"Invalid PIS checksum for '{value}'",
                value=value,
            )

        return digits

    @property
    def formatted(self) -> str:
        """Returns standard formatted PIS (XXX.XXXXX.XX-X)."""
        d = self.digits
        return f"{d[:3]}.{d[3:8]}.{d[8:10]}-{d[10]}"

    @property
    def masked(self) -> str:
        """Returns LGPD-compliant masked PIS (XXX.*****.**-X)."""
        d = self.digits
        return f"{d[:3]}.*****.**-{d[10]}"

    @classmethod
    def generate(cls, formatted: bool = False) -> PIS:
        """Generates a valid PIS document for testing purposes."""
        while True:
            first_10 = [random.randint(0, 9) for _ in range(10)]
            if len(set(first_10)) > 1:
                break

        total = sum(first_10[i] * cls.MULTIPLIERS[i] for i in range(10))
        rem = total % 11
        dv = 0 if rem < 2 else 11 - rem
        raw = "".join(str(d) for d in first_10) + str(dv)
        instance = cls(raw)
        if formatted:
            return cls(instance.formatted)
        return instance


# Common aliases in Brazilian business domain
PASEP = PIS
NIS = PIS
NIT = PIS
