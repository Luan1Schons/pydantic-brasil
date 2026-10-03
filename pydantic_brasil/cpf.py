"""CPF (Cadastro de Pessoas Físicas) validation and formatting."""

from __future__ import annotations

import random
from typing import Any, ClassVar, Dict, List, Optional, Union

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.exceptions import CPFInvalidError


class CPF(BrazilianType):
    """Brazilian individual taxpayer registry (Cadastro de Pessoas Físicas - CPF).

    Features:
    - Official Modulo 11 verification digits calculation.
    - Rejection of repeated sequential digits (e.g., 111.111.111-11).
    - `.formatted`: Formats with standard punctuation: `123.456.789-00`.
    - `.masked`: LGPD-compliant masking: `***.456.789-**`.
    - `.digits`: Pure 11 numerical digits string: `12345678900`.
    - `.fiscal_region`: Federal Revenue fiscal region (states) of issuance based on 9th digit.
    - `CPF.generate(state='SP', formatted=True)`: Test data generator.
    """

    EXPECTED_DIGITS: ClassVar[Optional[int]] = 11

    FISCAL_REGIONS: ClassVar[Dict[int, List[str]]] = {
        0: ["RS"],
        1: ["DF", "GO", "MT", "MS", "TO"],
        2: ["AC", "AM", "AP", "PA", "RO", "RR"],
        3: ["CE", "MA", "PI"],
        4: ["AL", "PB", "PE", "RN"],
        5: ["BA", "SE"],
        6: ["MG"],
        7: ["ES", "RJ"],
        8: ["SP"],
        9: ["PR", "SC"],
    }

    STATE_TO_DIGIT: ClassVar[Dict[str, int]] = {
        uf: digit for digit, ufs in FISCAL_REGIONS.items() for uf in ufs
    }

    @classmethod
    def _validate(cls, value: str) -> str:
        digits = cls._extract_digits(value)

        if len(digits) != 11:
            raise CPFInvalidError(
                f"CPF must have exactly 11 numerical digits (received {len(digits)})",
                value=value,
            )

        # Disallow sequences of repeated digits
        if len(set(digits)) == 1:
            raise CPFInvalidError(
                f"CPF cannot be composed of identical repeated digits: '{value}'",
                value=value,
            )

        # Verify first check digit
        s1 = sum(int(digits[i]) * (10 - i) for i in range(9))
        d1 = 11 - (s1 % 11)
        dv1 = 0 if d1 >= 10 else d1
        if int(digits[9]) != dv1:
            raise CPFInvalidError(
                f"Invalid CPF checksum digit 1 (expected {dv1}, got {digits[9]})",
                value=value,
            )

        # Verify second check digit
        s2 = sum(int(digits[i]) * (11 - i) for i in range(10))
        d2 = 11 - (s2 % 11)
        dv2 = 0 if d2 >= 10 else d2
        if int(digits[10]) != dv2:
            raise CPFInvalidError(
                f"Invalid CPF checksum digit 2 (expected {dv2}, got {digits[10]})",
                value=value,
            )

        return value

    @property
    def formatted(self) -> str:
        """Returns standard punctuated CPF string: `000.000.000-00`."""
        d = self.digits
        return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"

    @property
    def masked(self) -> str:
        """Returns LGPD-safe masked CPF string: `***.000.000-**`."""
        d = self.digits
        return f"***.{d[3:6]}.{d[6:9]}-**"

    @property
    def fiscal_region(self) -> List[str]:
        """Returns the list of Brazilian states (UFs) corresponding to the 9th digit."""
        digit = int(self.digits[8])
        return self.FISCAL_REGIONS[digit]

    @classmethod
    def generate(cls, state: Optional[Union[str, int]] = None, formatted: bool = False) -> CPF:
        """Generates a valid CPF for testing purposes.

        Args:
            state: Optional state abbreviation (e.g. 'SP', 'RJ') or 9th digit (0-9).
            formatted: If True, returns punctuated string; otherwise 11 digits.
        """
        digits = [random.randint(0, 9) for _ in range(8)]

        if state is not None:
            if isinstance(state, str):
                uf = state.upper().strip()
                if uf not in cls.STATE_TO_DIGIT:
                    raise ValueError(f"Unknown Brazilian state UF: {state}")
                digits.append(cls.STATE_TO_DIGIT[uf])
            elif isinstance(state, int):
                if not (0 <= state <= 9):
                    raise ValueError("State digit must be between 0 and 9")
                digits.append(state)
        else:
            digits.append(random.randint(0, 9))

        # First check digit
        s1 = sum(digits[i] * (10 - i) for i in range(9))
        d1 = 11 - (s1 % 11)
        dv1 = 0 if d1 >= 10 else d1
        digits.append(dv1)

        # Second check digit
        s2 = sum(digits[i] * (11 - i) for i in range(10))
        d2 = 11 - (s2 % 11)
        dv2 = 0 if d2 >= 10 else d2
        digits.append(dv2)

        raw = "".join(str(d) for d in digits)
        instance = cls(raw)
        return cls(instance.formatted if formatted else raw)

    @classmethod
    def openapi_schema_extra(cls) -> Dict[str, Any]:
        return {
            "type": "string",
            "title": "CPF",
            "description": "Brazilian individual taxpayer registry (CPF) with checksum validation",
            "examples": ["123.456.789-00", "12345678900"],
            "pattern": r"^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$",
        }
