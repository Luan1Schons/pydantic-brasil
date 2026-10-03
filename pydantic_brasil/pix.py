"""Chave PIX (Brazilian Instant Payment Key) validation and formatting."""

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
    """Categorization of Brazilian PIX Keys defined by the Central Bank of Brazil (Bacen)."""

    CPF = "CPF"
    CNPJ = "CNPJ"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    EVP = "EVP"  # Chave Aleatória / Endereço Virtual Pagador (UUID v4)


class ChavePIX(BrazilianType):
    """Brazilian Instant Payment Key (Chave PIX).

    Features:
    - Automatically identifies and validates the key type:
      * CPF: 11-digit valid CPF.
      * CNPJ: 14-digit valid CNPJ.
      * Email: Valid RFC 5322 e-mail address.
      * Phone: Valid Brazilian phone (+55DD9XXXXXXXX or DD9XXXXXXXX).
      * EVP: Valid UUID v4 random key.
    - `.key_type`: Returns `PixKeyType` enum.
    - `.normalized`: Returns canonical format specified by Bacen.
    - `.formatted`: Returns formatted representation according to the key type.
    - `.masked`: LGPD-safe masked representation.
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
            f"Value '{value}' is not a valid PIX key (must be CPF, CNPJ, Email, Phone or UUID).",
            value=value,
        )

    @property
    def key_type(self) -> PixKeyType:
        """Returns the detected PIX key type category."""
        return self._key_type

    @property
    def normalized(self) -> str:
        """Returns the Bacen canonical format of the key."""
        return self._normalized

    @property
    def formatted(self) -> str:
        """Returns formatted string according to the key type."""
        if self.key_type == PixKeyType.CPF:
            return CPF(self._normalized).formatted
        if self.key_type == PixKeyType.CNPJ:
            return CNPJ(self._normalized).formatted
        if self.key_type == PixKeyType.PHONE:
            return TelefoneBR(self._normalized).formatted
        return self._normalized

    @property
    def masked(self) -> str:
        """Returns masked string according to the key type."""
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
        """Generates a valid random EVP (UUID v4) PIX key."""
        return cls(str(uuid.uuid4()))

    @classmethod
    def openapi_schema_extra(cls) -> Dict[str, Any]:
        return {
            "type": "string",
            "title": "ChavePIX",
            "description": "Brazilian Central Bank PIX key (CPF, CNPJ, Email, Phone, or UUID EVP)",
            "examples": [
                "12345678900",
                "+5511987654321",
                "usuario@dominio.com.br",
                "123e4567-e89b-12d3-a456-426614174000",
            ],
        }


# English alias
PixKey = ChavePIX
