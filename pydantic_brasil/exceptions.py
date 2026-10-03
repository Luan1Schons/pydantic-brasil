"""Exceções customizadas para erros de validação em pydantic-brasil."""

from typing import Any, Optional


class BrazilianValidationError(ValueError):
    """Exceção base para erros de validação de documentos e tipos brasileiros."""

    def __init__(self, message: str, value: Optional[Any] = None) -> None:
        super().__init__(message)
        self.message = message
        self.value = value

    def __str__(self) -> str:
        return self.message


class CPFInvalidError(BrazilianValidationError):
    """Lançada quando um CPF é inválido (tamanho incorreto, dígito verificador ou repetido)."""


class CNPJInvalidError(BrazilianValidationError):
    """Lançada quando um CNPJ é inválido (tamanho, dígito verificador ou caracteres inválidos)."""


class CEPInvalidError(BrazilianValidationError):
    """Lançada quando um CEP é inválido (deve conter 8 dígitos numéricos)."""


class PhoneInvalidError(BrazilianValidationError):
    """Lançada quando um telefone é inválido (DDD inexistente ou quantidade de dígitos)."""


class PixKeyInvalidError(BrazilianValidationError):
    """Lançada quando uma chave PIX não atende a nenhum formato oficial do Bacen."""


class VehiclePlateInvalidError(BrazilianValidationError):
    """Lançada quando uma placa veicular é inválida (nem padrão tradicional nem Mercosul)."""


class RenavamInvalidError(BrazilianValidationError):
    """Lançada quando um RENAVAM é inválido (dígito verificador ou tamanho incorreto)."""


class CNHInvalidError(BrazilianValidationError):
    """Lançada quando uma CNH é inválida (duplo dígito verificador ou tamanho incorreto)."""


class StateRegistrationInvalidError(BrazilianValidationError):
    """Lançada quando uma Inscrição Estadual é inválida para a UF especificada."""


class MoneyInvalidError(BrazilianValidationError):
    """Lançada quando uma expressão de valor monetário não pode ser convertida em BRL."""


class PISInvalidError(BrazilianValidationError):
    """Lançada quando um PIS/PASEP/NIT é inválido (tamanho, dígito ou dígitos repetidos)."""


class TituloEleitorInvalidError(BrazilianValidationError):
    """Lançada quando um Título de Eleitor é inválido (UF inexistente, DV1 ou DV2 incorretos)."""


class CNSInvalidError(BrazilianValidationError):
    """Lançada quando um Cartão Nacional de Saúde (CNS/SUS) é inválido."""


class ProcessoCNJInvalidError(BrazilianValidationError):
    """Lançada quando um processo CNJ falha na validação do Módulo 97 ou formato."""


class CertidaoCivilInvalidError(BrazilianValidationError):
    """Lançada quando uma Certidão Civil (32 dígitos) é inválida no Módulo 11."""


class BankCodeInvalidError(BrazilianValidationError):
    """Lançada quando um código COMPE de banco brasileiro não é reconhecido ou é inválido."""


class ChaveDFeInvalidError(BrazilianValidationError):
    """Lançada quando uma chave de acesso de DF-e (NF-e/NFC-e/CT-e) é inválida no Módulo 11."""


class BoletoInvalidError(BrazilianValidationError):
    """Lançada quando uma linha digitável ou código de barras de boleto é inválido."""


class RastreioInvalidError(BrazilianValidationError):
    """Lançada quando um código de rastreamento postal (S10) dos Correios é inválido."""


class CAEPFInvalidError(BrazilianValidationError):
    """Lançada quando um CAEPF é inválido em tamanho ou dígitos verificadores."""


class GTINInvalidError(BrazilianValidationError):
    """Lançada quando um código GTIN/EAN possui dígito verificador inválido."""


class IBANInvalidError(BrazilianValidationError):
    """Lançada quando um código IBAN brasileiro é inválido na regra ISO 7064 / Módulo 97."""
