"""Validação e formatação de Processo Judicial CNJ (Numeração Única)."""

from __future__ import annotations

import random
from typing import ClassVar, Dict, Optional

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.exceptions import ProcessoCNJInvalidError


class ProcessoCNJ(BrazilianType):
    """Numeração Única de Processos Judiciais (Resolução CNJ nº 65/2008).

    Formato de 20 dígitos: NNNNNNN-DD.AAAA.J.TR.OOOO.
    - NNNNNNN: 7 dígitos do número sequencial no ano
    - DD: 2 dígitos verificadores (Módulo 97 - ISO 7064)
    - AAAA: 4 dígitos do ano de ajuizamento
    - J: 1 dígito do segmento da Justiça (ex: 8 para Estadual, 4 para Federal)
    - TR: 2 dígitos do tribunal / região
    - OOOO: 4 dígitos da vara / comarca / unidade de origem
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
                f"Processo CNJ deve conter exatamente 20 dígitos (recebido '{value}')",
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
                f"Segmento da justiça '{j}' inválido no Processo CNJ '{value}'",
                value=value,
            )

        # Validação matemática dos dígitos via Módulo 97 (ISO 7064)
        num_without_dv = f"{seq}{year}{j}{tr}{orig}00"
        rem = int(num_without_dv) % 97
        expected_dv = 98 - rem
        expected_dv_str = f"{expected_dv:02d}"

        if dv != expected_dv_str:
            raise ProcessoCNJInvalidError(
                f"Dígitos verificadores inválidos no Processo CNJ '{value}' "
                f"(esperado '{expected_dv_str}', recebido '{dv}')",
                value=value,
            )

        return digits

    @property
    def sequential(self) -> str:
        """Retorna o número sequencial com 7 dígitos."""
        return self.digits[:7]

    @property
    def check_digits(self) -> str:
        """Retorna os 2 dígitos verificadores (DD)."""
        return self.digits[7:9]

    @property
    def year(self) -> int:
        """Retorna o ano de ajuizamento (AAAA)."""
        return int(self.digits[9:13])

    @property
    def segment_id(self) -> int:
        """Retorna o identificador do segmento judiciário (J)."""
        return int(self.digits[13])

    @property
    def segment_name(self) -> str:
        """Retorna o nome por extenso do segmento da Justiça."""
        return self.SEGMENT_NAMES.get(self.segment_id, "Desconhecido")

    @property
    def tribunal(self) -> str:
        """Retorna o identificador do tribunal / região (TR)."""
        return self.digits[14:16]

    @property
    def origin(self) -> str:
        """Retorna o código da vara / comarca de origem (OOOO)."""
        return self.digits[16:20]

    @property
    def formatted(self) -> str:
        """Retorna o Processo CNJ formatado: `NNNNNNN-DD.AAAA.J.TR.OOOO`."""
        d = self.digits
        return f"{d[:7]}-{d[7:9]}.{d[9:13]}.{d[13]}.{d[14:16]}.{d[16:]}"

    @property
    def masked(self) -> str:
        """Retorna o Processo CNJ mascarado conforme a LGPD: `NNNNNNN-DD.AAAA.*.**.OOOO`."""
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
        """Gera um número de Processo CNJ válido para testes."""
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
