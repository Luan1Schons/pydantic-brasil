"""Documentos de trânsito e veículos (PlacaVeiculo, RENAVAM, CNH)."""

from __future__ import annotations

import re
from typing import Any, ClassVar, Dict, List

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.exceptions import (
    CNHInvalidError,
    RenavamInvalidError,
    VehiclePlateInvalidError,
)


class PlacaVeiculo(BrazilianType):
    """Placa de identificação veicular brasileira (Padrão Mercosul e Tradicional).

    Recursos:
    - Validação de placas do formato tradicional (`ABC-1234`) e Mercosul (`ABC1D23`).
    - Conversão bidirecional entre os padrões oficializada pelo Denatran.
    - `.is_mercosul`: Informa se a placa utiliza o padrão Mercosul.
    - `.to_mercosul()`: Converte placa tradicional para padrão Mercosul.
    - `.to_antiga()`: Converte placa Mercosul para padrão tradicional.
    """

    TRADITIONAL_REGEX: ClassVar[re.Pattern[str]] = re.compile(r"^[A-Z]{3}-?\d{4}$")
    MERCOSUL_REGEX: ClassVar[re.Pattern[str]] = re.compile(r"^[A-Z]{3}\d[A-Z]\d{2}$")

    # Mapeamento oficial de conversão do 5º caractere
    NUMBER_TO_LETTER: ClassVar[Dict[str, str]] = {
        "0": "A",
        "1": "B",
        "2": "C",
        "3": "D",
        "4": "E",
        "5": "F",
        "6": "G",
        "7": "H",
        "8": "I",
        "9": "J",
    }
    LETTER_TO_NUMBER: ClassVar[Dict[str, str]] = {v: k for k, v in NUMBER_TO_LETTER.items()}

    @classmethod
    def _validate(cls, value: str) -> str:
        clean = re.sub(r"[\s\-]", "", value.upper())
        if len(clean) != 7:
            raise VehiclePlateInvalidError(
                f"Placa de veículo deve conter 7 caracteres (recebido '{value}')",
                value=value,
            )

        if cls.MERCOSUL_REGEX.match(clean) or cls.TRADITIONAL_REGEX.match(clean):
            return clean

        raise VehiclePlateInvalidError(
            f"Placa de veículo '{value}' não atende ao padrão tradicional (ABC-1234) "
            f"nem ao padrão Mercosul (ABC1D23).",
            value=value,
        )

    @property
    def is_mercosul(self) -> bool:
        """Retorna True se for uma placa no formato Mercosul (ABC1D23)."""
        return bool(self.MERCOSUL_REGEX.match(str(self)))

    @property
    def is_antiga(self) -> bool:
        """Retorna True se for uma placa no formato tradicional/antigo (ABC-1234)."""
        return bool(self.TRADITIONAL_REGEX.match(str(self)))

    @property
    def formatted(self) -> str:
        """Retorna a placa com formatação: 'ABC-1234' ou 'ABC1D23'."""
        raw = str(self)
        if self.is_mercosul:
            return raw
        return f"{raw[:3]}-{raw[3:]}"

    @property
    def masked(self) -> str:
        """Retorna a placa com caracteres parciais ocultados: 'ABC-**34' ou 'ABC1**3'."""
        raw = str(self)
        if self.is_mercosul:
            return f"{raw[:4]}**{raw[-1]}"
        return f"{raw[:3]}-**{raw[-2:]}"

    def to_mercosul(self) -> PlacaVeiculo:
        """Converte placa do padrão antigo para o padrão Mercosul correspondente."""
        if self.is_mercosul:
            return self
        raw = str(self)
        fifth_char = self.NUMBER_TO_LETTER.get(raw[4], raw[4])
        return PlacaVeiculo(f"{raw[:4]}{fifth_char}{raw[5:]}")

    def to_antiga(self) -> PlacaVeiculo:
        """Converte placa do padrão Mercosul para o padrão antigo tradicional."""
        if not self.is_mercosul:
            return self
        raw = str(self)
        fifth_char = self.LETTER_TO_NUMBER.get(raw[4], raw[4])
        return PlacaVeiculo(f"{raw[:4]}{fifth_char}{raw[5:]}")

    @classmethod
    def openapi_schema_extra(cls) -> Dict[str, Any]:
        return {
            "type": "string",
            "title": "PlacaVeiculo",
            "description": (
                "Placa de veículo brasileira (Padrão Tradicional ABC-1234 ou Mercosul ABC1D23)"
            ),
            "examples": ["ABC-1234", "ABC1D23"],
            "pattern": r"^[A-Z]{3}-?\d([A-Z]|\d)\d{2}$",
        }


class RENAVAM(BrazilianType):
    """Registro Nacional de Veículos Automotores (RENAVAM).

    Recursos:
    - Código numérico de 11 dígitos com validação oficial de Módulo 11.
    - Trata números legados preenchendo até 11 dígitos.
    - `.formatted`: `0000000000-0`.
    - `.masked`: `****.******-1`.
    """

    WEIGHTS: ClassVar[List[int]] = [3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    @classmethod
    def _validate(cls, value: str) -> str:
        digits = cls._extract_digits(value)

        # Ajusta renavam legado de 8 a 11 dígitos
        if 8 <= len(digits) <= 11 and value.isdigit():
            digits = digits.zfill(11)

        if len(digits) != 11:
            raise RenavamInvalidError(
                f"RENAVAM deve ter 11 dígitos (recebido {len(digits)})",
                value=value,
            )

        if len(set(digits)) == 1:
            raise RenavamInvalidError(
                f"RENAVAM não pode conter todos os dígitos iguais: '{value}'",
                value=value,
            )

        sum_val = sum(int(digits[i]) * cls.WEIGHTS[i] for i in range(10))
        rem = (sum_val * 10) % 11
        dv = 0 if rem in (10, 11) else rem

        if int(digits[10]) != dv:
            raise RenavamInvalidError(
                f"Dígito verificador inválido para o RENAVAM '{value}'",
                value=value,
            )

        return digits

    @property
    def formatted(self) -> str:
        """Retorna o RENAVAM formatado: `0000000000-0`."""
        d = self.digits
        return f"{d[:10]}-{d[10:]}"

    @property
    def masked(self) -> str:
        """Retorna o RENAVAM mascarado: `****.******-0`."""
        d = self.digits
        return f"****.******-{d[10:]}"

    @classmethod
    def openapi_schema_extra(cls) -> Dict[str, Any]:
        return {
            "type": "string",
            "title": "RENAVAM",
            "description": "Registro Nacional de Veículos Automotores (RENAVAM)",
            "examples": ["00123456789"],
            "pattern": r"^\d{11}$",
        }


class CNH(BrazilianType):
    """Carteira Nacional de Habilitação (CNH).

    Recursos:
    - Código numérico de 11 dígitos com dupla verificação de Módulo 11.
    - `.formatted`: 11 dígitos numéricos.
    - `.masked`: `***.*****.**-0`.
    """

    @classmethod
    def _validate(cls, value: str) -> str:
        digits = cls._extract_digits(value)

        if 9 <= len(digits) <= 11 and value.isdigit():
            digits = digits.zfill(11)

        if len(digits) != 11:
            raise CNHInvalidError(
                f"CNH deve ter 11 dígitos (recebido {len(digits)})",
                value=value,
            )

        if len(set(digits)) == 1:
            raise CNHInvalidError(
                f"CNH não pode conter todos os dígitos iguais: '{value}'",
                value=value,
            )

        # Primeiro dígito verificador
        s1 = sum(int(digits[i]) * (9 - i) for i in range(9))
        r1 = s1 % 11
        incr = 0
        if r1 >= 10:
            dv1 = 0
            incr = -2 if r1 == 10 else 0
        else:
            dv1 = r1

        if int(digits[9]) != dv1:
            raise CNHInvalidError(
                f"Primeiro dígito verificador inválido para a CNH '{value}'",
                value=value,
            )

        # Segundo dígito verificador
        s2 = sum(int(digits[i]) * (1 + i) for i in range(9))
        r2 = (s2 + incr) % 11
        if r2 >= 10:
            dv2 = 0
        else:
            dv2 = r2

        if int(digits[10]) != dv2:
            raise CNHInvalidError(
                f"Segundo dígito verificador inválido para a CNH '{value}'",
                value=value,
            )

        return digits

    @property
    def formatted(self) -> str:
        """Retorna a CNH formatada."""
        return self.digits

    @property
    def masked(self) -> str:
        """Retorna a CNH mascarada."""
        d = self.digits
        return f"***.*****.**-{d[-1]}"

    @classmethod
    def openapi_schema_extra(cls) -> Dict[str, Any]:
        return {
            "type": "string",
            "title": "CNH",
            "description": "Carteira Nacional de Habilitação (CNH)",
            "examples": ["12345678901"],
            "pattern": r"^\d{11}$",
        }
