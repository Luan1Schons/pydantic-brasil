"""Custom exceptions for pydantic-brasil."""

from typing import Any, Optional


class BrazilianValidationError(ValueError):
    """Base exception for Brazilian document validation errors."""

    def __init__(self, message: str, value: Optional[Any] = None) -> None:
        super().__init__(message)
        self.message = message
        self.value = value

    def __str__(self) -> str:
        return self.message


class CPFInvalidError(BrazilianValidationError):
    """Raised when a CPF is invalid (bad length, bad checksum or repeated digits)."""


class CNPJInvalidError(BrazilianValidationError):
    """Raised when a CNPJ is invalid (bad length, bad checksum or invalid characters)."""


class CEPInvalidError(BrazilianValidationError):
    """Raised when a CEP is invalid (must have 8 digits)."""


class PhoneInvalidError(BrazilianValidationError):
    """Raised when a Brazilian phone number is invalid (bad DDD or invalid digit count)."""


class PixKeyInvalidError(BrazilianValidationError):
    """Raised when a PIX key does not match any valid format (CPF, CNPJ, Email, Phone, EVP)."""


class VehiclePlateInvalidError(BrazilianValidationError):
    """Raised when a license plate is invalid (neither standard nor Mercosul)."""


class RenavamInvalidError(BrazilianValidationError):
    """Raised when a RENAVAM is invalid (bad checksum or length)."""


class CNHInvalidError(BrazilianValidationError):
    """Raised when a CNH is invalid (bad checksum or length)."""


class StateRegistrationInvalidError(BrazilianValidationError):
    """Raised when an Inscrição Estadual (IE) is invalid for the specified UF."""


class MoneyInvalidError(BrazilianValidationError):
    """Raised when a currency amount string cannot be parsed as BRL currency."""
