from pydantic import BaseModel, ValidationError
import pytest

from pydantic_brasil import (
    CodigoRastreio,
    RastreioCorreios,
    RastreioInvalidError,
)


class DeliveryModel(BaseModel):
    rastreio: RastreioCorreios


def test_rastreio_valid_and_metadata():
    code = RastreioCorreios.generate(service="QC", country="BR")
    assert len(code) == 13
    assert code.service_code == "QC"
    assert code.origin_country == "BR"
    assert code.is_national is True
    assert "rastreamento.correios.com.br" in code.tracking_url
    assert " " in code.formatted
    assert "****" in code.masked


def test_rastreio_alias():
    assert CodigoRastreio == RastreioCorreios


def test_rastreio_known_check_digit():
    # If serial is 12345678:
    # weights: [8, 6, 4, 2, 3, 5, 9, 7]
    # sum = 1*8 + 2*6 + 3*4 + 4*2 + 5*3 + 6*5 + 7*9 + 8*7
    #     = 8 + 12 + 12 + 8 + 15 + 30 + 63 + 56 = 204
    # 204 % 11 = 6 -> dv = 11 - 6 = 5
    known = RastreioCorreios("AA123456785BR")
    assert known.dv == "5"


def test_rastreio_invalid_length():
    with pytest.raises(RastreioInvalidError, match="deve ter 13 caracteres"):
        RastreioCorreios("AA123BR")


def test_rastreio_invalid_checksum():
    with pytest.raises(RastreioInvalidError, match="Dígito verificador inválido"):
        RastreioCorreios("AA123456789BR")  # expected 5, given 9


def test_rastreio_pydantic():
    valid = RastreioCorreios.generate()
    model = DeliveryModel(rastreio=valid.formatted)
    assert model.rastreio == valid
    assert model.model_dump() == {"rastreio": str(valid)}

    with pytest.raises(ValidationError):
        DeliveryModel(rastreio="INVALID_CODE")
