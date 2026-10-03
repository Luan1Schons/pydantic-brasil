"""Brazilian Real (BRL) currency Value Object (DinheiroBRL)."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any, Dict, Union

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic_core import CoreSchema, core_schema
from pydantic_brasil.exceptions import MoneyInvalidError


class DinheiroBRL:
    """Brazilian Real (BRL) currency Value Object backed by `decimal.Decimal`.

    Features:
    - Precise fixed-point decimal arithmetic (no binary float rounding errors).
    - Parses strings with Brazilian formatting (`"R$ 1.250,50"`, `"1250,50"`,
      `"1250.50"`), ints, floats and Decimals.
    - `.amount`: Returns the exact `Decimal` value rounded to 2 decimal places.
    - `.centavos`: Returns the integer value in cents (e.g. 125050 for R$ 1.250,50 -
      essential for Stripe, Pagar.me, etc.).
    - `.formatted`: Formatted Brazilian string (`R$ 1.250,50`).
    - Full arithmetic support (`+`, `-`, `*`, `/`, `<`, `<=`, `>`, `>=`, `==`).
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

            # Handle Brazilian notation (1.234,56) vs standard notation (1234.56)
            if "," in clean and "." in clean:
                # E.g. 1.234,56 -> remove dots, replace comma with dot
                clean = clean.replace(".", "").replace(",", ".")
            elif "," in clean:
                # E.g. 1234,56 -> replace comma with dot
                clean = clean.replace(",", ".")

            # Remove spaces
            clean = re.sub(r"\s+", "", clean)

            try:
                dec = Decimal(clean)
                return dec.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            except InvalidOperation as exc:
                raise MoneyInvalidError(
                    f"Cannot parse '{value}' as Brazilian Real currency (BRL).",
                    value=value,
                ) from exc

        raise MoneyInvalidError(
            f"Unsupported type for DinheiroBRL: {type(value).__name__}",
            value=value,
        )

    @property
    def amount(self) -> Decimal:
        """Returns the exact `Decimal` amount (e.g. Decimal('1250.50'))."""
        return self._amount

    @property
    def centavos(self) -> int:
        """Returns the amount converted to integer cents (e.g. 125050 for R$ 1.250,50)."""
        return int(self._amount * 100)

    @property
    def formatted(self) -> str:
        """Returns standard Brazilian currency string: `R$ 1.250,50`."""
        return f"R$ {self.formatted_no_symbol}"

    @property
    def formatted_no_symbol(self) -> str:
        """Returns formatted string without currency symbol: `1.250,50`."""
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
        """Creates a DinheiroBRL instance from integer centavos (e.g. 1000 -> R$ 10,00)."""
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
            "description": "Brazilian Real currency (BRL)",
            "examples": ["R$ 1.250,50", 1250.50],
        }


# Short alias
BRL = DinheiroBRL
