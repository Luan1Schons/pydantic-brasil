"""Validação e formatação de CEP (Código de Endereçamento Postal)."""

from __future__ import annotations

import random
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.exceptions import CEPInvalidError


class CEP(BrazilianType):
    """Código de Endereçamento Postal (CEP).

    Recursos:
    - Validação de 8 dígitos numéricos.
    - Inferência automática da UF (estado) a partir da faixa postal dos Correios.
    - `.formatted`: `01310-100`.
    - `.masked`: `01310-***`.
    - `.state`: Sigla da UF do estado (ex: 'SP', 'RJ', 'MG').
    - `CEP.generate(state='SP', formatted=True)`: Gerador para testes.
    """

    EXPECTED_DIGITS: ClassVar[Optional[int]] = 8

    # Faixas de CEP oficiais dos Correios: (min_5_digitos, max_5_digitos, UF)
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
                f"CEP deve conter exatamente 8 dígitos numéricos (recebido {len(digits)})",
                value=value,
            )

        return value

    @property
    def formatted(self) -> str:
        """Retorna o CEP formatado: `00000-000`."""
        d = self.digits
        return f"{d[:5]}-{d[5:]}"

    @property
    def masked(self) -> str:
        """Retorna o CEP mascarado: `00000-***`."""
        d = self.digits
        return f"{d[:5]}-***"

    @property
    def state(self) -> Optional[str]:
        """Retorna a sigla da UF correspondente à faixa postal, se identificada."""
        prefix_5 = int(self.digits[:5])
        for min_val, max_val, uf in self.RANGES:
            if min_val <= prefix_5 <= max_val:
                return uf
        return None

    @classmethod
    def generate(cls, state: Optional[str] = None, formatted: bool = False) -> CEP:
        """Gera um CEP válido para testes.

        Args:
            state: Sigla da UF opcional (ex: 'SP', 'RJ').
            formatted: Se verdadeiro, retorna com pontuação; senão, 8 dígitos.
        """
        if state is not None:
            uf = state.upper().strip()
            matching_ranges = [r for r in cls.RANGES if r[2] == uf]
            if not matching_ranges:
                raise ValueError(f"Estado (UF) desconhecido: {state}")
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
            "description": "Código de Endereçamento Postal (CEP)",
            "examples": ["01310-100", "01310100"],
            "pattern": r"^\d{5}-?\d{3}$",
        }
