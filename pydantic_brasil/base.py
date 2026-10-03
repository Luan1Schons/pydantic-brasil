"""Base class for all Brazilian value objects in pydantic-brasil."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, Optional

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic_core import CoreSchema, core_schema


class BrazilianType(str, ABC):
    """Abstract base class for Brazilian documents, numbers, and value objects.

    Subclasses inherit from `str` for seamless JSON serialization and interoperability,
    while offering rich value-object methods such as `.digits`, `.formatted`, and `.masked`.
    """

    EXPECTED_DIGITS: ClassVar[Optional[int]] = None

    def __new__(cls, value: Any) -> BrazilianType:
        if isinstance(value, cls):
            return value

        cleaned = cls._clean_input(value)
        validated = cls._validate(cleaned)
        instance = super().__new__(cls, validated)
        instance._digits = cls._extract_digits(validated)
        return instance

    @classmethod
    def _clean_input(cls, value: Any) -> str:
        """Converts input to string and strips leading/trailing whitespace.

        Pads integers with leading zeros if EXPECTED_DIGITS is defined.
        """
        if value is None:
            raise TypeError("Value cannot be None")
        if isinstance(value, int) and cls.EXPECTED_DIGITS is not None:
            return str(value).zfill(cls.EXPECTED_DIGITS)
        return str(value).strip()

    @classmethod
    def _extract_digits(cls, value: str) -> str:
        """Extracts only decimal digits from the string."""
        return re.sub(r"\D", "", value)

    @classmethod
    @abstractmethod
    def _validate(cls, value: str) -> str:
        """Validates the input string and returns the canonical or valid value."""
        raise NotImplementedError

    @property
    def digits(self) -> str:
        """Returns only the numerical digits of the document/code."""
        if not hasattr(self, "_digits"):
            self._digits = self._extract_digits(str(self))
        return self._digits

    @property
    @abstractmethod
    def formatted(self) -> str:
        """Returns the document formatted with standard Brazilian punctuation."""
        raise NotImplementedError

    @property
    @abstractmethod
    def masked(self) -> str:
        """Returns the document with sensitive digits hidden for LGPD compliance."""
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        """Smart equality comparison.

        Allows comparing with another BrazilianType, pure digits, or formatted strings.
        """
        if isinstance(other, BrazilianType):
            return self.digits == other.digits
        if isinstance(other, (str, int)):
            other_digits = self._extract_digits(str(other))
            if other_digits and self.digits:
                return self.digits == other_digits
            return str(self) == str(other)
        return False

    def __hash__(self) -> int:
        return hash(self.digits or str(self))

    @classmethod
    def openapi_schema_extra(cls) -> Dict[str, Any]:
        """Provides OpenAPI documentation metadata for FastAPI Swagger/ReDoc."""
        return {
            "type": "string",
            "title": cls.__name__,
            "description": f"Valid Brazilian {cls.__name__}",
        }

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Generates Pydantic v2 core schema with zero-overhead validation."""
        return core_schema.json_or_python_schema(
            json_schema=core_schema.chain_schema(
                [
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls),
                ]
            ),
            python_schema=core_schema.chain_schema(
                [
                    core_schema.union_schema(
                        [
                            core_schema.is_instance_schema(cls),
                            core_schema.str_schema(),
                            core_schema.int_schema(),
                        ]
                    ),
                    core_schema.no_info_plain_validator_function(cls),
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: (
                    instance.digits if getattr(instance, "digits", None) else str(instance)
                )
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> Dict[str, Any]:
        """Injects custom JSON Schema and OpenAPI documentation into FastAPI schemas."""
        json_schema = handler(core_schema.str_schema())
        json_schema.update(cls.openapi_schema_extra())
        return json_schema
