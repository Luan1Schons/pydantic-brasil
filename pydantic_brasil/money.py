"""Objeto de valor para moeda brasileira (Real - BRL)."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any, Dict, Union

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic_core import CoreSchema, core_schema
from pydantic_brasil.exceptions import MoneyInvalidError


class DinheiroBRL:
    """Objeto de valor para valores monetários em Real (BRL) baseado em `decimal.Decimal`.

    Recursos:
    - Aritmética decimal de ponto fixo precisa (sem erros de arredondamento de float binário).
    - Interpreta strings no padrão brasileiro (`"R$ 1.250,50"`, `"1250,50"`,
      `"1250.50"`), inteiros, floats e Decimals.
    - `.amount`: Retorna o valor exato em `Decimal` arredondado para 2 casas decimais.
    - `.centavos`: Retorna o valor em centavos inteiros (ex: 125050 para R$ 1.250,50 -
      ideal para gateways de pagamento como Pagar.me, Asaas, etc.).
    - `.formatted`: String formatada no padrão brasileiro (`R$ 1.250,50`).
    - Suporte aritmético completo (`+`, `-`, `*`, `/`, `<`, `<=`, `>`, `>=`, `==`).
    """

    _amount: Decimal

    def __init__(self, value: Any) -> None:
        self._amount = self._parse_to_decimal(value)

    @classmethod
    def _parse_to_decimal(cls, value: Any) -> Decimal:
        if isinstance(value, DinheiroBRL):
            return value._amount

        if isinstance(value, Decimal):
            return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if isinstance(value, (int, float)):
            return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if isinstance(value, str):
            clean = value.strip().upper()
            clean = clean.replace("R$", "").strip()

            # Trata pontuação brasileira (1.234,56) vs padrão internacional (1234.56)
            if "," in clean and "." in clean:
                clean = clean.replace(".", "").replace(",", ".")
            elif "," in clean:
                clean = clean.replace(",", ".")

            clean = re.sub(r"\s+", "", clean)

            try:
                dec = Decimal(clean)
                return dec.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            except InvalidOperation as exc:
                raise MoneyInvalidError(
                    f"Não foi possível converter '{value}' em moeda Real (BRL).",
                    value=value,
                ) from exc

        raise MoneyInvalidError(
            f"Tipo incompatível para DinheiroBRL: {type(value).__name__}",
            value=value,
        )

    @property
    def amount(self) -> Decimal:
        """Retorna o valor exato em `Decimal` (ex: Decimal('1250.50'))."""
        return self._amount

    @property
    def centavos(self) -> int:
        """Retorna o valor convertido em centavos inteiros (ex: 125050 para R$ 1.250,50)."""
        return int(self._amount * 100)

    @property
    def formatted(self) -> str:
        """Retorna a representação monetária brasileira: `R$ 1.250,50`."""
        return f"R$ {self.formatted_no_symbol}"

    @property
    def formatted_no_symbol(self) -> str:
        """Retorna o valor formatado sem o símbolo R$: `1.250,50`."""
        cents = abs(self.centavos) % 100
        whole = abs(int(self._amount))
        whole_str = f"{whole:,}".replace(",", ".")
        sign = "-" if self._amount < 0 else ""
        return f"{sign}{whole_str},{cents:02d}"

    def __str__(self) -> str:
        return self.formatted

    def __repr__(self) -> str:
        return f"DinheiroBRL('{self.formatted}')"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DinheiroBRL):
            return self._amount == other._amount
        if isinstance(other, (Decimal, int, float, str)):
            try:
                other_dec = self._parse_to_decimal(other)
                return self._amount == other_dec
            except Exception:
                return False
        return False

    def __lt__(self, other: Any) -> bool:
        return self._amount < self._parse_to_decimal(other)

    def __le__(self, other: Any) -> bool:
        return self._amount <= self._parse_to_decimal(other)

    def __gt__(self, other: Any) -> bool:
        return self._amount > self._parse_to_decimal(other)

    def __ge__(self, other: Any) -> bool:
        return self._amount >= self._parse_to_decimal(other)

    def __add__(self, other: Any) -> DinheiroBRL:
        return DinheiroBRL(self._amount + self._parse_to_decimal(other))

    def __sub__(self, other: Any) -> DinheiroBRL:
        return DinheiroBRL(self._amount - self._parse_to_decimal(other))

    def __mul__(self, other: Union[int, float, Decimal]) -> DinheiroBRL:
        return DinheiroBRL(self._amount * Decimal(str(other)))

    def __truediv__(self, other: Union[int, float, Decimal]) -> DinheiroBRL:
        return DinheiroBRL(self._amount / Decimal(str(other)))

    def __abs__(self) -> DinheiroBRL:
        return DinheiroBRL(abs(self._amount))

    def __hash__(self) -> int:
        return hash(self._amount)

    @classmethod
    def from_centavos(cls, cents: int) -> DinheiroBRL:
        """Cria DinheiroBRL a partir de centavos inteiros (ex: 1000 -> R$ 10,00)."""
        return cls(Decimal(cents) / Decimal(100))

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.chain_schema(
                [
                    core_schema.union_schema(
                        [
                            core_schema.str_schema(),
                            core_schema.float_schema(),
                            core_schema.int_schema(),
                        ]
                    ),
                    core_schema.no_info_plain_validator_function(cls),
                ]
            ),
            python_schema=core_schema.chain_schema(
                [
                    core_schema.union_schema(
                        [
                            core_schema.is_instance_schema(cls),
                            core_schema.is_instance_schema(Decimal),
                            core_schema.str_schema(),
                            core_schema.float_schema(),
                            core_schema.int_schema(),
                        ]
                    ),
                    core_schema.no_info_plain_validator_function(cls),
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: float(instance.amount)
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> Dict[str, Any]:
        return {
            "type": "number",
            "title": "DinheiroBRL",
            "description": "Valor monetário em Real brasileiro (BRL)",
            "examples": ["R$ 1.250,50", 1250.50],
        }


# Alias
BRL = DinheiroBRL
