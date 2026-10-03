"""Validação e formatação de PIS, PASEP, NIS e NIT."""

from __future__ import annotations

import random
from typing import ClassVar, Optional

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.exceptions import PISInvalidError


class PIS(BrazilianType):
    """Identificador do trabalhador brasileiro (PIS / PASEP / NIS / NIT).

    O PIS (Programa de Integração Social) e o PASEP compartilham a mesma
    estrutura de 11 dígitos numéricos e validação oficial por Módulo 11.
    """

    EXPECTED_DIGITS: ClassVar[Optional[int]] = 11
    DOC_NAME: ClassVar[str] = "PIS/PASEP"
    MULTIPLIERS: ClassVar[list[int]] = [3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    @classmethod
    def _validate(cls, value: str) -> str:
        digits = cls._extract_digits(value)

        if len(digits) != 11:
            raise PISInvalidError(
                f"PIS deve conter exatamente 11 dígitos numéricos (recebido '{value}')",
                value=value,
            )

        if len(set(digits)) == 1:
            raise PISInvalidError(
                f"PIS não pode conter todos os dígitos iguais: '{value}'",
                value=value,
            )

        total = sum(int(digits[i]) * cls.MULTIPLIERS[i] for i in range(10))
        rem = total % 11
        expected_dv = 0 if rem < 2 else 11 - rem

        if int(digits[10]) != expected_dv:
            raise PISInvalidError(
                f"Dígito verificador inválido para o PIS '{value}'",
                value=value,
            )

        return digits

    @property
    def formatted(self) -> str:
        """Retorna o PIS formatado: `XXX.XXXXX.XX-X`."""
        d = self.digits
        return f"{d[:3]}.{d[3:8]}.{d[8:10]}-{d[10]}"

    @property
    def masked(self) -> str:
        """Retorna o PIS mascarado para conformidade com a LGPD: `XXX.*****.**-X`."""
        d = self.digits
        return f"{d[:3]}.*****.**-{d[10]}"

    @classmethod
    def generate(cls, formatted: bool = False) -> PIS:
        """Gera um PIS válido para testes."""
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


# Aliases comuns no domínio corporativo brasileiro
PASEP = PIS
NIS = PIS
NIT = PIS
