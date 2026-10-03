from pydantic import BaseModel, ValidationError
import pytest

from pydantic_brasil import NIS, NIT, PASEP, PIS, PISInvalidError


class Employee(BaseModel):
    name: str
    pis: PIS


def test_pis_valid_and_aliases() -> None:
    # Generate and validate
    gen = PIS.generate(formatted=True)
    assert len(gen.digits) == 11
    assert "." in gen.formatted
    assert "-" in gen.formatted
    assert "*" in gen.masked

    # Aliases
    p1 = PIS(gen.digits)
    p2 = PASEP(gen.digits)
    p3 = NIS(gen.digits)
    p4 = NIT(gen.digits)

    assert p1 == p2 == p3 == p4
    assert p1.digits == p2.digits


def test_pis_pydantic_model() -> None:
    valid_pis = PIS.generate()
    emp = Employee(name="Carlos Lima", pis=valid_pis)
    assert emp.pis.digits == valid_pis.digits

    # Serialization to unpunctuated digits
    dumped = emp.model_dump()
    assert dumped["pis"] == valid_pis.digits


def test_pis_invalid_length() -> None:
    with pytest.raises(PISInvalidError):
        PIS("123456789")


def test_pis_invalid_repeated_digits() -> None:
    with pytest.raises(PISInvalidError):
        PIS("11111111111")


def test_pis_invalid_checksum() -> None:
    gen = PIS.generate()
    # Invert check digit
    wrong_dv = "0" if gen.digits[-1] != "0" else "1"
    bad_pis = gen.digits[:-1] + wrong_dv
    with pytest.raises(PISInvalidError):
        PIS(bad_pis)


def test_pis_pydantic_invalid() -> None:
    with pytest.raises(ValidationError):
        Employee(name="Erro", pis="000.00000.00-0")
