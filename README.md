# pydantic-brasil 🇧🇷

[![PyPI version](https://img.shields.io/pypi/v/pydantic-brasil?color=blue&style=flat-square)](https://pypi.org/project/pydantic-brasil/)
[![Python versions](https://img.shields.io/pypi/pyversions/pydantic-brasil?style=flat-square)](https://pypi.org/project/pydantic-brasil/)
[![CI Tests](https://github.com/Luan1Schons/pydantic-brasil/actions/workflows/test.yml/badge.svg)](https://github.com/Luan1Schons/pydantic-brasil/actions/workflows/test.yml)
[![Coverage](https://img.shields.io/badge/coverage-94%25-brightgreen?style=flat-square)](https://github.com/Luan1Schons/pydantic-brasil)
[![Pydantic v2](https://img.shields.io/badge/pydantic-v2-E92063?logo=pydantic&logoColor=white&style=flat-square)](https://docs.pydantic.dev/)
[![Types](https://img.shields.io/badge/typing-Mypy%20Strict-blue?style=flat-square)](https://mypy.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](https://opensource.org/licenses/MIT)

**Modern, high-performance Brazilian data types and validators for Pydantic v2 and FastAPI.**

*Read this in [Português (Brasil)](README.pt-BR.md).*

---

## ⚡ Highlights

- **⚡ Built natively for Pydantic v2**: Integrates directly with `pydantic-core` via `__get_pydantic_core_schema__` for lightning-fast C-speed validation.
- **🛡️ 2026 Alphanumeric CNPJ Ready**: Full support for both traditional numeric CNPJ and the new Receita Federal 2026 alphanumeric CNPJ format.
- **🔒 LGPD-Compliant Masking**: Native `.masked` property on sensitive fields (`123.***.***-00`) for logs, analytics, and telemetry.
- **🗄️ Database-Optimized**: `model_dump()` automatically serializes documents, phones, and postal codes into clean unpunctuated digits for optimal indexing and querying in Postgres, MySQL, MongoDB, etc.
- **🚀 Zero External Dependencies**: Powered only by `pydantic>=2.0.0` and `typing-extensions`.
- **🎯 100% Type-Safe**: Full PEP 561 compliance (`py.typed`) and passes `mypy --strict`.
- **🧪 Built-in Test Data Generators**: Generate realistic, valid documents on demand (`CPF.generate()`, `CNPJ.generate()`, `ChavePIX.generate_evp()`, etc.).

---

## 📦 Supported Brazilian Types

| Type | Name / Alias | Features & Properties |
| :--- | :--- | :--- |
| **CPF** | `CPF` | Mod 11 checksum, repeated digit detection, `.fiscal_region`, `.formatted`, `.digits`, `.masked`, `.generate()` |
| **CNPJ** | `CNPJ` | Traditional + 2026 Alphanumeric format, `.is_matriz`, `.is_filial`, `.branch_number`, `.formatted`, `.digits`, `.masked`, `.generate()` |
| **Documento Geral** | `CPFouCNPJ`, `DocumentoBR` | Polymorphic auto-detection, `.is_cpf`, `.is_cnpj`, `.as_cpf()`, `.as_cnpj()` |
| **CEP** | `CEP` | 8-digit postal validation, Correios UF range detection (`.state`), `.formatted`, `.digits`, `.generate()` |
| **Telefone** | `TelefoneBR` | Mobile (9 digits) and landline (8 digits), ANATEL DDD check, `.ddd`, `.e164`, `.whatsapp_link`, `.is_mobile`, `.generate()` |
| **Chave PIX** | `ChavePIX`, `PixKey` | Bacen types (CPF, CNPJ, Email, Phone, EVP), `.key_type`, `.normalized`, `.formatted`, `.masked`, `.generate_evp()` |
| **Dinheiro BRL** | `DinheiroBRL`, `BRL` | `Decimal`-backed financial precision, parses `"R$ 1.250,50"`, `.centavos` (int), `.formatted`, arithmetic ops |
| **Placa Veicular** | `PlacaVeiculo` | Mercosul (`ABC1D23`) and Legacy (`ABC-1234`), `.is_mercosul`, `.to_mercosul()`, `.to_antiga()` |
| **RENAVAM** | `RENAVAM` | 11-digit national vehicle registry validation with Mod 11 |
| **CNH** | `CNH` | 11-digit national driver's license with dual Mod 11 verification |
| **Inscrição Estadual**| `InscricaoEstadual` | SP (including rural 'P' prefix), RJ, MG, RS, PR, SC, and generic length fallback; accepts `"ISENTO"` |

---

## 🚀 Installation

```bash
pip install pydantic-brasil
```

or with Poetry:

```bash
poetry add pydantic-brasil
```

or with uv:

```bash
uv add pydantic-brasil
```

---

## 🛠️ Quickstart

### 1. Pydantic Model Validation

```python
from pydantic import BaseModel
from pydantic_brasil import CPF, CNPJ, CEP, TelefoneBR, ChavePIX, DinheiroBRL

class CustomerSchema(BaseModel):
    name: str
    cpf: CPF
    cnpj: CNPJ
    cep: CEP
    phone: TelefoneBR
    pix: ChavePIX
    credit_limit: DinheiroBRL

# Accepts formatted strings, raw digits, integers, etc.
customer = CustomerSchema(
    name="Maria Silva",
    cpf="123.456.789-09",
    cnpj="12.ABC.345/0001-67",  # Supports 2026 alphanumeric format!
    cep="01310-100",
    phone="(11) 98765-4321",
    pix="maria.silva@example.com",
    credit_limit="R$ 12.500,75",
)

# Rich property access
print(customer.cpf.formatted)      # "123.456.789-09"
print(customer.cpf.digits)         # "12345678909"
print(customer.cpf.masked)         # "123.***.***-09" (LGPD safe)
print(customer.cpf.fiscal_region)  # ["SP"]

print(customer.phone.e164)          # "+5511987654321"
print(customer.phone.whatsapp_link) # "https://wa.me/5511987654321"

print(customer.pix.key_type)       # PixKeyType.EMAIL
print(customer.credit_limit.centavos) # 1250075 (int, perfect for payment gateways)

# Database-friendly dumping
print(customer.model_dump())
# {
#     "name": "Maria Silva",
#     "cpf": "12345678909",
#     "cnpj": "12ABC345000167",
#     "cep": "01310100",
#     "phone": "11987654321",
#     "pix": "maria.silva@example.com",
#     "credit_limit": 12500.75
# }
```

### 2. FastAPI Integration

All types generate clean OpenAPI schemas with proper descriptions and examples in Swagger UI (`/docs`):

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pydantic_brasil import CPF, ChavePIX, DinheiroBRL

app = FastAPI(title="Minha API Brasileira")

class PixPaymentRequest(BaseModel):
    pix_key: ChavePIX
    amount: DinheiroBRL
    payer_cpf: CPF

@app.post("/pix/pay")
def process_pix(payment: PixPaymentRequest):
    return {
        "status": "success",
        "key_type": payment.pix_key.key_type,
        "amount_cents": payment.amount.centavos,
        "payer": payment.payer_cpf.masked,
    }
```

---

## 🔍 Detailed Usage

### CPF & Fiscal Regions

```python
from pydantic_brasil import CPF

cpf = CPF("123.456.789-09")

# Format representations
cpf.formatted  # "123.456.789-09"
cpf.digits     # "12345678909"
cpf.masked     # "123.***.***-09"

# Identify tax issuance region by 9th digit
cpf.fiscal_region  # ["SP"]

# Smart comparison (formats don't matter)
CPF("123.456.789-09") == "12345678909"  # True
CPF("123.456.789-09") == 12345678909    # True

# Generate mock data for unit tests
test_cpf = CPF.generate(state="RS", formatted=True)
```

### CNPJ (Including 2026 Alphanumeric Format)

The Federal Revenue of Brazil (Receita Federal) introduced the alphanumeric format for CNPJs starting in 2026. `pydantic-brasil` handles both legacy numeric and new alphanumeric formats seamlessly:

```python
from pydantic_brasil import CNPJ

# Traditional numeric CNPJ
cnpj_old = CNPJ("12.345.678/0001-95")

# 2026 Alphanumeric CNPJ
cnpj_new = CNPJ("12.ABC.345/0001-67")
cnpj_new.is_matriz     # True
cnpj_new.branch_number # "0001"
cnpj_new.masked        # "12.***.***/0001-67"

# Generate test CNPJs
test_cnpj = CNPJ.generate(branch=1, formatted=True)
```

### Polymorphic Document (`CPFouCNPJ` / `DocumentoBR`)

When a field can be either a person's CPF or a company's CNPJ:

```python
from pydantic_brasil import CPFouCNPJ

doc = CPFouCNPJ("12.345.678/0001-95")
if doc.is_cnpj:
    company = doc.as_cnpj()
    print(company.is_matriz)
```

### CEP & State Inference

```python
from pydantic_brasil import CEP

cep = CEP("01310-100")
cep.formatted  # "01310-100"
cep.digits     # "01310100"
cep.state      # "SP" (Inferred from Correios postal range)

test_cep = CEP.generate(state="RJ")
```

### TelefoneBR (Landline & Mobile)

```python
from pydantic_brasil import TelefoneBR

phone = TelefoneBR("+55 (11) 98765-4321")
phone.digits         # "11987654321"
phone.formatted      # "(11) 98765-4321"
phone.e164           # "+5511987654321"
phone.whatsapp_link  # "https://wa.me/5511987654321"
phone.ddd            # "11"
phone.is_mobile      # True
phone.is_landline    # False

# Generate mock phones
test_phone = TelefoneBR.generate(ddd=21, mobile=True)
```

### Chave PIX

Auto-detects and validates the 5 official types according to Central Bank rules:

```python
from pydantic_brasil import ChavePIX, PixKeyType

key1 = ChavePIX("123.456.789-09")           # PixKeyType.CPF
key2 = ChavePIX("user@company.com.br")       # PixKeyType.EMAIL
key3 = ChavePIX("+5511987654321")            # PixKeyType.PHONE
key4 = ChavePIX("550e8400-e29b-41d4-a716-446655440000") # PixKeyType.EVP

print(key1.normalized)  # "12345678909"
print(key3.normalized)  # "+5511987654321"
print(key2.masked)      # "u***r@company.com.br"

# Generate random EVP
random_pix = ChavePIX.generate_evp()
```

### DinheiroBRL (Monetary Precision)

Avoid floating-point representation bugs (`0.1 + 0.2 != 0.3`). `DinheiroBRL` uses `Decimal` internally and offers convenient constructors and conversions:

```python
from pydantic_brasil import DinheiroBRL

price = DinheiroBRL("R$ 1.500,50")
print(price.centavos)   # 150050 (int, ideal for payment APIs)
print(price.formatted)  # "R$ 1.500,50"

# From integer cents
fee = DinheiroBRL.from_centavos(250) # R$ 2,50

# Native math operations
total = price + fee
print(total.formatted)  # "R$ 1.503,00"
```

### Placa Veicular (Mercosul & Legacy)

```python
from pydantic_brasil import PlacaVeiculo

placa = PlacaVeiculo("ABC-1234")
print(placa.is_antiga)       # True
print(placa.to_mercosul())   # "ABC1C34"

mercosul = PlacaVeiculo("ABC1C34")
print(mercosul.is_mercosul)  # True
print(mercosul.to_antiga())  # "ABC-1234"
```

---

## 🧪 Testing & Code Quality

```bash
# Run pytest with coverage report
pytest --cov=pydantic_brasil --cov-report=term-missing

# Run strict type checking
mypy pydantic_brasil tests

# Check formatting and style
flake8
black --check .
```

---

## 🤝 Contributing

Contributions are very welcome! Feel free to open an issue or pull request.
For major changes, please open an issue first to discuss what you would like to change.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/MinhaFeature`)
3. Commit your Changes (`git commit -m 'feat: Adiciona nova funcionalidade'`)
4. Push to the Branch (`git push origin feature/MinhaFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
