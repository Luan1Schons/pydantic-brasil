"""Documento fiscal brasileiro polimórfico (CPF ou CNPJ)."""

from __future__ import annotations

import re
from typing import Any, Dict, Union, cast

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.cnpj import CNPJ
from pydantic_brasil.cpf import CPF
from pydantic_brasil.exceptions import BrazilianValidationError


class CPFouCNPJ(BrazilianType):
    """Documento de identificação fiscal brasileiro (aceita CPF ou CNPJ).

    Identifica automaticamente se a entrada é um CPF ou CNPJ e executa
    as respectivas regras e validações matemáticas de dígitos verificadores.
    """

    _inner: Union[CPF, CNPJ]

    def __new__(cls, value: Any) -> CPFouCNPJ:
        if isinstance(value, cls):
            return value

        cleaned = cls._clean_input(value)
        validated_doc = cls._resolve(cleaned)

        instance = cast(CPFouCNPJ, super().__new__(cls, str(validated_doc)))
        instance._inner = validated_doc
        instance._digits = validated_doc.digits
        return instance

    @classmethod
    def _validate(cls, value: str) -> str:
        doc = cls._resolve(value)
        return str(doc)

    @classmethod
    def _resolve(cls, value: str) -> Union[CPF, CNPJ]:
        digits = cls._extract_digits(value)
        raw_alphanumeric = re.sub(r"[\.\/\-\s]", "", value.upper())

        # Verifica se é CPF (11 dígitos numéricos)
        if len(digits) == 11 or (digits.isdigit() and len(digits) <= 11 and "/" not in value):
            try:
                return CPF(value)
            except Exception as e_cpf:
                if len(raw_alphanumeric) != 14:
                    raise e_cpf

        # Verifica se é CNPJ (14 caracteres ou barra presente)
        try:
            return CNPJ(value)
        except Exception as e_cnpj:
            raise BrazilianValidationError(
                f"O valor '{value}' não é um CPF nem um CNPJ válido.",
                value=value,
            ) from e_cnpj

    @property
    def is_cpf(self) -> bool:
        """Retorna True se for um CPF."""
        return isinstance(self._inner, CPF)

    @property
    def is_cnpj(self) -> bool:
        """Retorna True se for um CNPJ."""
        return isinstance(self._inner, CNPJ)

    def as_cpf(self) -> CPF:
        """Retorna a instância como CPF tipado ou lança ValueError."""
        if not self.is_cpf:
            raise ValueError(f"O documento '{self}' é um CNPJ, não um CPF")
        return self._inner  # type: ignore[return-value]

    def as_cnpj(self) -> CNPJ:
        """Retorna a instância como CNPJ tipado ou lança ValueError."""
        if not self.is_cnpj:
            raise ValueError(f"O documento '{self}' é um CPF, não um CNPJ")
        return self._inner  # type: ignore[return-value]

    @property
    def formatted(self) -> str:
        """Retorna o documento formatado."""
        return self._inner.formatted

    @property
    def masked(self) -> str:
        """Retorna o documento mascarado em conformidade com a LGPD."""
        return self._inner.masked

    @classmethod
    def openapi_schema_extra(cls) -> Dict[str, Any]:
        return {
            "type": "string",
            "title": "CPFouCNPJ",
            "description": (
                "Documento de identificação fiscal: CPF (11 dígitos) ou CNPJ (14 dígitos)"
            ),
            "examples": ["123.456.789-00", "12.345.678/0001-90"],
        }


# Alias
DocumentoBR = CPFouCNPJ
