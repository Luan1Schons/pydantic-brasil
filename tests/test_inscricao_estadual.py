import pytest
from pydantic import BaseModel, ValidationError

from pydantic_brasil.exceptions import StateRegistrationInvalidError
from pydantic_brasil.inscricao_estadual import InscricaoEstadual


class CompanyTax(BaseModel):
    ie: InscricaoEstadual


def test_ie_isento():
    ie = InscricaoEstadual("ISENTO")
    assert ie.is_isento is True
    assert ie.formatted == "ISENTO"
    assert ie.masked == "ISENTO"


def test_ie_sp():
    ie = InscricaoEstadual("110.042.490.114", uf="SP")
    assert ie.is_isento is False
    assert ie.uf == "SP"
    assert ie.digits == "110042490114"

    with pytest.raises(StateRegistrationInvalidError):
        InscricaoEstadual("110.042.490.999", uf="SP")


def test_ie_rj():
    ie = InscricaoEstadual("78.040.602", uf="RJ")
    assert ie.uf == "RJ"
    assert ie.digits == "78040602"

    with pytest.raises(StateRegistrationInvalidError):
        InscricaoEstadual("78.040.609", uf="RJ")


def test_ie_rs():
    ie = InscricaoEstadual("2243658792", uf="RS")
    assert ie.uf == "RS"
    assert ie.digits == "2243658792"

    with pytest.raises(StateRegistrationInvalidError):
        InscricaoEstadual("2243658790", uf="RS")


def test_ie_generic_fallback():
    ie = InscricaoEstadual("1234567890", uf="TO")
    assert ie.uf == "TO"
    assert ie.digits == "1234567890"

    with pytest.raises(StateRegistrationInvalidError):
        InscricaoEstadual("123", uf="TO")


def test_ie_pydantic():
    m = CompanyTax(ie="ISENTO")
    assert m.ie.is_isento is True

    m2 = CompanyTax(ie="110042490114")
    assert m2.ie.digits == "110042490114"

    with pytest.raises(ValidationError):
        CompanyTax(ie="123")
