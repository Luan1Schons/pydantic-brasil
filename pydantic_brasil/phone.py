"""Brazilian Phone number (TelefoneBR) validation and formatting."""

from __future__ import annotations

import random
from typing import Any, ClassVar, Dict, Optional, Set, Union

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.exceptions import PhoneInvalidError


class TelefoneBR(BrazilianType):
    """Brazilian landline and mobile telephone number (TelefoneBR).

    Features:
    - Validates Brazilian DDD area codes.
    - Validates mobile (11 digits, starts with 9) and landline (10 digits, starts with 2-5).
    - Accepts optional Brazilian country code `+55`.
    - `.is_mobile` / `.is_landline`: Classifies mobile vs landline.
    - `.ddd`: Area code string (e.g. '11', '21').
    - `.number`: Local subscriber number string.
    - `.formatted`: `(11) 98765-4321` or `(11) 3456-7890`.
    - `.masked`: `(11) 9****-**21`.
    - `.e164`: International E.164 format: `+5511987654321`.
    - `.whatsapp_link`: Direct WhatsApp click-to-chat URL: `https://wa.me/5511987654321`.
    - `TelefoneBR.generate(ddd=11, mobile=True)`: Test data generator.
    """

    VALID_DDDS: ClassVar[Set[str]] = {
        # SP
        "11",
        "12",
        "13",
        "14",
        "15",
        "16",
        "17",
        "18",
        "19",
        # RJ / ES
        "21",
        "22",
        "24",
        "27",
        "28",
        # MG
        "31",
        "32",
        "33",
        "34",
        "35",
        "37",
        "38",
        # PR / SC
        "41",
        "42",
        "43",
        "44",
        "45",
        "46",
        "47",
        "48",
        "49",
        # RS
        "51",
        "53",
        "54",
        "55",
        # Centro-Oeste / Norte
        "61",
        "62",
        "63",
        "64",
        "65",
        "66",
        "67",
        "68",
        "69",
        # Nordeste
        "71",
        "73",
        "74",
        "75",
        "77",
        "79",
        "81",
        "82",
        "83",
        "84",
        "85",
        "86",
        "87",
        "88",
        "89",
        # Norte
        "91",
        "92",
        "93",
        "94",
        "95",
        "96",
        "97",
        "98",
        "99",
    }

    @classmethod
    def _extract_digits(cls, value: str) -> str:
        digits = super()._extract_digits(value)
        if digits.startswith("55") and len(digits) in (12, 13):
            return digits[2:]
        return digits

    @classmethod
    def _validate(cls, value: str) -> str:
        digits = cls._extract_digits(value)

        if len(digits) not in (10, 11):
            raise PhoneInvalidError(
                f"Brazilian phone number must have 10 (landline) or 11 (mobile) digits "
                f"(received {len(digits)})",
                value=value,
            )

        ddd = digits[:2]
        if ddd not in cls.VALID_DDDS:
            raise PhoneInvalidError(
                f"Invalid Brazilian area code (DDD): '{ddd}'",
                value=value,
            )

        number = digits[2:]
        if len(digits) == 11:
            # Mobile: must start with 9
            if number[0] != "9":
                raise PhoneInvalidError(
                    f"Brazilian mobile numbers must start with digit '9' (got '{number[0]}')",
                    value=value,
                )
        else:
            # Landline (10 digits): must start with 2, 3, 4, or 5
            if number[0] not in ("2", "3", "4", "5"):
                raise PhoneInvalidError(
                    f"Brazilian landline numbers must start with 2, 3, 4, or 5 (got '{number[0]}')",
                    value=value,
                )

        return value

    @property
    def ddd(self) -> str:
        """Returns the 2-digit Brazilian area code (DDD)."""
        return self.digits[:2]

    @property
    def number(self) -> str:
        """Returns the local subscriber number without DDD."""
        return self.digits[2:]

    @property
    def is_mobile(self) -> bool:
        """Returns True if this is a 9-digit mobile number."""
        return len(self.digits) == 11

    @property
    def is_landline(self) -> bool:
        """Returns True if this is an 8-digit landline number."""
        return len(self.digits) == 10

    @property
    def formatted(self) -> str:
        """Returns standard punctuated telephone string: `(11) 98765-4321` or `(11) 3456-7890`."""
        d = self.digits
        if len(d) == 11:
            return f"({d[:2]}) {d[2:7]}-{d[7:]}"
        return f"({d[:2]}) {d[2:6]}-{d[6:]}"

    @property
    def masked(self) -> str:
        """Returns masked telephone string: `(11) 9****-**21` or `(11) 3***-**90`."""
        d = self.digits
        if len(d) == 11:
            return f"({d[:2]}) {d[2]}****-**{d[-2:]}"
        return f"({d[:2]}) {d[2]}***-**{d[-2:]}"

    @property
    def e164(self) -> str:
        """Returns international E.164 formatted string: `+5511987654321`."""
        return f"+55{self.digits}"

    @property
    def whatsapp_link(self) -> str:
        """Returns direct WhatsApp click-to-chat URL: `https://wa.me/5511987654321`."""
        return f"https://wa.me/55{self.digits}"

    @classmethod
    def generate(
        cls,
        ddd: Optional[Union[int, str]] = None,
        mobile: bool = True,
        formatted: bool = False,
    ) -> TelefoneBR:
        """Generates a valid Brazilian phone number for testing.

        Args:
            ddd: Optional DDD (e.g. 11, '21'). If omitted, randomly chosen from valid DDDs.
            mobile: If True generates 11-digit mobile, else 10-digit landline.
            formatted: If True returns punctuated string.
        """
        chosen_ddd = str(ddd) if ddd is not None else random.choice(list(cls.VALID_DDDS))
        if chosen_ddd not in cls.VALID_DDDS:
            raise ValueError(f"Invalid Brazilian DDD: {ddd}")

        if mobile:
            subscriber = "9" + "".join(str(random.randint(0, 9)) for _ in range(8))
        else:
            first_digit = str(random.choice([2, 3, 4, 5]))
            subscriber = first_digit + "".join(str(random.randint(0, 9)) for _ in range(7))

        raw = chosen_ddd + subscriber
        instance = cls(raw)
        return cls(instance.formatted if formatted else raw)

    @classmethod
    def openapi_schema_extra(cls) -> Dict[str, Any]:
        return {
            "type": "string",
            "title": "TelefoneBR",
            "description": "Brazilian phone number (landline or mobile with valid DDD)",
            "examples": ["(11) 98765-4321", "11987654321", "+5511987654321"],
            "pattern": r"^(\+55)?\s?\(?[1-9]{2}\)?\s?(9[1-9]\d{3}|[2-5]\d{3})-?\d{4}$",
        }
