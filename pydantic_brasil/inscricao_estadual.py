"""Inscrição Estadual (IE) validation for Brazilian States (UFs)."""

from __future__ import annotations

from typing import Any, Callable, ClassVar, Dict, Optional, cast

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.exceptions import StateRegistrationInvalidError


def _validate_sp(digits: str) -> bool:
    """Validates São Paulo (SP) Inscrição Estadual (12 digits or 'P' prefix for rural)."""
    if digits.startswith("P"):
        # Rural producer: P followed by 8 digits + 1 check digit
        body = digits[1:9]
        if len(body) != 8:
            return False
        weights = [1, 3, 4, 5, 6, 7, 8, 10]
        s = sum(int(body[i]) * weights[i] for i in range(8))
        dv = s % 11
        dv = dv % 10
        return str(dv) == digits[9]

    if len(digits) != 12:
        return False

    # 1st DV (position 9)
    w1 = [1, 3, 4, 5, 6, 7, 8, 10]
    s1 = sum(int(digits[i]) * w1[i] for i in range(8))
    dv1 = (s1 % 11) % 10
    if int(digits[8]) != dv1:
        return False

    # 2nd DV (position 12)
    w2 = [3, 2, 10, 9, 8, 7, 6, 5, 4, 3, 2]
    s2 = sum(int(digits[i]) * w2[i] for i in range(11))
    dv2 = (s2 % 11) % 10
    return int(digits[11]) == dv2


def _validate_rj(digits: str) -> bool:
    """Validates Rio de Janeiro (RJ) Inscrição Estadual (8 digits)."""
    if len(digits) != 8:
        return False
    weights = [2, 7, 6, 5, 4, 3, 2]
    s = sum(int(digits[i]) * weights[i] for i in range(7))
    r = s % 11
    dv = 0 if r <= 1 else 11 - r
    return int(digits[7]) == dv


def _validate_mg(digits: str) -> bool:
    """Validates Minas Gerais (MG) Inscrição Estadual (13 digits)."""
    if len(digits) != 13:
        return False

    # MG 1st DV
    body = digits[:3] + "0" + digits[3:11]
    w1 = [1, 2] * 6
    terms = []
    for i in range(12):
        prod = int(body[i]) * w1[i]
        terms.extend([int(c) for c in str(prod)])
    s1 = sum(terms)
    next_ten = ((s1 // 10) + 1) * 10 if s1 % 10 != 0 else s1
    dv1 = next_ten - s1
    if int(digits[11]) != dv1:
        return False

    # MG 2nd DV
    w2 = [3, 2, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
    s2 = sum(int(digits[i]) * w2[i] for i in range(12))
    r2 = s2 % 11
    dv2 = 0 if r2 in (0, 1) else 11 - r2
    return int(digits[12]) == dv2


def _validate_rs(digits: str) -> bool:
    """Validates Rio Grande do Sul (RS) Inscrição Estadual (10 digits)."""
    if len(digits) != 10:
        return False
    weights = [2, 9, 8, 7, 6, 5, 4, 3, 2]
    s = sum(int(digits[i]) * weights[i] for i in range(9))
    r = s % 11
    dv = 0 if r in (0, 1) else 11 - r
    return int(digits[9]) == dv


def _validate_pr(digits: str) -> bool:
    """Validates Paraná (PR) Inscrição Estadual (10 digits)."""
    if len(digits) != 10:
        return False
    w1 = [3, 2, 7, 6, 5, 4, 3, 2]
    s1 = sum(int(digits[i]) * w1[i] for i in range(8))
    r1 = s1 % 11
    dv1 = 0 if r1 in (0, 1) else 11 - r1
    if int(digits[8]) != dv1:
        return False

    w2 = [4, 3, 2, 7, 6, 5, 4, 3, 2]
    s2 = sum(int(digits[i]) * w2[i] for i in range(9))
    r2 = s2 % 11
    dv2 = 0 if r2 in (0, 1) else 11 - r2
    return int(digits[9]) == dv2


def _validate_sc(digits: str) -> bool:
    """Validates Santa Catarina (SC) Inscrição Estadual (9 digits)."""
    if len(digits) != 9:
        return False
    weights = [9, 8, 7, 6, 5, 4, 3, 2]
    s = sum(int(digits[i]) * weights[i] for i in range(8))
    r = s % 11
    dv = 0 if r in (0, 1) else 11 - r
    return int(digits[8]) == dv


def _validate_generic(digits: str) -> bool:
    """Fallback validator for other UFs: ensures minimum 8 to 14 numeric digits."""
    return 8 <= len(digits) <= 14 and digits.isdigit()


class InscricaoEstadual(BrazilianType):
    """Brazilian State Tax Registration (Inscrição Estadual - IE).

    Features:
    - Official checksum and pattern validation for Brazilian states (SP, RJ, MG, RS, PR, SC, etc.).
    - Supports 'ISENTO' for exempt businesses.
    - `.uf`: Optional state specified.
    - `.formatted`: Numeric digits or 'ISENTO'.
    """

    STATE_VALIDATORS: ClassVar[Dict[str, Callable[[str], bool]]] = {
        "SP": _validate_sp,
        "RJ": _validate_rj,
        "MG": _validate_mg,
        "RS": _validate_rs,
        "PR": _validate_pr,
        "SC": _validate_sc,
    }

    _uf: Optional[str] = None

    def __new__(cls, value: Any, uf: Optional[str] = None) -> InscricaoEstadual:
        cleaned = cls._clean_input(value)
        upper_val = cleaned.upper()

        if upper_val == "ISENTO":
            instance = cast(InscricaoEstadual, super().__new__(cls, "ISENTO"))
            instance._uf = uf.upper() if uf else None
            instance._digits = ""
            return instance

        raw_digits = cls._extract_digits(upper_val)
        if upper_val.startswith("P") and (uf == "SP" or uf is None):
            raw_digits = "P" + cls._extract_digits(upper_val)

        if uf:
            uf_upper = uf.upper().strip()
            validator = cls.STATE_VALIDATORS.get(uf_upper, _validate_generic)
            if not validator(raw_digits):
                raise StateRegistrationInvalidError(
                    f"Invalid Inscrição Estadual for state '{uf_upper}': '{value}'",
                    value=value,
                )
        else:
            # If no UF provided, ensure reasonable IE digit length
            if not (8 <= len(raw_digits) <= 14):
                raise StateRegistrationInvalidError(
                    f"Inscrição Estadual must have between 8 and 14 digits (received '{value}')",
                    value=value,
                )

        instance = cast(InscricaoEstadual, super().__new__(cls, raw_digits))
        instance._uf = uf.upper() if uf else None
        instance._digits = cls._extract_digits(raw_digits)
        return instance

    @classmethod
    def _validate(cls, value: str) -> str:
        upper = value.upper().strip()
        if upper == "ISENTO":
            return "ISENTO"
        digits = cls._extract_digits(upper)
        if not (8 <= len(digits) <= 14):
            raise StateRegistrationInvalidError(
                f"Invalid Inscrição Estadual: '{value}'",
                value=value,
            )
        return digits

    @property
    def is_isento(self) -> bool:
        """Returns True if the taxpayer is exempt from state registration."""
        return str(self) == "ISENTO"

    @property
    def uf(self) -> Optional[str]:
        """Returns the Brazilian state (UF) this registration was validated against, if set."""
        return getattr(self, "_uf", None)

    @property
    def formatted(self) -> str:
        """Returns registration digits or 'ISENTO'."""
        return str(self)

    @property
    def masked(self) -> str:
        """Returns masked registration string."""
        if self.is_isento:
            return "ISENTO"
        d = self.digits
        if len(d) > 4:
            return f"***.{d[3:-2]}.**-{d[-2:]}"
        return d

    @classmethod
    def openapi_schema_extra(cls) -> Dict[str, Any]:
        return {
            "type": "string",
            "title": "InscricaoEstadual",
            "description": "Brazilian State Tax Registration (Inscrição Estadual or ISENTO)",
            "examples": ["110.042.490.114", "ISENTO"],
        }
