from pydantic import BaseModel, ValidationError
import pytest

from pydantic_brasil import (
    ChaveAcessoNFe,
    ChaveDFe,
    ChaveDFeInvalidError,
    ChaveNFe,
)


class InvoiceModel(BaseModel):
    chave: ChaveDFe


def test_dfe_valid_and_metadata():
    chave = ChaveDFe.generate(
        uf="SP",
        year=24,
        month=10,
        modelo="55",
        serie=1,
        numero=123456,
        formatted=False,
    )
    assert len(chave.digits) == 44
    assert chave.uf == "SP"
    assert chave.uf_code == 35
    assert chave.year == 2024
    assert chave.month == 10
    assert chave.ano_mes == "2410"
    assert chave.modelo == "55"
    assert "NF-e" in chave.modelo_nome
    assert chave.serie == "001"
    assert chave.numero == "000123456"
    assert chave.tipo_emissao == "1"
    assert len(chave.dv) == 1
    assert " " in chave.formatted
    assert "****" in chave.masked
    assert chave.cnpj_emitente.digits


def test_dfe_aliases():
    assert ChaveAcessoNFe == ChaveDFe
    assert ChaveNFe == ChaveDFe


def test_dfe_formatted_input():
    valid = ChaveDFe.generate()
    chave_from_fmt = ChaveDFe(valid.formatted)
    assert chave_from_fmt == valid
    assert chave_from_fmt.digits == valid.digits


def test_dfe_invalid_length():
    with pytest.raises(ChaveDFeInvalidError, match="deve conter exatamente 44 dígitos"):
        ChaveDFe("352410")


def test_dfe_repeated_digits():
    with pytest.raises(ChaveDFeInvalidError, match="não pode conter todos os dígitos iguais"):
        ChaveDFe("1" * 44)


def test_dfe_invalid_uf():
    # 99 is not a valid IBGE UF code
    with pytest.raises(ChaveDFeInvalidError, match="Código de UF '99' inválido"):
        ChaveDFe("99" + "0" * 41 + "1")


def test_dfe_invalid_checksum():
    valid = ChaveDFe.generate()
    wrong_last = str((int(valid.digits[-1]) + 1) % 10)
    bad_key = valid.digits[:-1] + wrong_last
    with pytest.raises(ChaveDFeInvalidError, match="Dígito verificador inválido"):
        ChaveDFe(bad_key)


def test_dfe_pydantic_integration():
    valid = ChaveDFe.generate()
    model = InvoiceModel(chave=valid.formatted)
    assert model.chave.digits == valid.digits
    assert model.model_dump() == {"chave": valid.digits}

    with pytest.raises(ValidationError):
        InvoiceModel(chave="invalido")
