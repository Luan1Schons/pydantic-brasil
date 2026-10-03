from pydantic import BaseModel, ValidationError
import pytest

from pydantic_brasil import ProcessoCNJ, ProcessoJudicial, ProcessoCNJInvalidError


class Lawsuit(BaseModel):
    title: str
    lawsuit_number: ProcessoCNJ


def test_processo_cnj_valid_and_metadata() -> None:
    p = ProcessoCNJ.generate(year=2024, segment=8, tribunal=26, origin=100, formatted=True)
    assert len(p.digits) == 20
    assert p.year == 2024
    assert p.segment_id == 8
    assert "Justiça dos Estados" in p.segment_name
    assert p.tribunal == "26"
    assert p.origin == "0100"
    assert "-" in p.formatted
    assert "." in p.formatted
    assert "*" in p.masked

    # Alias check
    alias = ProcessoJudicial(p.digits)
    assert alias == p


def test_processo_cnj_pydantic() -> None:
    p = ProcessoCNJ.generate()
    lawsuit = Lawsuit(title="Ação Ordinária", lawsuit_number=p)
    assert lawsuit.lawsuit_number.digits == p.digits
    assert lawsuit.model_dump()["lawsuit_number"] == p.digits


def test_processo_cnj_invalid_length() -> None:
    with pytest.raises(ProcessoCNJInvalidError):
        ProcessoCNJ("123456789")


def test_processo_cnj_invalid_segment() -> None:
    # 0 is invalid segment
    p = ProcessoCNJ.generate()
    bad_segment = p.digits[:13] + "0" + p.digits[14:]
    with pytest.raises(ProcessoCNJInvalidError):
        ProcessoCNJ(bad_segment)


def test_processo_cnj_invalid_checksum() -> None:
    p = ProcessoCNJ.generate()
    # Invert check digits
    bad_dv = "00" if p.digits[7:9] != "00" else "99"
    bad_proc = p.digits[:7] + bad_dv + p.digits[9:]
    with pytest.raises(ProcessoCNJInvalidError):
        ProcessoCNJ(bad_proc)


def test_processo_cnj_pydantic_invalid() -> None:
    with pytest.raises(ValidationError):
        Lawsuit(title="Erro", lawsuit_number="00000000000000000000")
