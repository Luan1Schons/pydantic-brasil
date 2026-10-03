import pytest
from pydantic import BaseModel, ValidationError

from pydantic_brasil.cpf import CPF
from pydantic_brasil.cnpj import CNPJ
from pydantic_brasil.exceptions import PixKeyInvalidError
from pydantic_brasil.pix import ChavePIX, PixKey, PixKeyType


class PixReceiver(BaseModel):
    pix: ChavePIX


def test_pix_alias():
    assert PixKey == ChavePIX


def test_pix_cpf():
    cpf = CPF.generate()
    key = ChavePIX(cpf.formatted)
    assert key.key_type == PixKeyType.CPF
    assert key.normalized == cpf.digits
    assert key.formatted == cpf.formatted


def test_pix_cnpj():
    cnpj = CNPJ.generate()
    key = ChavePIX(cnpj.formatted)
    assert key.key_type == PixKeyType.CNPJ
    assert key.normalized == cnpj.digits


def test_pix_email():
    key = ChavePIX("contato@empresa.com.br")
    assert key.key_type == PixKeyType.EMAIL
    assert key.normalized == "contato@empresa.com.br"
    assert "***" in key.masked


def test_pix_phone():
    key = ChavePIX("(11) 98765-4321")
    assert key.key_type == PixKeyType.PHONE
    assert key.normalized == "+5511987654321"


def test_pix_evp_uuid():
    raw_uuid = "e8a78bf5-4f40-42bf-9076-2f6cfd939634"
    key = ChavePIX(raw_uuid)
    assert key.key_type == PixKeyType.EVP
    assert key.normalized == raw_uuid.lower()


def test_pix_invalid():
    with pytest.raises(PixKeyInvalidError):
        ChavePIX("not_a_valid_pix_key")


def test_pix_generate_evp():
    key = ChavePIX.generate_evp()
    assert key.key_type == PixKeyType.EVP


def test_pix_pydantic():
    m = PixReceiver(pix="usuario@teste.com")
    assert m.pix.key_type == PixKeyType.EMAIL
    assert m.model_dump() == {"pix": "usuario@teste.com"}

    with pytest.raises(ValidationError):
        PixReceiver(pix="invalido")
