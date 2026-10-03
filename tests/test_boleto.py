from pydantic import BaseModel, ValidationError
import pytest

from pydantic_brasil import (
    BoletoBancario,
    BoletoInvalidError,
    CodigoBarrasBoleto,
    LinhaDigitavel,
)


class PaymentOrder(BaseModel):
    boleto: BoletoBancario


def test_boleto_cobranca_generation_and_metadata():
    boleto = BoletoBancario.generate(banco="001", valor=150.00, formatted=True)
    assert boleto.is_arrecadacao is False
    assert len(boleto.codigo_barras) == 44
    assert boleto.codigo_banco == "001"
    assert boleto.banco is not None
    assert boleto.banco.short_name == "Banco do Brasil"
    assert boleto.valor is not None
    assert boleto.valor.centavos == 15000
    assert boleto.data_vencimento is not None
    assert "." in boleto.linha_digitavel
    assert "..." in boleto.masked


def test_boleto_aliases():
    assert LinhaDigitavel == BoletoBancario
    assert CodigoBarrasBoleto == BoletoBancario


def test_boleto_from_barcode():
    boleto_gen = BoletoBancario.generate(banco="237", valor=89.90, formatted=False)
    barcode = boleto_gen.codigo_barras
    from_barcode = BoletoBancario(barcode)
    assert from_barcode.codigo_barras == barcode
    assert from_barcode.codigo_banco == "237"
    assert from_barcode.valor is not None
    assert from_barcode.valor.centavos == 8990


def test_boleto_invalid_length():
    with pytest.raises(BoletoInvalidError):
        BoletoBancario("123456789")


def test_boleto_repeated_digits():
    with pytest.raises(BoletoInvalidError, match="não pode conter todos os dígitos iguais"):
        BoletoBancario("1" * 47)


def test_boleto_cobranca_invalid_field_dv():
    boleto = BoletoBancario.generate(formatted=False)
    ld = boleto.linha_digitavel.replace(".", "").replace(" ", "")

    # Erro campo 1
    bad_dv1 = str((int(ld[9]) + 1) % 10)
    bad_ld1 = ld[:9] + bad_dv1 + ld[10:]
    with pytest.raises(BoletoInvalidError, match="campo 1"):
        BoletoBancario(bad_ld1)

    # Erro campo 2
    bad_dv2 = str((int(ld[20]) + 1) % 10)
    bad_ld2 = ld[:20] + bad_dv2 + ld[21:]
    with pytest.raises(BoletoInvalidError, match="campo 2"):
        BoletoBancario(bad_ld2)

    # Erro campo 3
    bad_dv3 = str((int(ld[31]) + 1) % 10)
    bad_ld3 = ld[:31] + bad_dv3 + ld[32:]
    with pytest.raises(BoletoInvalidError, match="campo 3"):
        BoletoBancario(bad_ld3)

    # Erro DV geral
    bad_dv_geral = str((int(ld[32]) + 1) % 10)
    bad_ld_geral = ld[:32] + bad_dv_geral + ld[33:]
    with pytest.raises(BoletoInvalidError, match="Dígito verificador geral inválido"):
        BoletoBancario(bad_ld_geral)


def test_boleto_barcode_invalid_dv():
    boleto = BoletoBancario.generate(formatted=False)
    bc = boleto.codigo_barras
    bad_dv = "1" if bc[4] != "1" else "2"
    bad_bc = bc[:4] + bad_dv + bc[5:]
    with pytest.raises(BoletoInvalidError, match="Dígito verificador geral inválido"):
        BoletoBancario(bad_bc)


def test_boleto_arrecadacao_valid_and_barcode():
    c1 = "81600000001"
    dv1 = BoletoBancario._modulo10(c1)
    c2 = "00001234567"
    dv2 = BoletoBancario._modulo10(c2)
    c3 = "89012345678"
    dv3 = BoletoBancario._modulo10(c3)
    c4 = "90123456789"
    dv4 = BoletoBancario._modulo10(c4)
    arrecadacao_48 = f"{c1}{dv1}{c2}{dv2}{c3}{dv3}{c4}{dv4}"

    b = BoletoBancario(arrecadacao_48)
    assert b.is_arrecadacao is True
    assert b.codigo_banco is None
    assert b.banco is None
    assert b.fator_vencimento is None
    assert b.data_vencimento is None
    assert b.valor is not None
    assert len(b.codigo_barras) == 44
    assert len(b.linha_digitavel.replace(" ", "")) == 48

    # A partir do código de barras de arrecadação
    b_from_bc = BoletoBancario(b.codigo_barras)
    assert b_from_bc.is_arrecadacao is True
    assert b_from_bc.codigo_barras == b.codigo_barras
    assert len(b_from_bc.linha_digitavel.replace(" ", "")) == 48


def test_boleto_arrecadacao_invalid_block():
    c1 = "81600000001"
    dv1 = "0"  # incorreto
    c2 = "00001234567"
    dv2 = BoletoBancario._modulo10(c2)
    c3 = "89012345678"
    dv3 = BoletoBancario._modulo10(c3)
    c4 = "90123456789"
    dv4 = BoletoBancario._modulo10(c4)
    bad_48 = f"{c1}{dv1}{c2}{dv2}{c3}{dv3}{c4}{dv4}"

    with pytest.raises(BoletoInvalidError, match="Dígito verificador de bloco inválido"):
        BoletoBancario(bad_48)


def test_boleto_pydantic_integration():
    boleto = BoletoBancario.generate()
    order = PaymentOrder(boleto=boleto.linha_digitavel)
    assert order.boleto == boleto
    assert order.model_dump()["boleto"] == boleto.digits

    with pytest.raises(ValidationError):
        PaymentOrder(boleto="000")
