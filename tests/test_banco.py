from pydantic import BaseModel, ValidationError
import pytest

from pydantic_brasil import BancoBR, CodigoBanco, BankCodeInvalidError


class BankAccount(BaseModel):
    holder: str
    bank: BancoBR


def test_banco_by_code() -> None:
    bb = BancoBR("001")
    assert bb.code == "001"
    assert "Banco do Brasil" in bb.name
    assert bb.short_name == "Banco do Brasil"
    assert bb.ispb == "00000000"
    assert bb.formatted == "001 - Banco do Brasil"

    # Numeric padding
    bb_int = BancoBR(1)
    assert bb_int == bb


def test_banco_by_name() -> None:
    nu = BancoBR("Nubank")
    assert nu.code == "260"
    assert nu.short_name == "Nubank"
    assert nu.ispb == "18236120"

    itau = BancoBR("Itaú")
    assert itau.code == "341"


def test_banco_search() -> None:
    results = BancoBR.search("Caixa")
    assert len(results) >= 1
    assert results[0].code == "104"

    results_ispb = BancoBR.search("18236120")
    assert any(b.code == "260" for b in results_ispb)


def test_banco_alias() -> None:
    b1 = BancoBR("033")
    b2 = CodigoBanco("033")
    assert b1 == b2
    assert b1.short_name == "Santander"


def test_banco_pydantic() -> None:
    account = BankAccount(holder="João", bank="260")
    assert account.bank.code == "260"
    assert account.model_dump()["bank"] == "260"


def test_banco_invalid() -> None:
    with pytest.raises(BankCodeInvalidError):
        BancoBR("999")  # unassigned code

    with pytest.raises(BankCodeInvalidError):
        BancoBR("Banco Inexistente XYZ 123")


def test_banco_pydantic_invalid() -> None:
    with pytest.raises(ValidationError):
        BankAccount(holder="Erro", bank="999")
