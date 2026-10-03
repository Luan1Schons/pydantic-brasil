import pytest
from pydantic import BaseModel, ValidationError

from pydantic_brasil.exceptions import (
    CNHInvalidError,
    RenavamInvalidError,
    VehiclePlateInvalidError,
)
from pydantic_brasil.vehicles import CNH, RENAVAM, PlacaVeiculo


class VehicleModel(BaseModel):
    placa: PlacaVeiculo
    renavam: RENAVAM
    cnh: CNH


def test_plate_traditional():
    p = PlacaVeiculo("ABC-1234")
    assert p.is_mercosul is False
    assert p.formatted == "ABC-1234"
    assert p.masked == "ABC-**34"

    # Convert to Mercosul: 3 -> D
    mercosul = p.to_mercosul()
    assert mercosul.is_mercosul is True
    assert str(mercosul) == "ABC1C34"


def test_plate_mercosul():
    p = PlacaVeiculo("ABC1D23")
    assert p.is_mercosul is True
    assert p.formatted == "ABC1D23"

    # Convert to traditional: D -> 3
    antiga = p.to_antiga()
    assert antiga.is_mercosul is False
    assert antiga.formatted == "ABC-1323"


def test_plate_invalid():
    with pytest.raises(VehiclePlateInvalidError):
        PlacaVeiculo("AB12345")


def test_renavam_valid():
    r = RENAVAM("00123456789")
    assert r.digits == "00123456789"
    assert "-" in r.formatted
    assert "****" in r.masked


def test_renavam_invalid():
    with pytest.raises(RenavamInvalidError):
        RENAVAM("12345")

    with pytest.raises(RenavamInvalidError):
        RENAVAM("00123456780")


def test_cnh_valid():
    c = CNH("12345678900")
    assert c.digits == "12345678900"
    assert c.formatted == "12345678900"
    assert "***" in c.masked


def test_cnh_repeated_digits():
    with pytest.raises(CNHInvalidError):
        CNH("11111111111")


def test_cnh_invalid():
    with pytest.raises(CNHInvalidError):
        CNH("12345678999")


def test_pydantic_vehicle():
    m = VehicleModel(
        placa="ABC1D23",
        renavam="00123456789",
        cnh="12345678900",
    )
    assert m.placa.is_mercosul is True
    assert m.renavam.digits == "00123456789"
    assert m.cnh.digits == "12345678900"

    with pytest.raises(ValidationError):
        VehicleModel(
            placa="INVALID",
            renavam="00123456789",
            cnh="12345678900",
        )
