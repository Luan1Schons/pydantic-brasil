"""CNJ Judicial Process Number (Numeração Única CNJ) validation and formatting."""

from __future__ import annotations

import random
from typing import ClassVar, Dict, Optional

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.exceptions import ProcessoCNJInvalidError


class ProcessoCNJ(BrazilianType):
    """Brazilian CNJ Judicial Process Number (Numeração Única de Processos Judiciais).

    Established by Resolução CNJ nº 65/2008:
    Format: NNNNNNN-DD.AAAA.J.TR.OOOO (20 digits).
    - NNNNNNN: 7-digit sequential process number
    - DD: 2-digit verification checksum (Modulo 97 - ISO 7064)
    - AAAA: 4-digit filing year
    - J: 1-digit judicial segment (e.g. 8 for State Court, 4 for Federal Court)
    - TR: 2-digit tribunal / region identifier
    - OOOO: 4-digit court unit / origin identifier
    """

    EXPECTED_DIGITS: ClassVar[Optional[int]] = 20
    DOC_NAME: ClassVar[str] = "Processo Judicial CNJ"

    SEGMENT_NAMES: ClassVar[Dict[int, str]] = {
        1: "Supremo Tribunal Federal (STF)",
        2: "Conselho Nacional de Justiça (CNJ)",
        3: "Superior Tribunal de Justiça (STJ)",
        4: "Justiça Federal",
        5: "Justiça do Trabalho",
        6: "Justiça Eleitoral",
        7: "Justiça Militar da União",
        8: "Justiça dos Estados e do Distrito Federal",
        9: "Justiça Militar Estadual",
    }

    @classmethod
    def _validate(cls, value: str) -> str:
        digits = cls._extract_digits(value)

        if len(digits) != 20:
            raise ProcessoCNJInvalidError(
                f"Processo CNJ must have exactly 20 digits (received '{value}')",
                value=value,
            )

        seq = digits[:7]
        dv = digits[7:9]
        year = digits[9:13]
        j = digits[13]
        tr = digits[14:16]
        orig = digits[16:20]

        segment_num = int(j)
        if segment_num not in cls.SEGMENT_NAMES:
            raise ProcessoCNJInvalidError(
                f"Invalid judicial segment '{j}' in Processo CNJ '{value}'",
                value=value,
            )

        # Modulo 97 (ISO 7064) checksum validation
        # Formula: int(f"{seq}{year}{j}{tr}{orig}00") % 97
        num_without_dv = f"{seq}{year}{j}{tr}{orig}00"
        rem = int(num_without_dv) % 97
        expected_dv = 98 - rem
        expected_dv_str = f"{expected_dv:02d}"

        if dv != expected_dv_str:
            raise ProcessoCNJInvalidError(
                f"Invalid check digits in Processo CNJ '{value}' "
                f"(expected '{expected_dv_str}', got '{dv}')",
                value=value,
            )

        return digits

    @property
    def sequential(self) -> str:
        """Returns the 7-digit sequential process number."""
        return self.digits[:7]

    @property
    def check_digits(self) -> str:
        """Returns the 2 check digits (DD)."""
        return self.digits[7:9]

    @property
    def year(self) -> int:
        """Returns the 4-digit filing year (AAAA)."""
        return int(self.digits[9:13])

    @property
    def segment_id(self) -> int:
        """Returns the 1-digit judicial segment identifier (J)."""
        return int(self.digits[13])

    @property
    def segment_name(self) -> str:
        """Returns the descriptive name of the judicial segment."""
        return self.SEGMENT_NAMES.get(self.segment_id, "Desconhecido")

    @property
    def tribunal(self) -> str:
        """Returns the 2-digit tribunal / region identifier (TR)."""
        return self.digits[14:16]

    @property
    def origin(self) -> str:
        """Returns the 4-digit court origin identifier (OOOO)."""
        return self.digits[16:20]

    @property
    def formatted(self) -> str:
        """Returns standard formatted Processo CNJ (NNNNNNN-DD.AAAA.J.TR.OOOO)."""
        d = self.digits
        return f"{d[:7]}-{d[7:9]}.{d[9:13]}.{d[13]}.{d[14:16]}.{d[16:]}"

    @property
    def masked(self) -> str:
        """Returns LGPD-safe masked Processo CNJ (NNNNNNN-DD.AAAA.*.**.OOOO)."""
        d = self.digits
        return f"{d[:7]}-{d[7:9]}.{d[9:13]}.*.**.{d[16:]}"

    @classmethod
    def generate(
        cls,
        year: Optional[int] = None,
        segment: int = 8,
        tribunal: int = 26,
        origin: int = 100,
        formatted: bool = False,
    ) -> ProcessoCNJ:
        """Generates a valid Processo CNJ number for testing purposes."""
        yr = year or random.randint(2000, 2026)
        seq_num = random.randint(1, 9999999)
        seq_str = f"{seq_num:07d}"
        yr_str = f"{yr:04d}"
        seg_str = str(segment if segment in cls.SEGMENT_NAMES else 8)
        tr_str = f"{tribunal:02d}"
        orig_str = f"{origin:04d}"

        num_for_dv = f"{seq_str}{yr_str}{seg_str}{tr_str}{orig_str}00"
        dv = 98 - (int(num_for_dv) % 97)
        dv_str = f"{dv:02d}"

        raw = f"{seq_str}{dv_str}{yr_str}{seg_str}{tr_str}{orig_str}"
        instance = cls(raw)
        if formatted:
            return cls(instance.formatted)
        return instance


ProcessoJudicial = ProcessoCNJ
