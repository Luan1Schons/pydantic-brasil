"""CEP (Código de Endereçamento Postal) validation and formatting."""

from __future__ import annotations

import random
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.exceptions import CEPInvalidError


class CEP(BrazilianType):
    """Brazilian postal code (Código de Endereçamento Postal - CEP).

    Features:
    - Exactly 8 numerical digits.
    - Identification of Brazilian State (UF) based on official Correios numbering ranges.
    - `.formatted`: `01310-100`.
    - `.masked`: `01310-***`.
    - `.state`: Brazilian state abbreviation (e.g. 'SP', 'RJ', 'MG').
    - `CEP.generate(state='SP', formatted=True)`: Test data generator.
    """

    EXPECTED_DIGITS: ClassVar[Optional[int]] = 8

    # Official Correios Postal ranges: (min_5_digits, max_5_digits, UF)
    RANGES: ClassVar[List[Tuple[int, int, str]]] = [
        (1000, 19999, "SP"),
        (20000, 28999, "RJ"),
        (29000, 29999, "ES"),
        (30000, 39999, "MG"),
        (40000, 48999, "BA"),
        (49000, 49999, "SE"),
        (50000, 56999, "PE"),
        (57000, 57999, "AL"),
        (58000, 58999, "PB"),
        (59000, 59999, "RN"),
        (60000, 63999, "CE"),
        (64000, 64999, "PI"),
        (65000, 65999, "MA"),
        (66000, 68899, "PA"),
        (68900, 68999, "AP"),
        (69000, 69299, "AM"),
        (69300, 69399, "RR"),
        (69400, 69899, "AM"),
        (69900, 69999, "AC"),
        (70000, 72799, "DF"),
        (72800, 72999, "GO"),
        (73000, 73699, "DF"),
        (73700, 76799, "GO"),
        (76800, 76999, "RO"),
        (77000, 77999, "TO"),
        (78000, 78899, "MT"),
        (79000, 79999, "MS"),
        (80000, 87999, "PR"),
        (88000, 89999, "SC"),
        (90000, 99999, "RS"),
    ]

    @classmethod
    def _validate(cls, value: str) -> str:
        digits = cls._extract_digits(value)

        if len(digits) != 8:
            raise CEPInvalidError(
                f"CEP must have exactly 8 numerical digits (received {len(digits)})",
                value=value,
            )

        return value

    @property
    def formatted(self) -> str:
        """Returns standard punctuated CEP string: `00000-000`."""
        d = self.digits
        return f"{d[:5]}-{d[5:]}"

    @property
    def masked(self) -> str:
        """Returns partially masked CEP string: `00000-***`."""
        d = self.digits
        return f"{d[:5]}-***"

    @property
    def state(self) -> Optional[str]:
        """Returns the Brazilian state (UF) corresponding to this CEP prefix, if known."""
        prefix_5 = int(self.digits[:5])
        for min_val, max_val, uf in self.RANGES:
            if min_val <= prefix_5 <= max_val:
                return uf
        return None

    @classmethod
    def generate(cls, state: Optional[str] = None, formatted: bool = False) -> CEP:
        """Generates a valid CEP for testing purposes.

        Args:
            state: Optional state UF (e.g. 'SP', 'RJ'). If given, generates a CEP within that state.
            formatted: If True, returns formatted string; otherwise 8 digits.
        """
        if state is not None:
            uf = state.upper().strip()
            matching_ranges = [r for r in cls.RANGES if r[2] == uf]
            if not matching_ranges:
                raise ValueError(f"Unknown Brazilian state UF: {state}")
            chosen_range = random.choice(matching_ranges)
            prefix_5 = random.randint(chosen_range[0], chosen_range[1])
        else:
            chosen_range = random.choice(cls.RANGES)
            prefix_5 = random.randint(chosen_range[0], chosen_range[1])

        suffix_3 = random.randint(0, 999)
        raw = f"{prefix_5:05d}{suffix_3:03d}"
        instance = cls(raw)
        return cls(instance.formatted if formatted else raw)

    @classmethod
    def openapi_schema_extra(cls) -> Dict[str, Any]:
        return {
            "type": "string",
            "title": "CEP",
            "description": "Brazilian Postal Code (Código de Endereçamento Postal)",
            "examples": ["01310-100", "01310100"],
            "pattern": r"^\d{5}-?\d{3}$",
        }
