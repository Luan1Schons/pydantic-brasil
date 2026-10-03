"""Validação de Inscrição Estadual (IE) para unidades federativas brasileiras."""

from __future__ import annotations

from typing import Any, Callable, ClassVar, Dict, Optional, cast

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.exceptions import StateRegistrationInvalidError


def _validate_sp(digits: str) -> bool:
    """Valida Inscrição Estadual de SP (12 dígitos ou prefixo 'P' para produtor rural)."""
    if digits.startswith("P"):
        # Produtor rural: P seguido de 8 dígitos + 1 dígito verificador
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

    # 1º DV (posição 9)
    w1 = [1, 3, 4, 5, 6, 7, 8, 10]
    s1 = sum(int(digits[i]) * w1[i] for i in range(8))
    dv1 = (s1 % 11) % 10
    if int(digits[8]) != dv1:
        return False

    # 2º DV (posição 12)
    w2 = [3, 2, 10, 9, 8, 7, 6, 5, 4, 3, 2]
    s2 = sum(int(digits[i]) * w2[i] for i in range(11))
    dv2 = (s2 % 11) % 10
    return int(digits[11]) == dv2


def _validate_rj(digits: str) -> bool:
    """Valida Inscrição Estadual do Rio de Janeiro (RJ) (8 dígitos)."""
    if len(digits) != 8:
        return False
    weights = [2, 7, 6, 5, 4, 3, 2]
    s = sum(int(digits[i]) * weights[i] for i in range(7))
    r = s % 11
    dv = 0 if r <= 1 else 11 - r
    return int(digits[7]) == dv


def _validate_mg(digits: str) -> bool:
    """Valida Inscrição Estadual de Minas Gerais (MG) (13 dígitos)."""
    if len(digits) != 13:
        return False

    # MG 1º DV
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

    # MG 2º DV
    w2 = [3, 2, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
    s2 = sum(int(digits[i]) * w2[i] for i in range(12))
    r2 = s2 % 11
    dv2 = 0 if r2 in (0, 1) else 11 - r2
    return int(digits[12]) == dv2


def _validate_rs(digits: str) -> bool:
    """Valida Inscrição Estadual do Rio Grande do Sul (RS) (10 dígitos)."""
    if len(digits) != 10:
        return False
    weights = [2, 9, 8, 7, 6, 5, 4, 3, 2]
    s = sum(int(digits[i]) * weights[i] for i in range(9))
    r = s % 11
    dv = 0 if r in (0, 1) else 11 - r
    return int(digits[9]) == dv


def _validate_pr(digits: str) -> bool:
    """Valida Inscrição Estadual do Paraná (PR) (10 dígitos)."""
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
    """Valida Inscrição Estadual de Santa Catarina (SC) (9 dígitos)."""
    if len(digits) != 9:
        return False
    weights = [9, 8, 7, 6, 5, 4, 3, 2]
    s = sum(int(digits[i]) * weights[i] for i in range(8))
    r = s % 11
    dv = 0 if r in (0, 1) else 11 - r
    return int(digits[8]) == dv


def _validate_generic(digits: str) -> bool:
    """Validador padrão para outras UFs: assegura entre 8 e 14 dígitos numéricos."""
    return 8 <= len(digits) <= 14 and digits.isdigit()


class InscricaoEstadual(BrazilianType):
    """Inscrição Estadual (IE).

    Recursos:
    - Validação de dígitos verificadores e formatos por UF (SP, RJ, MG, RS, PR, SC, etc.).
    - Suporte a 'ISENTO' para contribuintes desobrigados.
    - Suporte a produtores rurais de São Paulo com prefixo 'P'.
    - `.uf`: UF validada opcionalmente.
    - `.formatted`: Dígitos ou 'ISENTO'.
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
                    f"Inscrição Estadual inválida para a UF '{uf_upper}': '{value}'",
                    value=value,
                )
        else:
            # Se nenhuma UF for especificada, valida comprimento geral
            if not (8 <= len(raw_digits) <= 14):
                raise StateRegistrationInvalidError(
                    f"Inscrição Estadual deve ter entre 8 e 14 dígitos (recebido '{value}')",
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
                f"Inscrição Estadual inválida: '{value}'",
                value=value,
            )
        return digits

    @property
    def is_isento(self) -> bool:
        """Retorna True se for ISENTO de Inscrição Estadual."""
        return str(self) == "ISENTO"

    @property
    def uf(self) -> Optional[str]:
        """Retorna a UF utilizada na validação, se fornecida."""
        return getattr(self, "_uf", None)

    @property
    def formatted(self) -> str:
        """Retorna os dígitos ou 'ISENTO'."""
        return str(self)

    @property
    def masked(self) -> str:
        """Retorna a inscrição mascarada."""
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
            "description": "Inscrição Estadual (IE) ou ISENTO",
            "examples": ["110.042.490.114", "ISENTO"],
        }
