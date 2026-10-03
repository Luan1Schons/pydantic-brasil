"""Validação e catálogo de códigos de bancos brasileiros (COMPE / ISPB)."""

from __future__ import annotations

from typing import Any, ClassVar, Dict, List, NamedTuple, Optional, cast

from pydantic_brasil.base import BrazilianType
from pydantic_brasil.exceptions import BankCodeInvalidError


class BankInfo(NamedTuple):
    code: str
    name: str
    short_name: str
    ispb: str


class BancoBR(BrazilianType):
    """Código de Banco Brasileiro (COMPE) e catálogo de instituições.

    Valida códigos COMPE de 3 dígitos atribuídos pelo Banco Central do Brasil (Bacen)
    e fornece acesso ao nome empresarial, nome comercial e código ISPB.
    """

    EXPECTED_DIGITS: ClassVar[Optional[int]] = 3
    DOC_NAME: ClassVar[str] = "Código de Banco Brasileiro (COMPE)"

    BANKS: ClassVar[Dict[str, BankInfo]] = {
        "001": BankInfo("001", "Banco do Brasil S.A.", "Banco do Brasil", "00000000"),
        "003": BankInfo("003", "Banco da Amazônia S.A.", "Banco da Amazônia", "04902979"),
        "004": BankInfo("004", "Banco do Nordeste do Brasil S.A.", "Banco do Nordeste", "07237373"),
        "021": BankInfo(
            "021", "BANESTES S.A. Banco do Estado do Espírito Santo", "Banestes", "28127603"
        ),
        "033": BankInfo("033", "Banco Santander (Brasil) S.A.", "Santander", "90400888"),
        "041": BankInfo("041", "Banco do Estado do Rio Grande do Sul S.A.", "Banrisul", "92702067"),
        "047": BankInfo("047", "Banco do Estado de Sergipe S.A.", "Banese", "13009717"),
        "070": BankInfo("070", "BRB - Banco de Brasília S.A.", "BRB", "00000208"),
        "074": BankInfo("074", "Banco J. Safra S.A.", "J. Safra", "03017677"),
        "077": BankInfo("077", "Banco Inter S.A.", "Inter", "00416968"),
        "104": BankInfo("104", "Caixa Econômica Federal", "Caixa", "00360305"),
        "197": BankInfo("197", "Stone Instituição de Pagamento S.A.", "Stone", "16501555"),
        "208": BankInfo("208", "Banco BTG Pactual S.A.", "BTG Pactual", "30306294"),
        "212": BankInfo("212", "Banco Original S.A.", "Original", "92894922"),
        "237": BankInfo("237", "Banco Bradesco S.A.", "Bradesco", "60746948"),
        "260": BankInfo(
            "260", "Nu Pagamentos S.A. - Instituição de Pagamento", "Nubank", "18236120"
        ),
        "290": BankInfo(
            "290", "PagBank Internet Instituição de Pagamento S.A.", "PagBank", "08561701"
        ),
        "318": BankInfo("318", "Banco BMG S.A.", "BMG", "61186680"),
        "323": BankInfo(
            "323", "Mercado Pago Instituição de Pagamento Ltda.", "Mercado Pago", "10573521"
        ),
        "336": BankInfo("336", "Banco C6 S.A.", "C6 Bank", "31872495"),
        "341": BankInfo("341", "Itaú Unibanco S.A.", "Itaú", "60701190"),
        "380": BankInfo("380", "PicPay Instituição de Pagamento S.A.", "PicPay", "22896431"),
        "403": BankInfo("403", "Cora Sociedade de Crédito Direto S.A.", "Cora", "37880206"),
        "422": BankInfo("422", "Banco Safra S.A.", "Safra", "58160789"),
        "633": BankInfo("633", "Banco Rendimento S.A.", "Rendimento", "68900810"),
        "655": BankInfo("655", "Banco Votorantim S.A.", "Banco BV", "59588111"),
        "748": BankInfo("748", "Banco Cooperativo Sicredi S.A.", "Sicredi", "01181521"),
        "756": BankInfo("756", "Banco Cooperativo do Brasil S.A.", "Sicoob", "02038232"),
    }

    _info: BankInfo

    def __new__(cls, value: Any) -> BancoBR:
        if isinstance(value, cls):
            return value

        cleaned = cls._clean_input(value)
        digits = cls._extract_digits(cleaned)

        if not digits:
            # Try lookup by name or short name
            query = cleaned.strip().lower()
            found: Optional[BankInfo] = None
            for b in cls.BANKS.values():
                if query in b.short_name.lower() or query in b.name.lower():
                    found = b
                    break
            if found is None:
                raise BankCodeInvalidError(
                    f"Banco brasileiro ou código COMPE não encontrado: '{value}'",
                    value=value,
                )
            code = found.code
        else:
            code = digits.zfill(3)

        if code not in cls.BANKS:
            raise BankCodeInvalidError(
                f"Código de banco COMPE inválido ou não cadastrado: '{value}' "
                f"(resolvido para '{code}')",
                value=value,
            )

        instance = cast(BancoBR, super().__new__(cls, code))
        instance._info = cls.BANKS[code]
        instance._digits = code
        return instance

    @classmethod
    def _validate(cls, value: str) -> str:
        digits = cls._extract_digits(value)
        code = digits.zfill(3)
        if code not in cls.BANKS:
            # Check name
            q = value.strip().lower()
            for b in cls.BANKS.values():
                if q in b.short_name.lower() or q in b.name.lower():
                    return b.code
            raise BankCodeInvalidError(
                f"Código de banco COMPE inválido: '{value}'",
                value=value,
            )
        return code

    @property
    def code(self) -> str:
        """Retorna o código COMPE com 3 dígitos (ex: '001', '260')."""
        return self._info.code

    @property
    def name(self) -> str:
        """Retorna a razão social oficial da instituição financeira."""
        return self._info.name

    @property
    def short_name(self) -> str:
        """Retorna o nome comercial / popular da instituição."""
        return self._info.short_name

    @property
    def ispb(self) -> str:
        """Retorna o código ISPB de 8 dígitos definido pelo Bacen."""
        return self._info.ispb

    @property
    def formatted(self) -> str:
        """Retorna a representação formatada: 'COMPE - Nome Comercial'."""
        return f"{self.code} - {self.short_name}"

    @property
    def masked(self) -> str:
        """Retorna a representação da instituição financeira (dados públicos)."""
        return self.formatted

    @classmethod
    def search(cls, term: str) -> List[BankInfo]:
        """Pesquisa bancos por código COMPE, ISPB ou trecho do nome."""
        t = term.strip().lower()
        return [
            b
            for b in cls.BANKS.values()
            if t in b.code or t in b.ispb or t in b.short_name.lower() or t in b.name.lower()
        ]


CodigoBanco = BancoBR
