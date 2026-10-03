"""pydantic-brasil: Tipos de dados e validadores brasileiros para Pydantic v2."""

from pydantic_brasil.banco import BancoBR, CodigoBanco
from pydantic_brasil.base import BrazilianType
from pydantic_brasil.cep import CEP
from pydantic_brasil.certidao import Certidao, CertidaoCivil
from pydantic_brasil.cnpj import CNPJ
from pydantic_brasil.cns import CNS, CartaoSUS
from pydantic_brasil.cpf import CPF
from pydantic_brasil.document import CPFouCNPJ, DocumentoBR
from pydantic_brasil.exceptions import (
    BankCodeInvalidError,
    BrazilianValidationError,
    CEPInvalidError,
    CertidaoCivilInvalidError,
    CNHInvalidError,
    CNPJInvalidError,
    CNSInvalidError,
    CPFInvalidError,
    MoneyInvalidError,
    PhoneInvalidError,
    PISInvalidError,
    PixKeyInvalidError,
    ProcessoCNJInvalidError,
    RenavamInvalidError,
    StateRegistrationInvalidError,
    TituloEleitorInvalidError,
    VehiclePlateInvalidError,
)
from pydantic_brasil.inscricao_estadual import InscricaoEstadual
from pydantic_brasil.money import BRL, DinheiroBRL
from pydantic_brasil.phone import TelefoneBR
from pydantic_brasil.pis import NIS, NIT, PASEP, PIS
from pydantic_brasil.pix import ChavePIX, PixKey, PixKeyType
from pydantic_brasil.processo_cnj import ProcessoCNJ, ProcessoJudicial
from pydantic_brasil.titulo_eleitor import TituloEleitor, TituloEleitoral
from pydantic_brasil.vehicles import CNH, RENAVAM, PlacaVeiculo

__version__ = "0.2.0"

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
    # Fiscal
    "InscricaoEstadual",
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
]
