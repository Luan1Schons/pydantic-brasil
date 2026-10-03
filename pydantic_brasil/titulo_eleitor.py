"""Validação e formatação de Título de Eleitor."""

from __future__ import annotations

import random
from typing import ClassVar, Dict, Optional

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.exceptions import TituloEleitorInvalidError


class TituloEleitor(BrazilianType):
    """Título de Eleitor brasileiro.

    Validação em conformidade com as normas do Tribunal Superior Eleitoral (TSE):
    - 12 dígitos: 8 sequenciais, 2 da UF (01 a 28) e 2 verificadores (DV1, DV2).
    """

    EXPECTED_DIGITS: ClassVar[Optional[int]] = 12
    DOC_NAME: ClassVar[str] = "Título de Eleitor"

    UF_CODE_TO_STATE: ClassVar[Dict[int, str]] = {
        1: "SP",
        2: "MG",
        3: "RJ",
        4: "RS",
        5: "BA",
        6: "PR",
        7: "CE",
        8: "PE",
        9: "SC",
        10: "GO",
        11: "MA",
        12: "PB",
        13: "PA",
        14: "ES",
        15: "PI",
        16: "RN",
        17: "AL",
        18: "MT",
        19: "MS",
        20: "DF",
        21: "SE",
        22: "AM",
        23: "RO",
        24: "AC",
        25: "AP",
        26: "RR",
        27: "TO",
        28: "ZZ",  # Exterior
    }

    STATE_TO_UF_CODE: ClassVar[Dict[str, int]] = {
        state: code for code, state in UF_CODE_TO_STATE.items()
    }

    @classmethod
    def _validate(cls, value: str) -> str:
        digits = cls._extract_digits(value)

        if len(digits) != 12:
            raise TituloEleitorInvalidError(
                f"Título de Eleitor deve conter exatamente 12 dígitos (recebido '{value}')",
                value=value,
            )

        uf_code = int(digits[8:10])
        if uf_code not in cls.UF_CODE_TO_STATE:
            raise TituloEleitorInvalidError(
                f"Código de UF '{digits[8:10]}' inválido para o Título de Eleitor '{value}'",
                value=value,
            )

        # Cálculo do DV1
        seq_digits = [int(d) for d in digits[:8]]
        w1 = list(range(2, 10))
        total1 = sum(d * w for d, w in zip(seq_digits, w1))
        rem1 = total1 % 11
        if rem1 == 10:
            expected_dv1 = [0]
        elif rem1 == 0:
            expected_dv1 = [0, 1] if uf_code in (1, 2) else [0]
        else:
            expected_dv1 = [rem1]

        given_dv1 = int(digits[10])
        if given_dv1 not in expected_dv1:
            raise TituloEleitorInvalidError(
                f"Primeiro dígito verificador inválido para o Título de Eleitor '{value}'",
                value=value,
            )

        # Cálculo do DV2
        uf_and_dv1 = [int(digits[8]), int(digits[9]), given_dv1]
        w2 = [7, 8, 9]
        total2 = sum(d * w for d, w in zip(uf_and_dv1, w2))
        rem2 = total2 % 11
        if rem2 == 10:
            expected_dv2 = [0]
        elif rem2 == 0:
            expected_dv2 = [0, 1] if uf_code in (1, 2) else [0]
        else:
            expected_dv2 = [rem2]

        given_dv2 = int(digits[11])
        if given_dv2 not in expected_dv2:
            raise TituloEleitorInvalidError(
                f"Segundo dígito verificador inválido para o Título de Eleitor '{value}'",
                value=value,
            )

        return digits

    @property
    def state(self) -> str:
        """Retorna a sigla da UF onde o Título de Eleitor foi emitido."""
        uf_code = int(self.digits[8:10])
        return self.UF_CODE_TO_STATE.get(uf_code, "UNKNOWN")

    @property
    def uf_code(self) -> str:
        """Retorna os 2 dígitos do código da UF (ex: '01' para SP)."""
        return self.digits[8:10]

    @property
    def formatted(self) -> str:
        """Retorna o Título de Eleitor formatado: `XXXX XXXX XXXX`."""
        d = self.digits
        return f"{d[:4]} {d[4:8]} {d[8:]}"

    @property
    def masked(self) -> str:
        """Retorna o Título de Eleitor mascarado conforme a LGPD: `XXXX **** **XX`."""
        d = self.digits
        return f"{d[:4]} **** **{d[10:]}"

    @classmethod
    def generate(cls, state: Optional[str] = None, formatted: bool = False) -> TituloEleitor:
        """Gera um Título de Eleitor válido para testes."""
        if state:
            uf_code = cls.STATE_TO_UF_CODE.get(state.upper().strip(), 1)
        else:
            uf_code = random.choice(list(cls.UF_CODE_TO_STATE.keys()))

        seq = [random.randint(0, 9) for _ in range(8)]
        w1 = list(range(2, 10))
        rem1 = sum(d * w for d, w in zip(seq, w1)) % 11
        dv1 = 0 if rem1 == 10 else rem1

        uf_digits = [uf_code // 10, uf_code % 10]
        w2 = [7, 8, 9]
        rem2 = sum(d * w for d, w in zip(uf_digits + [dv1], w2)) % 11
        dv2 = 0 if rem2 == 10 else rem2

        raw = "".join(str(d) for d in seq) + f"{uf_code:02d}" + str(dv1) + str(dv2)
        instance = cls(raw)
        if formatted:
            return cls(instance.formatted)
        return instance


TituloEleitoral = TituloEleitor
