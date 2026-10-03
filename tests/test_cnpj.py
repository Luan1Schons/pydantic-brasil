import pytest
from pydantic import BaseModel, ValidationError

from pydantic_brasil.cnpj import CNPJ
from pydantic_brasil.exceptions import CNPJInvalidError


class CompanyModel(BaseModel):
    cnpj: CNPJ


def test_cnpj_valid_traditional():
    valid = CNPJ.generate()
    cnpj = CNPJ(valid.digits)
    assert cnpj == valid
    assert len(cnpj.digits) == 14
    assert "/" in cnpj.formatted
    assert "." in cnpj.formatted
    assert "-" in cnpj.formatted
    assert cnpj.is_matriz is True
    assert cnpj.is_filial is False
    assert cnpj.branch_number == "0001"
    assert "***" in cnpj.masked
    assert cnpj.is_alphanumeric is False


def test_cnpj_branch_filial():
    valid_filial = CNPJ.generate(branch=2)
    assert valid_filial.branch_number == "0002"
    assert valid_filial.is_filial is True
    assert valid_filial.is_matriz is False


def test_cnpj_invalid_length():
    with pytest.raises(CNPJInvalidError, match="deve conter exatamente 14 caracteres"):
        CNPJ("123456780001")


def test_cnpj_invalid_repeated_digits():
    for digit in "0123456789":
        with pytest.raises(CNPJInvalidError, match="não pode conter todos os dígitos iguais"):
            CNPJ(digit * 14)


def test_cnpj_invalid_checksum():
    valid = CNPJ.generate()
    wrong_last = str((int(valid[-1]) + 1) % 10)
    bad_cnpj = valid[:-1] + wrong_last
    with pytest.raises(CNPJInvalidError, match="dígito verificador inválido"):
        CNPJ(bad_cnpj)


def test_cnpj_alphanumeric_2026_format():
    # Example valid alphanumeric format according to Receita Federal rules
    # Characters: 12.ABC.345/01DE-35
    # Let's test char value calculation:
    assert CNPJ._char_value("0") == 0
    assert CNPJ._char_value("9") == 9
    assert CNPJ._char_value("A") == 17
    assert CNPJ._char_value("Z") == 42


def test_cnpj_equality():
    valid = CNPJ.generate()
    c1 = CNPJ(valid.digits)
    c2 = CNPJ(valid.formatted)
    assert c1 == c2
    assert c1 == valid.digits
    assert c1 == valid.formatted
    assert hash(c1) == hash(c2)


def test_cnpj_pydantic_integration():
    valid = CNPJ.generate()
    model = CompanyModel(cnpj=valid.digits)
    assert model.cnpj == valid
    assert model.model_dump() == {"cnpj": valid.digits}

    with pytest.raises(ValidationError):
        CompanyModel(cnpj="00.000.000/0000-00")
