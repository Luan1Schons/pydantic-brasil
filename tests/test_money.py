from decimal import Decimal
import pytest
from pydantic import BaseModel, ValidationError

from pydantic_brasil.exceptions import MoneyInvalidError
from pydantic_brasil.money import BRL, DinheiroBRL


class OrderItem(BaseModel):
    preco: DinheiroBRL


def test_brl_alias():
    assert BRL == DinheiroBRL


def test_money_parse_brazilian_string():
    m = DinheiroBRL("R$ 1.250,50")
    assert m.amount == Decimal("1250.50")
    assert m.centavos == 125050
    assert m.formatted == "R$ 1.250,50"
    assert m.formatted_no_symbol == "1.250,50"


def test_money_parse_simple_comma():
    m = DinheiroBRL("1250,50")
    assert m.amount == Decimal("1250.50")
    assert m.centavos == 125050


def test_money_parse_dot_float():
    m = DinheiroBRL(1250.5)
    assert m.amount == Decimal("1250.50")
    assert m.centavos == 125050


def test_money_from_centavos():
    m = DinheiroBRL.from_centavos(9900)
    assert m.amount == Decimal("99.00")
    assert m.formatted == "R$ 99,00"


def test_money_arithmetic():
    m1 = DinheiroBRL("R$ 10,00")
    m2 = DinheiroBRL("R$ 5,50")

    add = m1 + m2
    assert add.formatted == "R$ 15,50"

    sub = m1 - m2
    assert sub.formatted == "R$ 4,50"

    mul = m1 * 2
    assert mul.formatted == "R$ 20,00"

    div = m1 / 2
    assert div.formatted == "R$ 5,00"


def test_money_comparisons():
    m1 = DinheiroBRL(10)
    m2 = DinheiroBRL(20)

    assert m1 < m2
    assert m1 <= m2
    assert m2 > m1
    assert m2 >= m1
    assert m1 == 10
    assert m1 == "10,00"
    assert m1 != m2


def test_money_invalid():
    with pytest.raises(MoneyInvalidError):
        DinheiroBRL("abc")


def test_money_pydantic():
    item = OrderItem(preco="R$ 1.999,90")
    assert item.preco.centavos == 199990
    assert item.model_dump() == {"preco": 1999.9}

    with pytest.raises(ValidationError):
        OrderItem(preco="invalid")
