import pytest
from pydantic import BaseModel, ValidationError

from pydantic_brasil.cep import CEP
from pydantic_brasil.exceptions import CEPInvalidError


class AddressModel(BaseModel):
    cep: CEP


def test_cep_valid():
    cep = CEP("01310-100")
    assert cep.digits == "01310100"
    assert cep.formatted == "01310-100"
    assert cep.masked == "01310-***"
    assert cep.state == "SP"


def test_cep_valid_unpunctuated():
    cep = CEP("01310100")
    assert cep.digits == "01310100"
    assert cep.formatted == "01310-100"


def test_cep_states_mapping():
    # RJ range (20000 to 28999)
    rj_cep = CEP("20040002")
    assert rj_cep.state == "RJ"

    # MG range (30000 to 39999)
    mg_cep = CEP("30130000")
    assert mg_cep.state == "MG"

    # RS range (90000 to 99999)
    rs_cep = CEP("90010000")
    assert rs_cep.state == "RS"


def test_cep_invalid_length():
    with pytest.raises(CEPInvalidError, match="deve conter exatamente 8 dígitos"):
        CEP("12345")

    with pytest.raises(CEPInvalidError):
        CEP("123456789")


def test_cep_generate():
    sp_cep = CEP.generate(state="SP")
    assert sp_cep.state == "SP"

    rj_cep = CEP.generate(state="RJ", formatted=True)
    assert rj_cep.state == "RJ"
    assert "-" in str(rj_cep)

    with pytest.raises(ValueError, match="Estado .* desconhecido"):
        CEP.generate(state="ZZ")


def test_cep_pydantic():
    m = AddressModel(cep="01310-100")
    assert m.cep.digits == "01310100"
    assert m.model_dump() == {"cep": "01310100"}

    with pytest.raises(ValidationError):
        AddressModel(cep="123")
