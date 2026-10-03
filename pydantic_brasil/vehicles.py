"""Vehicle and Driver documents (PlacaVeiculo, RENAVAM, CNH)."""

from __future__ import annotations

import re
from typing import Any, ClassVar, Dict, List

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.exceptions import (
    CNHInvalidError,
    RenavamInvalidError,
    VehiclePlateInvalidError,
)


class PlacaVeiculo(BrazilianType):
    """Brazilian vehicle license plate (standard and Mercosul format).

    Features:
    - Validates traditional format (`ABC-1234`) and Mercosul format (`ABC1D23`).
    - Bidirectional conversion between traditional and Mercosul patterns using
      the official Denatran table.
    - `.is_mercosul`: Indicates whether the plate uses the Mercosul pattern.
    - `.to_mercosul()`: Converts a traditional plate to its Mercosul counterpart.
    - `.to_antiga()`: Converts a Mercosul plate to its traditional counterpart.
    """

    TRADITIONAL_REGEX: ClassVar[re.Pattern[str]] = re.compile(r"^[A-Z]{3}-?\d{4}$")
    MERCOSUL_REGEX: ClassVar[re.Pattern[str]] = re.compile(r"^[A-Z]{3}\d[A-Z]\d{2}$")

    # Official Denatran conversion mapping for 5th character
    NUMBER_TO_LETTER: ClassVar[Dict[str, str]] = {
        "0": "A",
        "1": "B",
        "2": "C",
        "3": "D",
        "4": "E",
        "5": "F",
        "6": "G",
        "7": "H",
        "8": "I",
        "9": "J",
    }
    LETTER_TO_NUMBER: ClassVar[Dict[str, str]] = {v: k for k, v in NUMBER_TO_LETTER.items()}

    @classmethod
    def _validate(cls, value: str) -> str:
        clean = re.sub(r"[\s\-]", "", value.upper())
        if len(clean) != 7:
            raise VehiclePlateInvalidError(
                f"License plate must have 7 characters (received '{value}')",
                value=value,
            )

        if cls.MERCOSUL_REGEX.match(clean) or cls.TRADITIONAL_REGEX.match(clean):
            return clean

        raise VehiclePlateInvalidError(
            f"License plate '{value}' does not match traditional (ABC-1234) "
            f"or Mercosul (ABC1D23) format.",
            value=value,
        )

    @property
    def is_mercosul(self) -> bool:
        """Returns True if the plate follows the Mercosul format (e.g. ABC1D23)."""
        return bool(self.MERCOSUL_REGEX.match(str(self)))

    def to_mercosul(self) -> PlacaVeiculo:
        """Converts traditional plate to Mercosul pattern (e.g. ABC1234 -> ABC1C34)."""
        if self.is_mercosul:
            return self
        raw = str(self)
        fifth_char = self.NUMBER_TO_LETTER.get(raw[4], raw[4])
        return PlacaVeiculo(f"{raw[:4]}{fifth_char}{raw[5:]}")

    def to_antiga(self) -> PlacaVeiculo:
        """Converts Mercosul plate to traditional pattern (e.g. ABC1C34 -> ABC-1234)."""
        if not self.is_mercosul:
            return self
        raw = str(self)
        fifth_char = self.LETTER_TO_NUMBER.get(raw[4], raw[4])
        return PlacaVeiculo(f"{raw[:4]}{fifth_char}{raw[5:]}")

    @property
    def formatted(self) -> str:
        """Returns formatted plate: `ABC-1234` for traditional, `ABC1D23` for Mercosul."""
        raw = str(self)
        if self.is_mercosul:
            return raw
        return f"{raw[:3]}-{raw[3:]}"

    @property
    def masked(self) -> str:
        """Returns partially masked plate: `ABC-**34` or `ABC1**3`."""
        raw = str(self)
        if self.is_mercosul:
            return f"{raw[:4]}**{raw[-1]}"
        return f"{raw[:3]}-**{raw[-2:]}"

    @classmethod
    def openapi_schema_extra(cls) -> Dict[str, Any]:
        return {
            "type": "string",
            "title": "PlacaVeiculo",
            "description": (
                "Brazilian vehicle license plate (Traditional ABC-1234 or Mercosul ABC1D23)"
            ),
            "examples": ["ABC-1234", "ABC1D23"],
            "pattern": r"^[A-Z]{3}-?\d([A-Z]|\d)\d{2}$",
        }


class RENAVAM(BrazilianType):
    """Brazilian National Registry of Motor Vehicles (RENAVAM).

    Features:
    - 11-digit numerical code with official Modulo 11 check.
    - Handles legacy 9-digit numbers by prepending zeros.
    - `.formatted`: 11 digits string.
    - `.masked`: `****.******-1`.
    """

    WEIGHTS: ClassVar[List[int]] = [3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    @classmethod
    def _validate(cls, value: str) -> str:
        digits = cls._extract_digits(value)

        # Pad 9-digit legacy renavam to 11 digits
        if 8 <= len(digits) <= 11 and value.isdigit():
            digits = digits.zfill(11)

        if len(digits) != 11:
            raise RenavamInvalidError(
                f"RENAVAM must have 11 digits (received {len(digits)})",
                value=value,
            )

        if len(set(digits)) == 1:
            raise RenavamInvalidError(
                f"RENAVAM cannot be composed of identical repeated digits: '{value}'",
                value=value,
            )

        # Modulo 11 verification
        sum_val = sum(int(digits[i]) * cls.WEIGHTS[i] for i in range(10))
        rem = (sum_val * 10) % 11
        dv = 0 if rem in (10, 11) else rem

        if int(digits[10]) != dv:
            raise RenavamInvalidError(
                f"Invalid RENAVAM checksum (expected {dv}, got {digits[10]})",
                value=value,
            )

        return digits

    @property
    def formatted(self) -> str:
        """Returns standard punctuated RENAVAM string: `0000000000-0`."""
        d = self.digits
        return f"{d[:10]}-{d[10:]}"

    @property
    def masked(self) -> str:
        """Returns masked RENAVAM: `****.******-0`."""
        d = self.digits
        return f"****.******-{d[10:]}"

    @classmethod
    def openapi_schema_extra(cls) -> Dict[str, Any]:
        return {
            "type": "string",
            "title": "RENAVAM",
            "description": "Brazilian National Registry of Motor Vehicles code (RENAVAM)",
            "examples": ["00123456789"],
            "pattern": r"^\d{11}$",
        }


class CNH(BrazilianType):
    """Brazilian National Driver's License (Carteira Nacional de Habilitação - CNH).

    Features:
    - 11-digit code with dual Modulo 11 verification digits.
    - `.formatted`: 11 digits string.
    - `.masked`: `***.*****.**-0`.
    """

    @classmethod
    def _validate(cls, value: str) -> str:
        digits = cls._extract_digits(value)

        if 9 <= len(digits) <= 11 and value.isdigit():
            digits = digits.zfill(11)

        if len(digits) != 11:
            raise CNHInvalidError(
                f"CNH must have 11 digits (received {len(digits)})",
                value=value,
            )

        if len(set(digits)) == 1:
            raise CNHInvalidError(
                f"CNH cannot be composed of identical repeated digits: '{value}'",
                value=value,
            )

        # First verification digit
        s1 = sum(int(digits[i]) * (9 - i) for i in range(9))
        r1 = s1 % 11
        incr = 0
        if r1 >= 10:
            dv1 = 0
            incr = -2 if r1 == 10 else 0
        else:
            dv1 = r1

        if int(digits[9]) != dv1:
            raise CNHInvalidError(
                f"Invalid CNH check digit 1 (expected {dv1}, got {digits[9]})",
                value=value,
            )

        # Second verification digit
        s2 = sum(int(digits[i]) * (1 + i) for i in range(9))
        r2 = (s2 + incr) % 11
        if r2 >= 10:
            dv2 = 0
        else:
            dv2 = r2

        if int(digits[10]) != dv2:
            raise CNHInvalidError(
                f"Invalid CNH check digit 2 (expected {dv2}, got {digits[10]})",
                value=value,
            )

        return digits

    @property
    def formatted(self) -> str:
        """Returns standard punctuated CNH string."""
        return self.digits

    @property
    def masked(self) -> str:
        """Returns masked CNH string."""
        d = self.digits
        return f"***.*****.**-{d[-1]}"

    @classmethod
    def openapi_schema_extra(cls) -> Dict[str, Any]:
        return {
            "type": "string",
            "title": "CNH",
            "description": "Brazilian National Driver's License number (CNH)",
            "examples": ["12345678901"],
            "pattern": r"^\d{11}$",
        }
