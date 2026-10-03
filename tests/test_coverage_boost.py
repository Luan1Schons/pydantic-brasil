from decimal import Decimal
import pytest
from pydantic_brasil.inscricao_estadual import (
    InscricaoEstadual,
    _validate_mg,
    _validate_pr,
    _validate_sc,
    _validate_sp,
)
from pydantic_brasil.money import DinheiroBRL
from pydantic_brasil.pix import ChavePIX, PixKeyType
from pydantic_brasil.vehicles import PlacaVeiculo
from pydantic_brasil.cpf import CPF


def test_sp_rural_producer():
    # SP rural starts with P followed by 8 digits + 1 check digit
    # Let's test P011004243
    # body = "01100424" -> weights = [1, 3, 4, 5, 6, 7, 8, 10]
    # s = 0 + 3 + 4 + 0 + 0 + 28 + 16 + 40 = 91 -> 91 % 11 = 3 -> 3 % 10 = 3
    valid_rural = "P011004243"
    assert _validate_sp(valid_rural) is True
    assert _validate_sp("P011004244") is False
    assert _validate_sp("P123") is False

    ie = InscricaoEstadual(valid_rural, uf="SP")
    assert ie.digits == "011004243"


def test_mg_inscricao_estadual():
    # MG: 062.307.904/0081 -> 0623079040081
    assert _validate_mg("0623079040081") is True
    assert _validate_mg("0623079040082") is False
    assert _validate_mg("123") is False

    ie = InscricaoEstadual("0623079040081", uf="MG")
    assert ie.uf == "MG"


def test_pr_inscricao_estadual():
    # PR: 123.45678-50 -> 1234567850
    # Let's compute valid PR IE:
    # body 8 digits: 12345678 -> weights [3, 2, 7, 6, 5, 4, 3, 2]
    # s1 = 3 + 4 + 21 + 24 + 25 + 24 + 21 + 16 = 138 % 11 = 6 -> dv1 = 11 - 6 = 5
    # body 9 digits: 123456785 -> weights [4, 3, 2, 7, 6, 5, 4, 3, 2]
    # s2 = 4 + 6 + 6 + 28 + 30 + 35 + 28 + 24 + 10 = 171 % 11 = 6 -> dv2 = 11 - 6 = 5
    valid_pr = "1234567850"
    assert _validate_pr(valid_pr) is True
    assert _validate_pr("1234567859") is False
    assert _validate_pr("123") is False

    ie = InscricaoEstadual(valid_pr, uf="PR")
    assert ie.uf == "PR"


def test_sc_inscricao_estadual():
    # SC: 9 digits -> weights [9, 8, 7, 6, 5, 4, 3, 2]
    # body 8 digits: 25100000 -> s = 18 + 40 + 7 + 0 = 65 % 11 = 10 -> dv = 11 - 10 = 1
    valid_sc = "251000001"
    assert _validate_sc(valid_sc) is True
    assert _validate_sc("251000002") is False
    assert _validate_sc("123") is False

    ie = InscricaoEstadual(valid_sc, uf="SC")
    assert ie.uf == "SC"


def test_pix_mask_and_formatting():
    # Phone key
    phone_key = ChavePIX("+5511987654321")
    assert phone_key.key_type == PixKeyType.PHONE
    assert "(11)" in phone_key.formatted
    assert "****" in phone_key.masked

    # Email key
    email_key = ChavePIX("contato@loja.com.br")
    assert email_key.formatted == "contato@loja.com.br"
    assert "c***o@loja.com.br" == email_key.masked

    # EVP key
    evp = ChavePIX.generate_evp()
    assert "-****-" in evp.masked
    assert evp.formatted == evp.normalized


def test_vehicle_conversions_edge_cases():
    mercosul = PlacaVeiculo("ABC1D23")
    # Calling to_mercosul on already Mercosul returns self
    assert mercosul.to_mercosul() == mercosul

    antiga = PlacaVeiculo("ABC-1234")
    # Calling to_antiga on already antiga returns self
    assert antiga.to_antiga() == antiga


def test_money_extra_methods():
    m = DinheiroBRL(50)
    assert abs(m) == DinheiroBRL(50)
    assert abs(DinheiroBRL(-50)) == DinheiroBRL(50)
    assert m * 2 == DinheiroBRL(100)
    assert m / 2 == DinheiroBRL(25)
    assert repr(m) == "DinheiroBRL('R$ 50,00')"
    assert hash(m) == hash(Decimal("50.00"))


def test_base_fallback_methods():
    # Test base smart equality fallback
    cpf = CPF.generate()
    assert (cpf == 12345) is False
    assert cpf.__eq__(None) is False

    with pytest.raises(TypeError, match="Valor não pode ser nulo"):
        CPF(None)


def test_ie_masked():
    ie = InscricaoEstadual("110042490114", uf="SP")
    assert "***" in ie.masked
    assert ie.is_isento is False
