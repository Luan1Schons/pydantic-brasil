from pydantic import BaseModel, ValidationError
import pytest

from pydantic_brasil import (
    EAN,
    EAN13,
    GTIN,
    GTINInvalidError,
)


class ProductItem(BaseModel):
    gtin: GTIN


def test_gtin_valid_brazilian():
    gtin13 = GTIN.generate(length=13, brazilian=True)
    assert len(gtin13.digits) == 13
    assert gtin13.is_brazilian is True
    assert gtin13.prefix in ("789", "790")
    assert gtin13.gtin_type == "GTIN-13"
    assert gtin13.dv == gtin13.digits[-1]
    assert "****" in gtin13.masked


def test_gtin_aliases():
    assert EAN == GTIN
    assert EAN13 == GTIN


def test_gtin_lengths():
    for length in (8, 12, 13, 14):
        code = GTIN.generate(length=length, brazilian=False)
        assert len(code.digits) == length
        assert code.gtin_type == f"GTIN-{length}"


def test_gtin_known_check_digit():
    # EAN-13: 789100031550 -> 7
    # 7 8 9 1 0 0 0 3 1 5 5 0
    # alternating weights 3, 1 from right:
    # 0*3 + 5*1 + 5*3 + 1*1 + 3*3 + 0*1 + 0*3 + 0*1 + 1*3 + 9*1 + 8*3 + 7*1
    # = 0 + 5 + 15 + 1 + 9 + 0 + 0 + 0 + 3 + 9 + 24 + 7 = 73
    # 73 % 10 = 3 -> 10 - 3 = 7
    valid = GTIN("7891000315507")
    assert valid.dv == "7"
    assert valid.is_brazilian is True


def test_gtin_invalid_length():
    with pytest.raises(GTINInvalidError, match="deve conter 8, 12, 13 ou 14 dígitos"):
        GTIN("1234567")


def test_gtin_repeated_digits():
    with pytest.raises(GTINInvalidError, match="não pode conter todos os dígitos iguais"):
        GTIN("2" * 13)


def test_gtin_invalid_checksum():
    with pytest.raises(GTINInvalidError, match="Dígito verificador inválido"):
        GTIN("7891000315501")  # expected 7


def test_gtin_pydantic():
    valid = GTIN.generate()
    item = ProductItem(gtin=valid.digits)
    assert item.gtin == valid
    assert item.model_dump() == {"gtin": valid.digits}

    with pytest.raises(ValidationError):
        ProductItem(gtin="123")
