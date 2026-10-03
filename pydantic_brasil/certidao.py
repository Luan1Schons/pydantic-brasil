"""Validação e formatação de Certidão Civil (Nascimento, Casamento e Óbito)."""

from __future__ import annotations

import random
from typing import ClassVar, Dict, Optional

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.exceptions import CertidaoCivilInvalidError


class CertidaoCivil(BrazilianType):
    """Certidão de Registro Civil Unificada (Provimento CNJ nº 63/2017).

    Valida certidões padronizadas de 32 dígitos para registros de Nascimento, Casamento e Óbito.
    Formato: AAAAAA.BB.CC.DDDD.E.FFFFF.GGG.HHHHHHH-II
    - AAAAAA: 6 dígitos do código CNS do cartório
    - BB: 2 dígitos do código do acervo (geralmente 01)
    - CC: 2 dígitos do tipo de livro (55=Nascimento, 66=Casamento Civil, 88=Óbito)
    - DDDD: 4 dígitos do ano do registro
    - E: 1 dígito do tipo do livro
    - FFFFF: 5 dígitos do número do livro
    - GGG: 3 dígitos do número da folha
    - HHHHHHH: 7 dígitos do número do termo
    - II: 2 dígitos verificadores por Módulo 11 cíclico
    """

    EXPECTED_DIGITS: ClassVar[Optional[int]] = 32
    DOC_NAME: ClassVar[str] = "Certidão Civil (CNJ)"

    TYPE_NAMES: ClassVar[Dict[str, str]] = {
        "55": "Nascimento",
        "66": "Casamento Civil",
        "77": "Casamento Religioso com Efeito Civil",
        "88": "Óbito",
        "99": "Natimorto / Proclamas",
    }

    @staticmethod
    def _cyclical_weighted_sum(digits: list[int]) -> int:
        total = 0
        multiplier = 32 - len(digits)
        for d in digits:
            total += d * multiplier
            multiplier += 1
            if multiplier > 10:
                multiplier = 0
        return total

    @classmethod
    def _calculate_check_digits(cls, base_digits: list[int]) -> str:
        s1 = cls._cyclical_weighted_sum(base_digits)
        dv1 = s1 % 11
        if dv1 > 9:
            dv1 = 1

        s2 = cls._cyclical_weighted_sum(base_digits + [dv1])
        dv2 = s2 % 11
        if dv2 > 9:
            dv2 = 1

        return f"{dv1}{dv2}"

    @classmethod
    def _validate(cls, value: str) -> str:
        digits = cls._extract_digits(value)

        if len(digits) != 32:
            raise CertidaoCivilInvalidError(
                f"Certidão Civil deve conter exatamente 32 dígitos (recebido '{value}')",
                value=value,
            )

        if len(set(digits)) == 1:
            raise CertidaoCivilInvalidError(
                f"Certidão Civil não pode conter todos os dígitos iguais: '{value}'",
                value=value,
            )

        base_digits = [int(d) for d in digits[:30]]
        expected_dv = cls._calculate_check_digits(base_digits)
        given_dv = digits[30:]

        if given_dv != expected_dv:
            raise CertidaoCivilInvalidError(
                f"Dígitos verificadores inválidos na Certidão Civil '{value}' "
                f"(esperado '{expected_dv}', recebido '{given_dv}')",
                value=value,
            )

        return digits

    @property
    def cartorio_cns(self) -> str:
        """Retorna o código CNS do cartório emissor com 6 dígitos."""
        return self.digits[:6]

    @property
    def year(self) -> int:
        """Retorna o ano de registro do documento."""
        return int(self.digits[10:14])

    @property
    def type_code(self) -> str:
        """Retorna o código do tipo de registro (55, 66, 77, 88)."""
        return self.digits[8:10]

    @property
    def type_name(self) -> str:
        """Retorna o nome do tipo de certidão (ex: Nascimento, Casamento, Óbito)."""
        return self.TYPE_NAMES.get(self.type_code, "Outro")

    @property
    def formatted(self) -> str:
        """Retorna a certidão formatada no padrão do CNJ."""
        d = self.digits
        return (
            f"{d[:6]}.{d[6:8]}.{d[8:10]}.{d[10:14]}."
            f"{d[14]}.{d[15:20]}.{d[20:23]}.{d[23:30]}-{d[30:]}"
        )

    @property
    def masked(self) -> str:
        """Retorna a certidão mascarada em conformidade com a LGPD."""
        d = self.digits
        return f"{d[:6]}.**.**.{d[10:14]}." f"*.*****.***.*******-{d[30:]}"

    @classmethod
    def generate(
        cls,
        record_type: str = "55",
        year: Optional[int] = None,
        formatted: bool = False,
    ) -> CertidaoCivil:
        """Gera um número de certidão civil válido para testes."""
        yr = year or random.randint(1990, 2026)
        cns = f"{random.randint(100000, 999999):06d}"
        acervo = "01"
        tipo = record_type if record_type in cls.TYPE_NAMES else "55"
        livro_tipo = "1"
        livro = f"{random.randint(1, 99999):05d}"
        folha = f"{random.randint(1, 999):03d}"
        termo = f"{random.randint(1, 9999999):07d}"

        base_str = f"{cns}{acervo}{tipo}{yr:04d}{livro_tipo}{livro}{folha}{termo}"
        base_digits = [int(d) for d in base_str]
        dv = cls._calculate_check_digits(base_digits)

        raw = f"{base_str}{dv}"
        instance = cls(raw)
        if formatted:
            return cls(instance.formatted)
        return instance


Certidao = CertidaoCivil
