from pydantic import BaseModel, ValidationError
import pytest

from pydantic_brasil import (
    IBAN,
    IBANBrasil,
    IBANInvalidError,
)


class WireTransfer(BaseModel):
    iban: IBANBrasil


def test_iban_valid_generation_and_metadata():
    iban = IBANBrasil.generate(
        ispb="00000000",
        agencia=1,
        conta=123456,
        tipo_conta="C",
        titularidade="1",
        formatted=False,
    )
    assert len(iban) == 29
    assert iban.country_code == "BR"
    assert iban.ispb == "00000000"
    assert iban.agencia == "00001"
    assert iban.conta == "0000123456"
    assert iban.tipo_conta == "C"
    assert iban.titularidade == "1"
    assert iban.banco is not None
    assert iban.banco.code == "001"
    assert " " in iban.formatted
    assert "****" in iban.masked


def test_iban_alias():
    assert IBAN == IBANBrasil


def test_iban_formatted_input():
    valid = IBANBrasil.generate(formatted=True)
    iban_obj = IBANBrasil(str(valid))
    assert iban_obj.country_code == "BR"
    assert iban_obj.digits == valid.digits


def test_iban_invalid_length():
    with pytest.raises(IBANInvalidError, match="deve ter exatamente 29 caracteres"):
        IBANBrasil("BR123456")


def test_iban_invalid_country():
    with pytest.raises(IBANInvalidError, match="deve iniciar com o código de país 'BR'"):
        IBANBrasil("US12" + "0" * 25)


def test_iban_invalid_checksum():
    valid = IBANBrasil.generate(formatted=False)
    # Change check digits
    wrong_cd = "00" if valid[2:4] != "00" else "01"
    corrupt_iban = f"BR{wrong_cd}{valid[4:]}"
    with pytest.raises(IBANInvalidError, match="Dígitos verificadores do IBAN inválidos"):
        IBANBrasil(corrupt_iban)


def test_iban_pydantic_integration():
    valid = IBANBrasil.generate()
    transfer = WireTransfer(iban=valid.formatted)
    assert transfer.iban == valid
    assert transfer.model_dump() == {"iban": str(valid).replace(" ", "")}

    with pytest.raises(ValidationError):
        WireTransfer(iban="INVALID_IBAN")
