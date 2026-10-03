from pydantic import BaseModel, ValidationError
import pytest

from pydantic_brasil import CNS, CartaoSUS, CNSInvalidError


class Patient(BaseModel):
    name: str
    cns: CNS


def test_cns_definitivo() -> None:
    cns = CNS.generate(definitivo=True, formatted=True)
    assert len(cns.digits) == 15
    assert cns.is_definitivo is True
    assert cns.is_provisorio is False
    assert cns.digits[0] in ("1", "2")
    assert " " in cns.formatted
    assert "*" in cns.masked

    # Alias check
    alias = CartaoSUS(cns.digits)
    assert alias == cns


def test_cns_provisorio() -> None:
    cns = CNS.generate(definitivo=False)
    assert len(cns.digits) == 15
    assert cns.is_definitivo is False
    assert cns.is_provisorio is True
    assert cns.digits[0] in ("7", "8", "9")


def test_cns_pydantic() -> None:
    cns = CNS.generate(definitivo=True)
    patient = Patient(name="Paciente Teste", cns=cns)
    assert patient.cns.digits == cns.digits
    assert patient.model_dump()["cns"] == cns.digits


def test_cns_invalid_first_digit() -> None:
    with pytest.raises(CNSInvalidError):
        CNS("300000000000000")  # starts with 3, not allowed


def test_cns_invalid_length() -> None:
    with pytest.raises(CNSInvalidError):
        CNS("123456789")


def test_cns_invalid_checksum() -> None:
    cns = CNS.generate(definitivo=True)
    bad_dv = "0" if cns.digits[-1] != "0" else "1"
    bad_cns = cns.digits[:-1] + bad_dv
    with pytest.raises(CNSInvalidError):
        CNS(bad_cns)


def test_cns_pydantic_invalid() -> None:
    with pytest.raises(ValidationError):
        Patient(name="Erro", cns="100000000000000")
