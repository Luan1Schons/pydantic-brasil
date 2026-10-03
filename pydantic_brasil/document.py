"""Polymorphic Brazilian document (CPF or CNPJ)."""

from __future__ import annotations

import re
from typing import Any, Dict, Union, cast

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.cnpj import CNPJ
from pydantic_brasil.cpf import CPF
from pydantic_brasil.exceptions import BrazilianValidationError


class CPFouCNPJ(BrazilianType):
    """Polymorphic Brazilian taxpayer document (accepts either CPF or CNPJ).

    Automatically detects whether the input is a CPF or CNPJ and executes the
    appropriate checksum and constraint validations.
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

        # Check for CPF (11 digits, or int <= 11)
        if len(digits) == 11 or (digits.isdigit() and len(digits) <= 11 and "/" not in value):
            try:
                return CPF(value)
            except Exception as e_cpf:
                if len(raw_alphanumeric) != 14:
                    raise e_cpf

        # Check for CNPJ (14 characters or containing /)
        try:
            return CNPJ(value)
        except Exception as e_cnpj:
            raise BrazilianValidationError(
                f"Value '{value}' is neither a valid CPF nor a valid CNPJ.",
                value=value,
            ) from e_cnpj

    @property
    def is_cpf(self) -> bool:
        """Returns True if this document is a CPF."""
        return isinstance(self._inner, CPF)

    @property
    def is_cnpj(self) -> bool:
        """Returns True if this document is a CNPJ."""
        return isinstance(self._inner, CNPJ)

    def as_cpf(self) -> CPF:
        """Returns the document as a typed CPF instance, or raises ValueError."""
        if not self.is_cpf:
            raise ValueError(f"Document '{self}' is a CNPJ, not a CPF")
        return self._inner  # type: ignore[return-value]

    def as_cnpj(self) -> CNPJ:
        """Returns the document as a typed CNPJ instance, or raises ValueError."""
        if not self.is_cnpj:
            raise ValueError(f"Document '{self}' is a CPF, not a CNPJ")
        return self._inner  # type: ignore[return-value]

    @property
    def formatted(self) -> str:
        """Returns standard punctuated string (CPF: 000.000.000-00, CNPJ: 00.000.000/0000-00)."""
        return self._inner.formatted

    @property
    def masked(self) -> str:
        """Returns LGPD-compliant masked document string."""
        return self._inner.masked

    @classmethod
    def openapi_schema_extra(cls) -> Dict[str, Any]:
        return {
            "type": "string",
            "title": "CPFouCNPJ",
            "description": (
                "Brazilian taxpayer identifier: either a valid CPF (11 digits) or CNPJ (14 digits)"
            ),
            "examples": ["123.456.789-00", "12.345.678/0001-90"],
        }


# Alias for readability
DocumentoBR = CPFouCNPJ
