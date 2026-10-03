"""Validação e formatação de Chave PIX (Banco Central do Brasil)."""

from __future__ import annotations

import re
import uuid
from enum import Enum
from typing import Any, ClassVar, Dict, Tuple, cast

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.cnpj import CNPJ
from pydantic_brasil.cpf import CPF
from pydantic_brasil.exceptions import PixKeyInvalidError
from pydantic_brasil.phone import TelefoneBR


class PixKeyType(str, Enum):
    """Categorias oficiais de Chaves PIX definidas pelo Banco Central do Brasil (Bacen)."""

    CPF = "CPF"
    CNPJ = "CNPJ"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    EVP = "EVP"  # Chave Aleatória / Endereço Virtual Pagador (UUID v4)


class ChavePIX(BrazilianType):
    """Chave PIX (Sistema de Pagamentos Instantâneos do Banco Central).

    Recursos:
    - Identificação e validação automática do formato:
      * CPF: 11 dígitos numéricos com Módulo 11.
      * CNPJ: 14 dígitos válidos.
      * E-mail: Endereço em conformidade com o padrão RFC 5322.
      * Telefone: Padrão nacional brasileiro (+55DD9XXXXXXXX ou DD9XXXXXXXX).
      * EVP: Chave aleatória em formato UUID v4.
    - `.key_type`: Retorna enum `PixKeyType`.
    - `.normalized`: Formato canônico especificado pelo Bacen.
    - `.formatted`: Formatação correspondente ao tipo da chave.
    - `.masked`: Mascaramento conforme a LGPD.
    """

    EMAIL_REGEX: ClassVar[re.Pattern[str]] = re.compile(
        r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    )
    UUID_REGEX: ClassVar[re.Pattern[str]] = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
        re.IGNORECASE,
    )

    _key_type: PixKeyType
    _normalized: str

    def __new__(cls, value: Any) -> ChavePIX:
        if isinstance(value, cls):
            return value

        cleaned = cls._clean_input(value)
        ktype, norm = cls._resolve(cleaned)

        instance = cast(ChavePIX, super().__new__(cls, norm))
        instance._key_type = ktype
        instance._normalized = norm
        instance._digits = cls._extract_digits(norm)
        return instance

    @classmethod
    def _validate(cls, value: str) -> str:
        _, norm = cls._resolve(value)
        return norm

    @classmethod
    def _resolve(cls, value: str) -> Tuple[PixKeyType, str]:
        val = value.strip()

        # 1. Check for Random Key (EVP / UUID)
        if cls.UUID_REGEX.match(val):
            return PixKeyType.EVP, val.lower()

        # 2. Check for Email
        if "@" in val and cls.EMAIL_REGEX.match(val):
            return PixKeyType.EMAIL, val.lower()

        # 3. Check for CPF (11 digits)
        digits = cls._extract_digits(val)
        if (
            (len(digits) == 11 or (val.isdigit() and len(val) <= 11))
            and not val.startswith("+55")
            and "@" not in val
        ):
            try:
                cpf = CPF(val)
                return PixKeyType.CPF, cpf.digits
            except Exception:
                pass

        # 4. Check for CNPJ (14 digits)
        if (len(digits) == 14 or "/" in val) and not val.startswith("+55") and "@" not in val:
            try:
                cnpj = CNPJ(val)
                return PixKeyType.CNPJ, cnpj.digits
            except Exception:
                pass

        # 5. Check for Phone Number
        try:
            phone = TelefoneBR(val)
            return PixKeyType.PHONE, phone.e164
        except Exception:
            pass

        raise PixKeyInvalidError(
            f"O valor '{value}' não é uma chave PIX válida "
            f"(deve ser CPF, CNPJ, E-mail, Telefone ou Chave Aleatória/UUID).",
            value=value,
        )

    @property
    def key_type(self) -> PixKeyType:
        """Retorna a categoria/tipo identificada da chave PIX."""
        return self._key_type

    @property
    def normalized(self) -> str:
        """Retorna o formato canônico estipulado pelo Banco Central."""
        return self._normalized

    @property
    def formatted(self) -> str:
        """Retorna a chave formatada de acordo com o seu tipo."""
        if self.key_type == PixKeyType.CPF:
            return CPF(self._normalized).formatted
        if self.key_type == PixKeyType.CNPJ:
            return CNPJ(self._normalized).formatted
        if self.key_type == PixKeyType.PHONE:
            return TelefoneBR(self._normalized).formatted
        return self._normalized

    @property
    def masked(self) -> str:
        """Retorna a chave mascarada de acordo com a LGPD."""
        if self.key_type == PixKeyType.CPF:
            return CPF(self._normalized).masked
        if self.key_type == PixKeyType.CNPJ:
            return CNPJ(self._normalized).masked
        if self.key_type == PixKeyType.PHONE:
            return TelefoneBR(self._normalized).masked
        if self.key_type == PixKeyType.EMAIL:
            parts = self._normalized.split("@")
            user, domain = parts[0], parts[1]
            masked_user = user[0] + "***" + (user[-1] if len(user) > 1 else "")
            return f"{masked_user}@{domain}"
        if self.key_type == PixKeyType.EVP:
            return f"{self._normalized[:8]}-****-****-****-************"
        return self._normalized

    @classmethod
    def generate_evp(cls) -> ChavePIX:
        """Gera uma chave aleatória EVP (UUID v4) válida."""
        return cls(str(uuid.uuid4()))

    @classmethod
    def openapi_schema_extra(cls) -> Dict[str, Any]:
        return {
            "type": "string",
            "title": "ChavePIX",
            "description": "Chave PIX (CPF, CNPJ, E-mail, Telefone ou EVP Aleatória)",
            "examples": [
                "12345678900",
                "+5511987654321",
                "usuario@dominio.com.br",
                "123e4567-e89b-12d3-a456-426614174000",
            ],
        }


# Alias
PixKey = ChavePIX
