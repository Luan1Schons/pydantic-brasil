"""CNPJ (Cadastro Nacional da Pessoa Jurídica) validation and formatting."""

from __future__ import annotations

import random
import re
from typing import Any, ClassVar, Dict, List, Optional

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.exceptions import CNPJInvalidError


class CNPJ(BrazilianType):
    """Brazilian legal entity registry (Cadastro Nacional da Pessoa Jurídica - CNPJ).

    Features:
    - Official Modulo 11 verification digits calculation.
    - Full support for both traditional numerical format and the
      Receita Federal 2026 alphanumeric format.
    - Rejection of identical repeated sequences.
    - `.formatted`: `12.345.678/0001-90`.
    - `.masked`: `12.***.***/0001-90`.
    - `.is_matriz` / `.is_filial`: Identifies headquarters vs branch office.
    - `.branch_number`: The 4-character branch identifier.
    - `CNPJ.generate(formatted=True, branch=1)`: Test data generator.
    """

    EXPECTED_DIGITS: ClassVar[Optional[int]] = 14
    WEIGHTS_DV1: ClassVar[List[int]] = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    WEIGHTS_DV2: ClassVar[List[int]] = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    @classmethod
    def _char_value(cls, char: str) -> int:
        """Converts character to numeric value according to Receita Federal standard.

        Digits '0'-'9' have values 0-9.
        Letters 'A'-'Z' have values ord(char) - 48 (e.g. 'A' = 17, 'B' = 18).
        """
        c = char.upper()
        if c.isdigit():
            return int(c)
        if "A" <= c <= "Z":
            return ord(c) - 48
        raise CNPJInvalidError(f"Invalid character in CNPJ: '{char}'")

    @classmethod
    def _validate(cls, value: str) -> str:
        # Strip common formatting punctuation: '.', '/', '-'
        cleaned = re.sub(r"[\.\/\-\s]", "", value.upper())

        if len(cleaned) != 14:
            raise CNPJInvalidError(
                f"CNPJ must have exactly 14 characters (received {len(cleaned)})",
                value=value,
            )

        # Check for disallowed repeated sequences if purely numeric
        if cleaned.isdigit() and len(set(cleaned)) == 1:
            raise CNPJInvalidError(
                f"CNPJ cannot be composed of identical repeated digits: '{value}'",
                value=value,
            )

        # Last 2 characters must always be digits
        if not (cleaned[12].isdigit() and cleaned[13].isdigit()):
            raise CNPJInvalidError(
                f"The verification digits of a CNPJ must be numeric: '{cleaned[12:]}'",
                value=value,
            )

        # Calculate 1st Check Digit
        s1 = sum(cls._char_value(cleaned[i]) * cls.WEIGHTS_DV1[i] for i in range(12))
        r1 = s1 % 11
        dv1 = 0 if r1 < 2 else 11 - r1
        if int(cleaned[12]) != dv1:
            raise CNPJInvalidError(
                f"Invalid CNPJ checksum digit 1 (expected {dv1}, got {cleaned[12]})",
                value=value,
            )

        # Calculate 2nd Check Digit
        s2 = sum(cls._char_value(cleaned[i]) * cls.WEIGHTS_DV2[i] for i in range(13))
        r2 = s2 % 11
        dv2 = 0 if r2 < 2 else 11 - r2
        if int(cleaned[13]) != dv2:
            raise CNPJInvalidError(
                f"Invalid CNPJ checksum digit 2 (expected {dv2}, got {cleaned[13]})",
                value=value,
            )

        return value

    @property
    def formatted(self) -> str:
        """Returns standard punctuated CNPJ string: `00.000.000/0000-00`."""
        d = str(self)
        return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}"

    @property
    def masked(self) -> str:
        """Returns masked CNPJ string preserving root and branch: `00.***.***/0000-00`."""
        d = str(self)
        return f"{d[:2]}.***.***/{d[8:12]}-{d[12:]}"

    @property
    def is_matriz(self) -> bool:
        """Returns True if this is the headquarters (matriz), typically branch 0001."""
        return self.branch_number == "0001"

    @property
    def is_filial(self) -> bool:
        """Returns True if this is a branch office (filial)."""
        return not self.is_matriz

    @property
    def branch_number(self) -> str:
        """Returns the 4-character branch identifier (characters 9 to 12)."""
        return str(self)[8:12]

    @property
    def is_alphanumeric(self) -> bool:
        """Returns True if this CNPJ contains letters under the new 2026 format."""
        return any(c.isalpha() for c in str(self)[:12])

    @classmethod
    def generate(cls, formatted: bool = False, branch: int = 1) -> CNPJ:
        """Generates a valid traditional CNPJ for testing purposes.

        Args:
            formatted: If True, returns punctuated string; otherwise 14 characters.
            branch: Branch number (default 1 for headquarters '0001').
        """
        root = [random.randint(0, 9) for _ in range(8)]
        branch_str = str(branch).zfill(4)
        chars = [int(c) for c in ("".join(str(d) for d in root) + branch_str)]

        # 1st DV
        s1 = sum(chars[i] * cls.WEIGHTS_DV1[i] for i in range(12))
        r1 = s1 % 11
        dv1 = 0 if r1 < 2 else 11 - r1
        chars.append(dv1)

        # 2nd DV
        s2 = sum(chars[i] * cls.WEIGHTS_DV2[i] for i in range(13))
        r2 = s2 % 11
        dv2 = 0 if r2 < 2 else 11 - r2
        chars.append(dv2)

        raw = "".join(str(c) for c in chars)
        instance = cls(raw)
        return cls(instance.formatted if formatted else raw)

    @classmethod
    def openapi_schema_extra(cls) -> Dict[str, Any]:
        return {
            "type": "string",
            "title": "CNPJ",
            "description": "Brazilian legal entity registry (CNPJ) with checksum validation",
            "examples": ["12.345.678/0001-90", "12345678000190"],
            "pattern": r"^[A-Z0-9]{2}\.?[A-Z0-9]{3}\.?[A-Z0-9]{3}\/?[A-Z0-9]{4}-?\d{2}$",
        }
