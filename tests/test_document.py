import pytest
from pydantic import BaseModel, ValidationError

from pydantic_brasil.cnpj import CNPJ
from pydantic_brasil.cpf import CPF
from pydantic_brasil.document import CPFouCNPJ, DocumentoBR
from pydantic_brasil.exceptions import BrazilianValidationError


class BillingCustomer(BaseModel):
    document: CPFouCNPJ


def test_documento_br_alias():
    assert DocumentoBR == CPFouCNPJ


def test_cpf_or_cnpj_with_cpf():
    valid_cpf = CPF.generate()
    doc = CPFouCNPJ(valid_cpf.digits)
    assert doc.is_cpf is True
    assert doc.is_cnpj is False
    assert doc.digits == valid_cpf.digits
    assert doc.as_cpf() == valid_cpf

    with pytest.raises(ValueError, match="is a CPF, not a CNPJ"):
        doc.as_cnpj()


def test_cpf_or_cnpj_with_cnpj():
    valid_cnpj = CNPJ.generate()
    doc = CPFouCNPJ(valid_cnpj.digits)
    assert doc.is_cnpj is True
    assert doc.is_cpf is False
    assert doc.digits == valid_cnpj.digits
    assert doc.as_cnpj() == valid_cnpj

    with pytest.raises(ValueError, match="is a CNPJ, not a CPF"):
        doc.as_cpf()


def test_cpf_or_cnpj_invalid():
    with pytest.raises(BrazilianValidationError):
        CPFouCNPJ("12345678")


def test_cpf_or_cnpj_pydantic():
    cpf = CPF.generate()
    cnpj = CNPJ.generate()

    m1 = BillingCustomer(document=cpf.digits)
    assert m1.document.is_cpf is True

    m2 = BillingCustomer(document=cnpj.digits)
    assert m2.document.is_cnpj is True

    with pytest.raises(ValidationError):
        BillingCustomer(document="000.000.000-00")
