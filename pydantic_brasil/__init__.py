"""pydantic-brasil: Modern, high-performance Brazilian data types and validators for Pydantic v2."""

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.cep import CEP
from pydantic_brasil.cnpj import CNPJ
from pydantic_brasil.cpf import CPF
from pydantic_brasil.document import CPFouCNPJ, DocumentoBR
from pydantic_brasil.exceptions import (
    BrazilianValidationError,
    CEPInvalidError,
    CNHInvalidError,
    CNPJInvalidError,
    CPFInvalidError,
    MoneyInvalidError,
    PhoneInvalidError,
    PixKeyInvalidError,
    RenavamInvalidError,
    StateRegistrationInvalidError,
    VehiclePlateInvalidError,
)
from pydantic_brasil.inscricao_estadual import InscricaoEstadual
from pydantic_brasil.money import BRL, DinheiroBRL
from pydantic_brasil.phone import TelefoneBR
from pydantic_brasil.pix import ChavePIX, PixKey, PixKeyType
from pydantic_brasil.vehicles import CNH, RENAVAM, PlacaVeiculo

__version__ = "0.1.0"

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
]
