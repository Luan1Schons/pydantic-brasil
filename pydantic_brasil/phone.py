"""Validação e formatação de telefone brasileiro (TelefoneBR)."""

from __future__ import annotations

import random
from typing import Any, ClassVar, Dict, Optional, Set, Union

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.exceptions import PhoneInvalidError


class TelefoneBR(BrazilianType):
    """Número de telefone fixo ou celular brasileiro (TelefoneBR).

    Recursos:
    - Validação de códigos de área (DDDs oficiais da ANATEL).
    - Validação de celular (11 dígitos, iniciado com 9) e fixo (10 dígitos, iniciado com 2 a 5).
    - Aceita código do país `+55` opcionalmente.
    - `.is_mobile` / `.is_landline`: Classificação entre celular e fixo.
    - `.ddd`: Código de área com 2 dígitos (ex: '11', '21').
    - `.number`: Número do assinante sem o DDD.
    - `.formatted`: `(11) 98765-4321` ou `(11) 3456-7890`.
    - `.masked`: `(11) 9****-**21`.
    - `.e164`: Formato internacional E.164: `+5511987654321`.
    - `.whatsapp_link`: Link direto para conversa no WhatsApp: `https://wa.me/5511987654321`.
    - `TelefoneBR.generate(ddd=11, mobile=True)`: Gerador para testes.
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
        # Centro-Oeste / TO / RO / AC
        "61",
        "62",
        "63",
        "64",
        "65",
        "66",
        "67",
        "68",
        "69",
        # BA / SE
        "71",
        "73",
        "74",
        "75",
        "77",
        "79",
        # PE / AL / PB / RN
        "81",
        "82",
        "83",
        "84",
        "87",
        # CE / PI / MA / PA / AP / AM / RR
        "85",
        "86",
        "88",
        "89",
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
        # Remove código do país se fornecido (+55)
        if len(digits) in (12, 13) and digits.startswith("55"):
            digits = digits[2:]
        return digits

    @classmethod
    def _validate(cls, value: str) -> str:
        digits = cls._extract_digits(value)

        if len(digits) not in (10, 11):
            raise PhoneInvalidError(
                f"Telefone brasileiro deve ter 10 (fixo) ou 11 (celular) dígitos "
                f"(recebido {len(digits)})",
                value=value,
            )

        ddd = digits[:2]
        if ddd not in cls.VALID_DDDS:
            raise PhoneInvalidError(
                f"DDD '{ddd}' inválido para telefone brasileiro",
                value=value,
            )

        number = digits[2:]
        if len(digits) == 11:
            # Celular deve iniciar com 9
            if number[0] != "9":
                raise PhoneInvalidError(
                    f"Celular brasileiro deve iniciar com o dígito '9' (recebido '{number[0]}')",
                    value=value,
                )
        else:
            # Fixo deve iniciar com 2, 3, 4 ou 5
            if number[0] not in ("2", "3", "4", "5"):
                raise PhoneInvalidError(
                    f"Telefone fixo deve iniciar com 2, 3, 4 ou 5 (recebido '{number[0]}')",
                    value=value,
                )

        return value

    @property
    def ddd(self) -> str:
        """Retorna o código DDD com 2 dígitos."""
        return self.digits[:2]

    @property
    def number(self) -> str:
        """Retorna o número do assinante sem o DDD."""
        return self.digits[2:]

    @property
    def is_mobile(self) -> bool:
        """Retorna True se for um telefone celular (11 dígitos)."""
        return len(self.digits) == 11

    @property
    def is_landline(self) -> bool:
        """Retorna True se for um telefone fixo (10 dígitos)."""
        return len(self.digits) == 10

    @property
    def formatted(self) -> str:
        """Retorna o telefone formatado: `(11) 98765-4321` ou `(11) 3456-7890`."""
        d = self.digits
        if len(d) == 11:
            return f"({d[:2]}) {d[2:7]}-{d[7:]}"
        return f"({d[:2]}) {d[2:6]}-{d[6:]}"

    @property
    def masked(self) -> str:
        """Retorna o telefone mascarado: `(11) 9****-**21` ou `(11) 3***-**90`."""
        d = self.digits
        if len(d) == 11:
            return f"({d[:2]}) {d[2]}****-**{d[-2:]}"
        return f"({d[:2]}) {d[2]}***-**{d[-2:]}"

    @property
    def e164(self) -> str:
        """Retorna o número no formato internacional E.164: `+5511987654321`."""
        return f"+55{self.digits}"

    @property
    def whatsapp_link(self) -> str:
        """Retorna o link oficial de conversa no WhatsApp: `https://wa.me/5511987654321`."""
        return f"https://wa.me/55{self.digits}"

    @classmethod
    def generate(
        cls,
        ddd: Optional[Union[int, str]] = None,
        mobile: bool = True,
        formatted: bool = False,
    ) -> TelefoneBR:
        """Gera um telefone válido para testes.

        Args:
            ddd: DDD opcional (ex: 11, '21'). Se omitido, sorteia um DDD válido.
            mobile: Se verdadeiro gera celular (11 dígitos), senão fixo (10 dígitos).
            formatted: Se verdadeiro retorna com pontuação.
        """
        chosen_ddd = str(ddd) if ddd is not None else random.choice(list(cls.VALID_DDDS))
        if chosen_ddd not in cls.VALID_DDDS:
            raise ValueError(f"DDD inválido: {ddd}")

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
            "description": "Número de telefone brasileiro (fixo ou celular com DDD válido)",
            "examples": ["(11) 98765-4321", "11987654321", "+5511987654321"],
            "pattern": r"^(\+55)?\s?\(?[1-9]{2}\)?\s?(9[1-9]\d{3}|[2-5]\d{3})-?\d{4}$",
        }
