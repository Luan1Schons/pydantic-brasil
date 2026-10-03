"""Civil Registry Certificate (Certidão de Nascimento, Casamento, Óbito) validation."""

from __future__ import annotations

import random
from typing import ClassVar, Dict, Optional

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.exceptions import CertidaoCivilInvalidError


class CertidaoCivil(BrazilianType):
    """Brazilian Unified Civil Registry Certificate (Provimento CNJ nº 63/2017).

    Validates 32-digit standardized certificates for Birth, Marriage, and Death records.
    Format: AAAAAA.BB.CC.DDDD.E.FFFFF.GGG.HHHHHHH-II
    - AAAAAA: 6-digit Registry Office (CNS) code
    - BB: 2-digit Collection code (usually 01)
    - CC: 2-digit Book type (55=Birth, 66=Civil Marriage, 77=Religious Marriage, 88=Death)
    - DDDD: 4-digit registration year
    - E: 1-digit Book type code
    - FFFFF: 5-digit Book number
    - GGG: 3-digit Page number
    - HHHHHHH: 7-digit Term number
    - II: 2-digit Modulo 11 cyclical checksum
    """

    EXPECTED_DIGITS: ClassVar[Optional[int]] = 32
    DOC_NAME: ClassVar[str] = "Certidão Civil (CNJ)"

    TYPE_NAMES: ClassVar[Dict[str, str]] = {
        "55": "Nascimento",
        "66": "Casamento Civil",
        "77": "Casamento Religioso com Efeito Civil",
        "88": "Óbito",
        "99": "Natimorto / Proclamas",
    }

    @staticmethod
    def _cyclical_weighted_sum(digits: list[int]) -> int:
        total = 0
        multiplier = 32 - len(digits)
        for d in digits:
            total += d * multiplier
            multiplier += 1
            if multiplier > 10:
                multiplier = 0
        return total

    @classmethod
    def _calculate_check_digits(cls, base_digits: list[int]) -> str:
        s1 = cls._cyclical_weighted_sum(base_digits)
        dv1 = s1 % 11
        if dv1 > 9:
            dv1 = 1

        s2 = cls._cyclical_weighted_sum(base_digits + [dv1])
        dv2 = s2 % 11
        if dv2 > 9:
            dv2 = 1

        return f"{dv1}{dv2}"

    @classmethod
    def _validate(cls, value: str) -> str:
        digits = cls._extract_digits(value)

        if len(digits) != 32:
            raise CertidaoCivilInvalidError(
                f"Certidão Civil must have exactly 32 digits (received '{value}')",
                value=value,
            )

        if len(set(digits)) == 1:
            raise CertidaoCivilInvalidError(
                f"Certidão Civil cannot have all repeated digits: '{value}'",
                value=value,
            )

        base_digits = [int(d) for d in digits[:30]]
        expected_dv = cls._calculate_check_digits(base_digits)
        given_dv = digits[30:]

        if given_dv != expected_dv:
            raise CertidaoCivilInvalidError(
                f"Invalid check digits for Certidão Civil '{value}' "
                f"(expected '{expected_dv}', got '{given_dv}')",
                value=value,
            )

        return digits

    @property
    def cartorio_cns(self) -> str:
        """Returns the 6-digit Registry Office (CNS) code."""
        return self.digits[:6]

    @property
    def year(self) -> int:
        """Returns the 4-digit registration year."""
        return int(self.digits[10:14])

    @property
    def type_code(self) -> str:
        """Returns the 2-digit record type code (55, 66, 77, 88)."""
        return self.digits[8:10]

    @property
    def type_name(self) -> str:
        """Returns the human-readable record type (e.g. Nascimento, Casamento, Óbito)."""
        return self.TYPE_NAMES.get(self.type_code, "Outro")

    @property
    def formatted(self) -> str:
        """Returns standard formatted certificate number."""
        d = self.digits
        return (
            f"{d[:6]}.{d[6:8]}.{d[8:10]}.{d[10:14]}."
            f"{d[14]}.{d[15:20]}.{d[20:23]}.{d[23:30]}-{d[30:]}"
        )

    @property
    def masked(self) -> str:
        """Returns LGPD-safe masked certificate number."""
        d = self.digits
        return f"{d[:6]}.**.**.{d[10:14]}." f"*.*****.***.*******-{d[30:]}"

    @classmethod
    def generate(
        cls,
        record_type: str = "55",
        year: Optional[int] = None,
        formatted: bool = False,
    ) -> CertidaoCivil:
        """Generates a valid 32-digit civil registry certificate number."""
        yr = year or random.randint(1990, 2026)
        cns = f"{random.randint(100000, 999999):06d}"
        acervo = "01"
        tipo = record_type if record_type in cls.TYPE_NAMES else "55"
        livro_tipo = "1"
        livro = f"{random.randint(1, 99999):05d}"
        folha = f"{random.randint(1, 999):03d}"
        termo = f"{random.randint(1, 9999999):07d}"

        base_str = f"{cns}{acervo}{tipo}{yr:04d}{livro_tipo}{livro}{folha}{termo}"
        base_digits = [int(d) for d in base_str]
        dv = cls._calculate_check_digits(base_digits)

        raw = f"{base_str}{dv}"
        instance = cls(raw)
        if formatted:
            return cls(instance.formatted)
        return instance


Certidao = CertidaoCivil
