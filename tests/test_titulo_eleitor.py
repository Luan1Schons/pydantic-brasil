from pydantic import BaseModel, ValidationError
import pytest

from pydantic_brasil import TituloEleitor, TituloEleitoral, TituloEleitorInvalidError


class VoterSchema(BaseModel):
    name: str
    voter_id: TituloEleitor


def test_titulo_eleitor_valid_and_state() -> None:
    t_sp = TituloEleitor.generate(state="SP", formatted=True)
    assert t_sp.state == "SP"
    assert t_sp.uf_code == "01"
    assert len(t_sp.digits) == 12
    assert " " in t_sp.formatted
    assert "*" in t_sp.masked

    t_rj = TituloEleitor.generate(state="RJ")
    assert t_rj.state == "RJ"
    assert t_rj.uf_code == "03"

    # Alias
    t_alias = TituloEleitoral(t_sp.digits)
    assert t_alias == t_sp


def test_titulo_eleitor_pydantic() -> None:
    t = TituloEleitor.generate()
    voter = VoterSchema(name="Eleitor Teste", voter_id=t)
    assert voter.voter_id.digits == t.digits
    assert voter.model_dump()["voter_id"] == t.digits


def test_titulo_eleitor_invalid_length() -> None:
    with pytest.raises(TituloEleitorInvalidError):
        TituloEleitor("1234567890")


def test_titulo_eleitor_invalid_uf() -> None:
    # 99 is invalid UF code
    with pytest.raises(TituloEleitorInvalidError):
        TituloEleitor("123456789901")


def test_titulo_eleitor_invalid_checksum() -> None:
    t = TituloEleitor.generate(state="MG")
    bad_dv = "0" if t.digits[-1] != "0" else "1"
    bad_id = t.digits[:-1] + bad_dv
    with pytest.raises(TituloEleitorInvalidError):
        TituloEleitor(bad_id)


def test_titulo_eleitor_pydantic_invalid() -> None:
    with pytest.raises(ValidationError):
        VoterSchema(name="Erro", voter_id="000000000000")
