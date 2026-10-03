"""Cartão Nacional de Saúde (CNS / SUS) validation and formatting."""

from __future__ import annotations

import random
from typing import ClassVar, Optional

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.exceptions import CNSInvalidError


class CNS(BrazilianType):
    """Brazilian National Health Card (Cartão Nacional de Saúde - SUS).

    Validates according to DATASUS / Ministério da Saúde specifications:
    - 15 digits starting with 1, 2, 7, 8, or 9.
    - Definitive numbers (starting with 1 or 2) use an 11-digit base with Modulo 11 check.
    - Provisory numbers (starting with 7, 8, or 9) use a 15-digit weighted sum modulo 11 check.
    """

    EXPECTED_DIGITS: ClassVar[Optional[int]] = 15
    DOC_NAME: ClassVar[str] = "Cartão Nacional de Saúde (CNS)"

    @classmethod
    def _validate(cls, value: str) -> str:
        digits = cls._extract_digits(value)

        if len(digits) != 15:
            raise CNSInvalidError(
                f"CNS must have exactly 15 digits (received '{value}')",
                value=value,
            )

        first_digit = digits[0]
        if first_digit not in ("1", "2", "7", "8", "9"):
            raise CNSInvalidError(
                f"CNS must start with 1, 2, 7, 8, or 9 (received '{value}')",
                value=value,
            )

        if first_digit in ("1", "2"):
            # Definitive CNS
            s = sum(int(digits[i]) * (15 - i) for i in range(11))
            rem = s % 11
            dv = 11 - rem
            if dv == 11:
                dv = 0

            if dv == 10:
                s += 2
                rem = s % 11
                dv = 11 - rem
                expected_suffix = f"001{dv}"
            else:
                expected_suffix = f"000{dv}"

            if digits[11:] != expected_suffix:
                raise CNSInvalidError(
                    f"Invalid checksum for definitive CNS '{value}'",
                    value=value,
                )
        else:
            # Provisory CNS (starts with 7, 8, or 9)
            total = sum(int(digits[i]) * (15 - i) for i in range(15))
            if total % 11 != 0:
                raise CNSInvalidError(
                    f"Invalid checksum for provisory CNS '{value}'",
                    value=value,
                )

        return digits

    @property
    def is_definitivo(self) -> bool:
        """Returns True if the CNS is definitive (starts with 1 or 2)."""
        return self.digits[0] in ("1", "2")

    @property
    def is_provisorio(self) -> bool:
        """Returns True if the CNS is provisory (starts with 7, 8, or 9)."""
        return self.digits[0] in ("7", "8", "9")

    @property
    def formatted(self) -> str:
        """Returns standard formatted CNS (XXX XXXX XXXX XXXX)."""
        d = self.digits
        return f"{d[:3]} {d[3:7]} {d[7:11]} {d[11:]}"

    @property
    def masked(self) -> str:
        """Returns LGPD-compliant masked CNS (XXX **** **** XXXX)."""
        d = self.digits
        return f"{d[:3]} **** **** {d[11:]}"

    @classmethod
    def generate(cls, definitivo: bool = True, formatted: bool = False) -> CNS:
        """Generates a valid CNS number for testing purposes."""
        if definitivo:
            first_digit = random.choice([1, 2])
            body = [first_digit] + [random.randint(0, 9) for _ in range(10)]
            s = sum(body[i] * (15 - i) for i in range(11))
            rem = s % 11
            dv = 11 - rem
            if dv == 11:
                dv = 0
            if dv == 10:
                s += 2
                rem = s % 11
                dv = 11 - rem
                suffix = f"001{dv}"
            else:
                suffix = f"000{dv}"
            raw = "".join(str(d) for d in body) + suffix
        else:
            first_digit = random.choice([7, 8, 9])
            while True:
                candidate = [first_digit] + [random.randint(0, 9) for _ in range(13)]
                s = sum(candidate[i] * (15 - i) for i in range(14))
                # Last weight is (15 - 14) = 1
                # (s + last_digit * 1) % 11 == 0  =>  last_digit = (11 - (s % 11)) % 11
                last_digit = (11 - (s % 11)) % 11
                if last_digit < 10:
                    raw = "".join(str(d) for d in candidate) + str(last_digit)
                    break

        instance = cls(raw)
        if formatted:
            return cls(instance.formatted)
        return instance


CartaoSUS = CNS
