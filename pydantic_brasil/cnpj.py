"""Validação e formatação de CNPJ (Cadastro Nacional da Pessoa Jurídica)."""

from __future__ import annotations

import random
import re
from typing import Any, ClassVar, Dict, List, Optional

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.exceptions import CNPJInvalidError


class CNPJ(BrazilianType):
    """Cadastro Nacional da Pessoa Jurídica (CNPJ).

    Recursos:
    - Validação oficial dos dígitos verificadores via Módulo 11.
    - Suporte integral ao padrão numérico e ao novo padrão alfanumérico 2026 da Receita Federal.
    - Rejeição de sequências com todos os caracteres repetidos.
    - `.formatted`: `12.345.678/0001-90`.
    - `.masked`: `12.***.***/0001-90`.
    - `.is_matriz` / `.is_filial`: Identificação de matriz ou filial.
    - `.branch_number`: Identificador de filial/ordem com 4 caracteres.
    - `CNPJ.generate(formatted=True, branch=1)`: Gerador de dados para testes.
    """

    EXPECTED_DIGITS: ClassVar[Optional[int]] = 14
    WEIGHTS_DV1: ClassVar[List[int]] = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    WEIGHTS_DV2: ClassVar[List[int]] = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    @classmethod
    def _char_value(cls, char: str) -> int:
        """Converte o caractere para valor numérico conforme a regra da Receita Federal.

        Dígitos '0'-'9' possuem valores 0 a 9.
        Letras 'A'-'Z' possuem valores ord(char) - 48 (ex: 'A' = 17, 'B' = 18).
        """
        c = char.upper()
        if c.isdigit():
            return int(c)
        if "A" <= c <= "Z":
            return ord(c) - 48
        raise CNPJInvalidError(f"Caractere inválido no CNPJ: '{char}'")

    @classmethod
    def _validate(cls, value: str) -> str:
        cleaned = re.sub(r"[\.\/\-\s]", "", value.upper())

        if len(cleaned) != 14:
            raise CNPJInvalidError(
                f"CNPJ deve conter exatamente 14 caracteres (recebido {len(cleaned)})",
                value=value,
            )

        if cleaned.isdigit() and len(set(cleaned)) == 1:
            raise CNPJInvalidError(
                f"CNPJ não pode conter todos os dígitos iguais: '{value}'",
                value=value,
            )

        if not (cleaned[12].isdigit() and cleaned[13].isdigit()):
            raise CNPJInvalidError(
                f"Os dígitos verificadores do CNPJ devem ser numéricos: '{cleaned[12:]}'",
                value=value,
            )

        # Primeiro dígito verificador
        s1 = sum(cls._char_value(cleaned[i]) * cls.WEIGHTS_DV1[i] for i in range(12))
        r1 = s1 % 11
        dv1 = 0 if r1 < 2 else 11 - r1
        if int(cleaned[12]) != dv1:
            raise CNPJInvalidError(
                f"Primeiro dígito verificador inválido para o CNPJ '{value}'",
                value=value,
            )

        # Segundo dígito verificador
        s2 = sum(cls._char_value(cleaned[i]) * cls.WEIGHTS_DV2[i] for i in range(13))
        r2 = s2 % 11
        dv2 = 0 if r2 < 2 else 11 - r2
        if int(cleaned[13]) != dv2:
            raise CNPJInvalidError(
                f"Segundo dígito verificador inválido para o CNPJ '{value}'",
                value=value,
            )

        return value

    @property
    def formatted(self) -> str:
        """Retorna o CNPJ formatado: `00.000.000/0000-00`."""
        d = str(self)
        return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}"

    @property
    def masked(self) -> str:
        """Retorna o CNPJ mascarado para conformidade com a LGPD: `00.***.***/0000-00`."""
        d = str(self)
        return f"{d[:2]}.***.***/{d[8:12]}-{d[12:]}"

    @property
    def is_matriz(self) -> bool:
        """Retorna True se for matriz (normalmente ordem 0001)."""
        return self.branch_number == "0001"

    @property
    def is_filial(self) -> bool:
        """Retorna True se for filial."""
        return not self.is_matriz

    @property
    def branch_number(self) -> str:
        """Retorna o número/código da filial com 4 caracteres."""
        return str(self)[8:12]

    @property
    def is_alphanumeric(self) -> bool:
        """Retorna True se contiver caracteres alfabéticos (formato 2026)."""
        return any(c.isalpha() for c in str(self)[:12])

    @classmethod
    def generate(cls, formatted: bool = False, branch: int = 1) -> CNPJ:
        """Gera um CNPJ válido para testes.

        Args:
            formatted: Se verdadeiro, retorna formatado com pontuação.
            branch: Número da filial (padrão 1 para matriz '0001').
        """
        root = [random.randint(0, 9) for _ in range(8)]
        branch_str = str(branch).zfill(4)
        chars = [int(c) for c in ("".join(str(d) for d in root) + branch_str)]

        s1 = sum(chars[i] * cls.WEIGHTS_DV1[i] for i in range(12))
        r1 = s1 % 11
        dv1 = 0 if r1 < 2 else 11 - r1
        chars.append(dv1)

        s2 = sum(chars[i] * cls.WEIGHTS_DV2[i] for i in range(13))
        r2 = s2 % 11
        dv2 = 0 if r2 < 2 else 11 - r2
        chars.append(dv2)

        raw = "".join(str(c) for c in chars)
        instance = cls(raw)
        return cls(instance.formatted if formatted else raw)

    @classmethod
    def openapi_schema_extra(cls) -> Dict[str, Any]:
        return {
            "type": "string",
            "title": "CNPJ",
            "description": "Cadastro Nacional da Pessoa Jurídica (CNPJ)",
            "examples": ["12.345.678/0001-90", "12ABC345000167"],
            "pattern": r"^[A-Z0-9]{2}\.?[A-Z0-9]{3}\.?[A-Z0-9]{3}\/?[A-Z0-9]{4}-?\d{2}$",
        }
