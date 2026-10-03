"""pydantic-brasil: Tipos de dados e validadores brasileiros para Pydantic v2."""

from pydantic_brasil.banco import BancoBR, CodigoBanco
from pydantic_brasil.base import BrazilianType
from pydantic_brasil.boleto import BoletoBancario, CodigoBarrasBoleto, LinhaDigitavel
from pydantic_brasil.cep import CEP
from pydantic_brasil.certidao import Certidao, CertidaoCivil
from pydantic_brasil.cnpj import CNPJ
from pydantic_brasil.cns import CNS, CartaoSUS
from pydantic_brasil.cpf import CPF
from pydantic_brasil.dfe import ChaveAcessoNFe, ChaveDFe, ChaveNFe
from pydantic_brasil.document import CPFouCNPJ, DocumentoBR
from pydantic_brasil.exceptions import (
    BankCodeInvalidError,
    BoletoInvalidError,
    BrazilianValidationError,
    CAEPFInvalidError,
    CEPInvalidError,
    CertidaoCivilInvalidError,
    ChaveDFeInvalidError,
    CNHInvalidError,
    CNPJInvalidError,
    CNSInvalidError,
    CPFInvalidError,
    GTINInvalidError,
    IBANInvalidError,
    MoneyInvalidError,
    PhoneInvalidError,
    PISInvalidError,
    PixKeyInvalidError,
    ProcessoCNJInvalidError,
    RastreioInvalidError,
    RenavamInvalidError,
    StateRegistrationInvalidError,
    TituloEleitorInvalidError,
    VehiclePlateInvalidError,
)
from pydantic_brasil.gtin import EAN, EAN13, GTIN
from pydantic_brasil.iban import IBAN, IBANBrasil
from pydantic_brasil.inscricao_estadual import InscricaoEstadual
from pydantic_brasil.money import BRL, DinheiroBRL
from pydantic_brasil.phone import TelefoneBR
from pydantic_brasil.pis import NIS, NIT, PASEP, PIS
from pydantic_brasil.pix import ChavePIX, PixKey, PixKeyType
from pydantic_brasil.processo_cnj import ProcessoCNJ, ProcessoJudicial
from pydantic_brasil.rastreio import CodigoRastreio, RastreioCorreios
from pydantic_brasil.titulo_eleitor import TituloEleitor, TituloEleitoral
from pydantic_brasil.vehicles import CNH, RENAVAM, PlacaVeiculo

__version__ = "0.3.0"

__all__ = [
    # Core Base
    "BrazilianType",
    # Taxpayer Documents
    "CPF",
    "CNPJ",
    "CPFouCNPJ",
    "DocumentoBR",
    # Address & Communication
    "CEP",
    "TelefoneBR",
    # Payments & Banking
    "ChavePIX",
    "PixKey",
    "PixKeyType",
    "DinheiroBRL",
    "BRL",
    "BancoBR",
    "CodigoBanco",
    "BoletoBancario",
    "LinhaDigitavel",
    "CodigoBarrasBoleto",
    "IBANBrasil",
    "IBAN",
    # Fiscal & Commerce
    "ChaveDFe",
    "ChaveAcessoNFe",
    "ChaveNFe",
    "InscricaoEstadual",
    "GTIN",
    "EAN",
    "EAN13",
    # Logistics
    "RastreioCorreios",
    "CodigoRastreio",
    # Labor & Social
    "PIS",
    "PASEP",
    "NIS",
    "NIT",
    # Health & Vital Records
    "CNS",
    "CartaoSUS",
    "CertidaoCivil",
    "Certidao",
    # Civic & Legal
    "TituloEleitor",
    "TituloEleitoral",
    "ProcessoCNJ",
    "ProcessoJudicial",
    # Vehicles & Transit
    "PlacaVeiculo",
    "RENAVAM",
    "CNH",
    # Exceptions
    "BrazilianValidationError",
    "CPFInvalidError",
    "CNPJInvalidError",
    "CEPInvalidError",
    "PhoneInvalidError",
    "PixKeyInvalidError",
    "VehiclePlateInvalidError",
    "RenavamInvalidError",
    "CNHInvalidError",
    "StateRegistrationInvalidError",
    "MoneyInvalidError",
    "PISInvalidError",
    "TituloEleitorInvalidError",
    "CNSInvalidError",
    "ProcessoCNJInvalidError",
    "CertidaoCivilInvalidError",
    "BankCodeInvalidError",
    "ChaveDFeInvalidError",
    "BoletoInvalidError",
    "RastreioInvalidError",
    "CAEPFInvalidError",
    "GTINInvalidError",
    "IBANInvalidError",
]
