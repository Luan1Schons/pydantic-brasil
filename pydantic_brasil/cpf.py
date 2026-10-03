"""Validação e formatação de CPF (Cadastro de Pessoas Físicas)."""

from __future__ import annotations

import random
from typing import Any, ClassVar, Dict, List, Optional, Union

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.exceptions import CPFInvalidError


class CPF(BrazilianType):
    """Cadastro de Pessoas Físicas (CPF).

    Recursos:
    - Validação matemática oficial dos dígitos verificadores (Módulo 11).
    - Rejeição de sequências com todos os dígitos repetidos (ex: 111.111.111-11).
    - `.formatted`: Formatação padrão: `123.456.789-00`.
    - `.masked`: Mascaramento conforme a LGPD: `***.456.789-**`.
    - `.digits`: Dígitos numéricos puros: `12345678900`.
    - `.fiscal_region`: Região fiscal da Receita Federal (estados) de emissão (9º dígito).
    - `CPF.generate(state='SP', formatted=True)`: Gerador de dados válidos para testes.
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
                f"CPF deve conter exatamente 11 dígitos numéricos (recebido {len(digits)})",
                value=value,
            )

        if len(set(digits)) == 1:
            raise CPFInvalidError(
                f"CPF não pode conter todos os dígitos iguais: '{value}'",
                value=value,
            )

        # Primeiro dígito verificador
        s1 = sum(int(digits[i]) * (10 - i) for i in range(9))
        d1 = 11 - (s1 % 11)
        dv1 = 0 if d1 >= 10 else d1
        if int(digits[9]) != dv1:
            raise CPFInvalidError(
                f"Primeiro dígito verificador inválido para o CPF '{value}'",
                value=value,
            )

        # Segundo dígito verificador
        s2 = sum(int(digits[i]) * (11 - i) for i in range(10))
        d2 = 11 - (s2 % 11)
        dv2 = 0 if d2 >= 10 else d2
        if int(digits[10]) != dv2:
            raise CPFInvalidError(
                f"Segundo dígito verificador inválido para o CPF '{value}'",
                value=value,
            )

        return value

    @property
    def formatted(self) -> str:
        """Retorna o CPF formatado: `000.000.000-00`."""
        d = self.digits
        return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"

    @property
    def masked(self) -> str:
        """Retorna o CPF mascarado para conformidade com a LGPD: `***.000.000-**`."""
        d = self.digits
        return f"***.{d[3:6]}.{d[6:9]}-**"

    @property
    def fiscal_region(self) -> List[str]:
        """Retorna a lista de estados (UFs) da Região Fiscal emissora (9º dígito)."""
        digit = int(self.digits[8])
        return self.FISCAL_REGIONS[digit]

    @classmethod
    def generate(cls, state: Optional[Union[str, int]] = None, formatted: bool = False) -> CPF:
        """Gera um CPF válido para testes.

        Args:
            state: Sigla da UF (ex: 'SP', 'RJ') ou dígito da região fiscal (0 a 9).
            formatted: Se verdadeiro, retorna formatado com pontuação; caso contrário, dígitos.
        """
        digits = [random.randint(0, 9) for _ in range(8)]

        if state is not None:
            if isinstance(state, str):
                uf = state.upper().strip()
                if uf not in cls.STATE_TO_DIGIT:
                    raise ValueError(f"Estado (UF) desconhecido: {state}")
                digits.append(cls.STATE_TO_DIGIT[uf])
            elif isinstance(state, int):
                if not (0 <= state <= 9):
                    raise ValueError("O dígito do estado deve estar entre 0 e 9")
                digits.append(state)
        else:
            digits.append(random.randint(0, 9))

        s1 = sum(digits[i] * (10 - i) for i in range(9))
        d1 = 11 - (s1 % 11)
        dv1 = 0 if d1 >= 10 else d1
        digits.append(dv1)

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
            "description": "Cadastro de Pessoas Físicas (CPF) com validação de dígitos",
            "examples": ["123.456.789-00", "12345678900"],
            "pattern": r"^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$",
        }
