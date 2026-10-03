import pytest
from pydantic import BaseModel, ValidationError

from pydantic_brasil.exceptions import PhoneInvalidError
from pydantic_brasil.phone import TelefoneBR


class ContactModel(BaseModel):
    phone: TelefoneBR


def test_mobile_phone_valid():
    phone = TelefoneBR("11987654321")
    assert phone.is_mobile is True
    assert phone.is_landline is False
    assert phone.ddd == "11"
    assert phone.number == "987654321"
    assert phone.formatted == "(11) 98765-4321"
    assert phone.e164 == "+5511987654321"
    assert "wa.me/5511987654321" in phone.whatsapp_link
    assert phone.masked == "(11) 9****-**21"


def test_landline_phone_valid():
    phone = TelefoneBR("(11) 3456-7890")
    assert phone.is_landline is True
    assert phone.is_mobile is False
    assert phone.ddd == "11"
    assert phone.number == "34567890"
    assert phone.formatted == "(11) 3456-7890"
    assert phone.e164 == "+551134567890"


def test_phone_with_country_code():
    phone = TelefoneBR("+55 11 98765-4321")
    assert phone.digits == "11987654321"


def test_phone_invalid_ddd():
    with pytest.raises(PhoneInvalidError, match="DDD .* inválido"):
        TelefoneBR("00987654321")

    with pytest.raises(PhoneInvalidError, match="DDD .* inválido"):
        TelefoneBR("20987654321")


def test_phone_invalid_mobile_digit():
    # Celular com 11 dígitos mas sem iniciar com 9
    with pytest.raises(PhoneInvalidError, match="deve iniciar com o dígito '9'"):
        TelefoneBR("11887654321")


def test_phone_invalid_length():
    with pytest.raises(PhoneInvalidError, match="deve ter 10.*ou 11.*dígitos"):
        TelefoneBR("119876")


def test_phone_generate():
    mobile = TelefoneBR.generate(ddd=11, mobile=True)
    assert mobile.is_mobile is True
    assert mobile.ddd == "11"

    landline = TelefoneBR.generate(ddd=21, mobile=False, formatted=True)
    assert landline.is_landline is True
    assert landline.ddd == "21"
    assert "(" in str(landline)


def test_phone_pydantic():
    m = ContactModel(phone="(11) 98765-4321")
    assert m.phone.digits == "11987654321"
    assert m.model_dump() == {"phone": "11987654321"}

    with pytest.raises(ValidationError):
        ContactModel(phone="1234")
