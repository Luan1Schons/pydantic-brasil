from pydantic import BaseModel, ValidationError
import pytest

from pydantic_brasil import Certidao, CertidaoCivil, CertidaoCivilInvalidError


class RegistryEntry(BaseModel):
    subject: str
    certificate: CertidaoCivil


def test_certidao_civil_valid_and_metadata() -> None:
    c = CertidaoCivil.generate(record_type="55", year=2024, formatted=True)
    assert len(c.digits) == 32
    assert c.year == 2024
    assert c.type_code == "55"
    assert c.type_name == "Nascimento"
    assert len(c.cartorio_cns) == 6
    assert "." in c.formatted
    assert "-" in c.formatted
    assert "*" in c.masked

    # Alias check
    alias = Certidao(c.digits)
    assert alias == c


def test_certidao_civil_pydantic() -> None:
    c = CertidaoCivil.generate()
    entry = RegistryEntry(subject="Certidão de Registro", certificate=c)
    assert entry.certificate.digits == c.digits
    assert entry.model_dump()["certificate"] == c.digits


def test_certidao_civil_invalid_length() -> None:
    with pytest.raises(CertidaoCivilInvalidError):
        CertidaoCivil("123456789")


def test_certidao_civil_invalid_checksum() -> None:
    c = CertidaoCivil.generate()
    bad_dv = "00" if c.digits[30:] != "00" else "11"
    bad_cert = c.digits[:30] + bad_dv
    with pytest.raises(CertidaoCivilInvalidError):
        CertidaoCivil(bad_cert)


def test_certidao_civil_pydantic_invalid() -> None:
    with pytest.raises(ValidationError):
        RegistryEntry(subject="Erro", certificate="00000000000000000000000000000000")
