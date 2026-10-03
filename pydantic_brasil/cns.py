"""Validação e formatação de Cartão Nacional de Saúde (CNS / SUS)."""

from __future__ import annotations

import random
from typing import ClassVar, Optional

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.exceptions import CNSInvalidError


class CNS(BrazilianType):
    """Cartão Nacional de Saúde (CNS / SUS).

    Validação em conformidade com as normas do DATASUS e Ministério da Saúde:
    - 15 dígitos iniciados com 1, 2, 7, 8 ou 9.
    - Números definitivos (iniciados com 1 ou 2) utilizam base de 11 dígitos com Módulo 11.
    - Números provisórios (iniciados com 7, 8 ou 9) utilizam validação ponderada
      sobre os 15 dígitos.
    """

    EXPECTED_DIGITS: ClassVar[Optional[int]] = 15
    DOC_NAME: ClassVar[str] = "Cartão Nacional de Saúde (CNS)"

    @classmethod
    def _validate(cls, value: str) -> str:
        digits = cls._extract_digits(value)

        if len(digits) != 15:
            raise CNSInvalidError(
                f"CNS deve conter exatamente 15 dígitos numéricos (recebido '{value}')",
                value=value,
            )

        first_digit = digits[0]
        if first_digit not in ("1", "2", "7", "8", "9"):
            raise CNSInvalidError(
                f"CNS deve iniciar com 1, 2, 7, 8 ou 9 (recebido '{value}')",
                value=value,
            )

        if first_digit in ("1", "2"):
            # CNS definitivo
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
                    f"Dígito verificador inválido para o CNS definitivo '{value}'",
                    value=value,
                )
        else:
            # CNS provisório (iniciado com 7, 8 ou 9)
            total = sum(int(digits[i]) * (15 - i) for i in range(15))
            if total % 11 != 0:
                raise CNSInvalidError(
                    f"Validação inválida para o CNS provisório '{value}'",
                    value=value,
                )

        return digits

    @property
    def is_definitivo(self) -> bool:
        """Retorna True se for um CNS definitivo (iniciado com 1 ou 2)."""
        return self.digits[0] in ("1", "2")

    @property
    def is_provisorio(self) -> bool:
        """Retorna True se for um CNS provisório (iniciado com 7, 8 ou 9)."""
        return self.digits[0] in ("7", "8", "9")

    @property
    def formatted(self) -> str:
        """Retorna o CNS formatado: `XXX XXXX XXXX XXXX`."""
        d = self.digits
        return f"{d[:3]} {d[3:7]} {d[7:11]} {d[11:]}"

    @property
    def masked(self) -> str:
        """Retorna o CNS mascarado para conformidade com a LGPD: `XXX **** **** XXXX`."""
        d = self.digits
        return f"{d[:3]} **** **** {d[11:]}"

    @classmethod
    def generate(cls, definitivo: bool = True, formatted: bool = False) -> CNS:
        """Gera um CNS válido para testes."""
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
                last_digit = (11 - (s % 11)) % 11
                if last_digit < 10:
                    raw = "".join(str(d) for d in candidate) + str(last_digit)
                    break

        instance = cls(raw)
        if formatted:
            return cls(instance.formatted)
        return instance


CartaoSUS = CNS
