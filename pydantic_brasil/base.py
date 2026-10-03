"""Classe base para todos os tipos de dados e objetos de valor brasileiros."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, Optional

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic_core import CoreSchema, core_schema


class BrazilianType(str, ABC):
    """Classe base abstrata para documentos, códigos e valores brasileiros.

    Herda de `str` para interoperabilidade e serialização direta em JSON,
    oferecendo métodos avançados como `.digits`, `.formatted` e `.masked`.
    """

    EXPECTED_DIGITS: ClassVar[Optional[int]] = None
    SERIALIZE_AS_DIGITS: ClassVar[bool] = True

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
        """Converte a entrada para texto e remove espaços no início e fim.

        Preenche inteiros com 0 à esquerda caso EXPECTED_DIGITS esteja definido.
        """
        if value is None:
            raise TypeError("Valor não pode ser nulo (None)")
        if isinstance(value, int) and cls.EXPECTED_DIGITS is not None:
            return str(value).zfill(cls.EXPECTED_DIGITS)
        return str(value).strip()

    @classmethod
    def _extract_digits(cls, value: str) -> str:
        """Extrai apenas os dígitos numéricos da sequência."""
        return re.sub(r"\D", "", value)

    @classmethod
    @abstractmethod
    def _validate(cls, value: str) -> str:
        """Valida a entrada e retorna o valor canônico ou validado."""
        raise NotImplementedError

    @property
    def digits(self) -> str:
        """Retorna apenas os dígitos numéricos do documento ou código."""
        if not hasattr(self, "_digits"):
            self._digits = self._extract_digits(str(self))
        return self._digits

    @property
    @abstractmethod
    def formatted(self) -> str:
        """Retorna o documento formatado na pontuação oficial brasileira."""
        raise NotImplementedError

    @property
    @abstractmethod
    def masked(self) -> str:
        """Retorna o documento mascarado para conformidade com a LGPD."""
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        """Comparação inteligente de igualdade.

        Permite comparar instâncias entre si, com dígitos puros ou strings formatadas.
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
        """Fornece metadados de documentação OpenAPI para o Swagger e Redoc do FastAPI."""
        return {
            "type": "string",
            "title": cls.__name__,
            "description": f"Documento brasileiro válido do tipo {cls.__name__}",
        }

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Gera o schema do pydantic-core para validação nativa de alta performance."""
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
                    instance.digits
                    if (
                        getattr(instance, "SERIALIZE_AS_DIGITS", True)
                        and getattr(instance, "digits", None)
                    )
                    else str(instance)
                )
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> Dict[str, Any]:
        """Injeta metadados de JSON Schema e OpenAPI nas rotas do FastAPI."""
        json_schema = handler(core_schema.str_schema())
        json_schema.update(cls.openapi_schema_extra())
        return json_schema
