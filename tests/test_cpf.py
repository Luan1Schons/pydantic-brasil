import pytest
from pydantic import BaseModel, ValidationError

from pydantic_brasil.cpf import CPF
from pydantic_brasil.exceptions import CPFInvalidError


class UserCPF(BaseModel):
    cpf: CPF


def test_cpf_valid_unpunctuated():
    valid_cpf = CPF.generate()
    cpf_obj = CPF(valid_cpf.digits)
    assert cpf_obj == valid_cpf
    assert len(cpf_obj.digits) == 11
    assert "." in cpf_obj.formatted
    assert "-" in cpf_obj.formatted
    assert "***" in cpf_obj.masked


def test_cpf_valid_punctuated():
    valid_cpf = CPF.generate(formatted=True)
    cpf_obj = CPF(str(valid_cpf))
    assert cpf_obj.digits == valid_cpf.digits
    assert cpf_obj.formatted == str(valid_cpf)


def test_cpf_invalid_length():
    with pytest.raises(CPFInvalidError, match="must have exactly 11 numerical digits"):
        CPF("123456789")


def test_cpf_invalid_repeated_digits():
    for digit in "0123456789":
        with pytest.raises(
            CPFInvalidError, match="cannot be composed of identical repeated digits"
        ):
            CPF(digit * 11)


def test_cpf_invalid_checksum():
    # Valid CPF with last digit changed
    valid = CPF.generate()
    wrong_last_digit = str((int(valid.digits[-1]) + 1) % 10)
    bad_cpf = valid.digits[:-1] + wrong_last_digit
    with pytest.raises(CPFInvalidError, match="Invalid CPF checksum"):
        CPF(bad_cpf)


def test_cpf_fiscal_region():
    # Generate for SP (region 8)
    sp_cpf = CPF.generate(state="SP")
    assert sp_cpf.digits[8] == "8"
    assert "SP" in sp_cpf.fiscal_region

    # Generate for RS (region 0)
    rs_cpf = CPF.generate(state="RS")
    assert rs_cpf.digits[8] == "0"
    assert "RS" in rs_cpf.fiscal_region

    # Integer region
    mg_cpf = CPF.generate(state=6)
    assert mg_cpf.digits[8] == "6"
    assert "MG" in mg_cpf.fiscal_region


def test_cpf_pydantic_model_valid():
    valid = CPF.generate()
    user = UserCPF(cpf=valid.digits)
    assert user.cpf == valid
    assert user.model_dump() == {"cpf": valid.digits}


def test_cpf_pydantic_model_invalid():
    with pytest.raises(ValidationError):
        UserCPF(cpf="111.111.111-11")


def test_cpf_equality_and_hash():
    valid = CPF.generate()
    cpf_1 = CPF(valid.digits)
    cpf_2 = CPF(valid.formatted)
    assert cpf_1 == cpf_2
    assert cpf_1 == valid.digits
    assert cpf_1 == valid.formatted
    assert hash(cpf_1) == hash(cpf_2)


def test_cpf_generate_unknown_state():
    with pytest.raises(ValueError, match="Unknown Brazilian state"):
        CPF.generate(state="XX")

    with pytest.raises(ValueError, match="State digit must be between 0 and 9"):
        CPF.generate(state=15)
