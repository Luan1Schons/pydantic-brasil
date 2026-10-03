# pydantic-brasil 🇧🇷

[![Versão PyPI](https://img.shields.io/pypi/v/pydantic-brasil?color=blue&style=flat-square)](https://pypi.org/project/pydantic-brasil/)
[![Versões Python](https://img.shields.io/pypi/pyversions/pydantic-brasil?style=flat-square)](https://pypi.org/project/pydantic-brasil/)
[![Testes de CI](https://github.com/Luan1Schons/pydantic-brasil/actions/workflows/test.yml/badge.svg)](https://github.com/Luan1Schons/pydantic-brasil/actions/workflows/test.yml)
[![Cobertura](https://img.shields.io/badge/coverage-94%25-brightgreen?style=flat-square)](https://github.com/Luan1Schons/pydantic-brasil)
[![Pydantic v2](https://img.shields.io/badge/pydantic-v2-E92063?logo=pydantic&logoColor=white&style=flat-square)](https://docs.pydantic.dev/)
[![Tipagem Estrita](https://img.shields.io/badge/typing-Mypy%20Strict-blue?style=flat-square)](https://mypy.readthedocs.io/)
[![Licença: MIT](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](https://opensource.org/licenses/MIT)

**Tipos de dados e validadores brasileiros modernos e de alta performance para Pydantic v2 e FastAPI.**

*Read this in [English](README.md).*

---

## ⚡ Destaques

- **⚡ Desenvolvido nativamente para Pydantic v2**: Integração direta com o `pydantic-core` via `__get_pydantic_core_schema__`, garantindo validação ultrarrápida compilada em C/Rust.
- **🛡️ Preparado para o CNPJ Alfanumérico 2026**: Suporte integral tanto ao formato numérico tradicional quanto ao novo padrão alfanumérico da Receita Federal.
- **🔒 Mascaramento em conformidade com a LGPD**: Propriedade `.masked` nativa em dados sensíveis (`123.***.***-00`) para logs seguros, telemetria e auditoria.
- **🗄️ Otimizado para Banco de Dados**: `model_dump()` serializa documentos, telefones e CEPs diretamente em dígitos limpos e desformatados, garantindo indexação e performance superiores em PostgreSQL, MySQL, SQLite e MongoDB.
- **🚀 Zero Dependências Externas**: Construído utilizando unicamente `pydantic>=2.0.0` e `typing-extensions`.
- **🎯 100% Tipado (PEP 561)**: Compatibilidade estrita comprovada com `mypy --strict`.
- **🧪 Geradores de Dados para Testes Unitários**: Crie instâncias e documentos válidos em tempo de execução com `.generate()` (`CPF.generate()`, `CNPJ.generate()`, `ChavePIX.generate_evp()`, etc.).

---

## 📦 Tipos Brasileiros Suportados

| Tipo | Nome / Alias | Recursos & Propriedades |
| :--- | :--- | :--- |
| **CPF** | `CPF` | Módulo 11, detecção de dígitos repetidos, `.fiscal_region`, `.formatted`, `.digits`, `.masked`, `.generate()` |
| **CNPJ** | `CNPJ` | Tradicional + Formato Alfanumérico 2026, `.is_matriz`, `.is_filial`, `.branch_number`, `.formatted`, `.digits`, `.masked`, `.generate()` |
| **Documento Geral** | `CPFouCNPJ`, `DocumentoBR` | Detecção polimórfica automática, `.is_cpf`, `.is_cnpj`, `.as_cpf()`, `.as_cnpj()` |
| **CEP** | `CEP` | Validação de 8 dígitos, detecção de UF por faixa dos Correios (`.state`), `.formatted`, `.digits`, `.generate()` |
| **Telefone** | `TelefoneBR` | Celular (9 dígitos) e fixo (8 dígitos), validação de DDDs da ANATEL, `.ddd`, `.e164`, `.whatsapp_link`, `.is_mobile`, `.generate()` |
| **Chave PIX** | `ChavePIX`, `PixKey` | Tipos oficiais Bacen (CPF, CNPJ, E-mail, Telefone, EVP), `.key_type`, `.normalized`, `.formatted`, `.masked`, `.generate_evp()` |
| **Dinheiro BRL** | `DinheiroBRL`, `BRL` | Precisão financeira com `Decimal`, parse de `"R$ 1.250,50"`, `.centavos` (int), `.formatted`, operadores aritméticos |
| **Placa de Veículo** | `PlacaVeiculo` | Mercosul (`ABC1D23`) e Tradicional (`ABC-1234`), `.is_mercosul`, `.to_mercosul()`, `.to_antiga()` |
| **RENAVAM** | `RENAVAM` | Validação de 11 dígitos pelo Módulo 11 |
| **CNH** | `CNH` | Validação de 11 dígitos com verificação dupla de DV pelo Módulo 11 |
| **Inscrição Estadual**| `InscricaoEstadual` | SP (incluindo produtor rural 'P'), RJ, MG, RS, PR, SC e fallback genérico para demais estados; aceita `"ISENTO"` |

---

## 🚀 Instalação

```bash
pip install pydantic-brasil
```

ou com Poetry:

```bash
poetry add pydantic-brasil
```

ou com uv:

```bash
uv add pydantic-brasil
```

---

## 🛠️ Guia Rápido

### 1. Validação em Modelos Pydantic

```python
from pydantic import BaseModel
from pydantic_brasil import CPF, CNPJ, CEP, TelefoneBR, ChavePIX, DinheiroBRL

class ClienteSchema(BaseModel):
    nome: str
    cpf: CPF
    cnpj: CNPJ
    cep: CEP
    telefone: TelefoneBR
    pix: ChavePIX
    limite_credito: DinheiroBRL

# Aceita strings formatadas, dígitos puros, números inteiros, etc.
cliente = ClienteSchema(
    nome="Maria Silva",
    cpf="123.456.789-09",
    cnpj="12.ABC.345/0001-67",  # Suporta o novo formato alfanumérico de 2026!
    cep="01310-100",
    telefone="(11) 98765-4321",
    pix="maria.silva@example.com",
    limite_credito="R$ 12.500,75",
)

# Propriedades ricas disponíveis
print(cliente.cpf.formatted)      # "123.456.789-09"
print(cliente.cpf.digits)         # "12345678909"
print(cliente.cpf.masked)         # "123.***.***-09" (Em conformidade com a LGPD)
print(cliente.cpf.fiscal_region)  # ["SP"]

print(cliente.telefone.e164)          # "+5511987654321"
print(cliente.telefone.whatsapp_link) # "https://wa.me/5511987654321"

print(cliente.pix.key_type)           # PixKeyType.EMAIL
print(cliente.limite_credito.centavos) # 1250075 (int puro, ideal para gateways de pagamento)

# Serialização limpa otimizada para persistência em bancos de dados
print(cliente.model_dump())
# {
#     "nome": "Maria Silva",
#     "cpf": "12345678909",
#     "cnpj": "12ABC345000167",
#     "cep": "01310100",
#     "telefone": "11987654321",
#     "pix": "maria.silva@example.com",
#     "limite_credito": 12500.75
# }
```

### 2. Integração com FastAPI

Todos os tipos geram esquemas OpenAPI automáticos e detalhados na documentação interativa do Swagger (`/docs`):

```python
from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_brasil import CPF, ChavePIX, DinheiroBRL

app = FastAPI(title="Minha API de Pagamentos")

class CobrancaPix(BaseModel):
    chave: ChavePIX
    valor: DinheiroBRL
    pagador_cpf: CPF

@app.post("/pix/pagar")
def pagar_pix(cobranca: CobrancaPix):
    return {
        "status": "sucesso",
        "tipo_chave": cobranca.chave.key_type,
        "valor_em_centavos": cobranca.valor.centavos,
        "pagador": cobranca.pagador_cpf.masked,
    }
```

---

## 🔍 Exemplos Detalhados

### CPF e Regiões Fiscais

```python
from pydantic_brasil import CPF

cpf = CPF("123.456.789-09")

cpf.formatted  # "123.456.789-09"
cpf.digits     # "12345678909"
cpf.masked     # "123.***.***-09"

# Identifica a Região Fiscal emissora pelo 9º dígito
cpf.fiscal_region  # ["SP"]

# Comparação inteligente (ignora pontuação e tipos compatíveis)
CPF("123.456.789-09") == "12345678909"  # True
CPF("123.456.789-09") == 12345678909    # True

# Gerador para testes automatizados
cpf_fake = CPF.generate(state="RS", formatted=True)
```

### CNPJ (Incluindo Alfanumérico 2026)

A Receita Federal estabeleceu o formato de CNPJ alfanumérico a partir de 2026. O `pydantic-brasil` suporta nativamente ambos os formatos:

```python
from pydantic_brasil import CNPJ

# CNPJ numérico tradicional
cnpj_legado = CNPJ("12.345.678/0001-95")

# CNPJ alfanumérico 2026
cnpj_novo = CNPJ("12.ABC.345/0001-67")
cnpj_novo.is_matriz     # True
cnpj_novo.branch_number # "0001"
cnpj_novo.masked        # "12.***.***/0001-67"

# Gerador para testes
cnpj_fake = CNPJ.generate(branch=1, formatted=True)
```

### Documento Polimórfico (`CPFouCNPJ` / `DocumentoBR`)

Útil para formulários e APIs onde o campo aceita tanto pessoa física quanto jurídica:

```python
from pydantic_brasil import CPFouCNPJ

doc = CPFouCNPJ("12.345.678/0001-95")
if doc.is_cnpj:
    empresa = doc.as_cnpj()
    print(empresa.is_matriz)
```

### CEP e Identificação do Estado

```python
from pydantic_brasil import CEP

cep = CEP("01310-100")
cep.formatted  # "01310-100"
cep.digits     # "01310100"
cep.state      # "SP" (Detectado pela faixa postal dos Correios)

cep_fake = CEP.generate(state="RJ")
```

### TelefoneBR (Fixo e Celular)

```python
from pydantic_brasil import TelefoneBR

tel = TelefoneBR("+55 (11) 98765-4321")
tel.digits         # "11987654321"
tel.formatted      # "(11) 98765-4321"
tel.e164           # "+5511987654321"
tel.whatsapp_link  # "https://wa.me/5511987654321"
tel.ddd            # "11"
tel.is_mobile      # True

tel_fake = TelefoneBR.generate(ddd=21, mobile=True)
```

### Chave PIX

Auto-identifica e valida os 5 formatos oficiais do Banco Central:

```python
from pydantic_brasil import ChavePIX, PixKeyType

k1 = ChavePIX("123.456.789-09")            # PixKeyType.CPF
k2 = ChavePIX("contato@empresa.com.br")     # PixKeyType.EMAIL
k3 = ChavePIX("+5511987654321")             # PixKeyType.PHONE
k4 = ChavePIX("550e8400-e29b-41d4-a716-446655440000") # PixKeyType.EVP

print(k1.normalized)  # "12345678909"
print(k3.normalized)  # "+5511987654321"
print(k2.masked)      # "c*****o@empresa.com.br"

# Gerar chave aleatória EVP válida
chave_aleatoria = ChavePIX.generate_evp()
```

### DinheiroBRL (Precisão Monetária)

Evite erros de arredondamento inerentes a números de ponto flutuante (`float`). `DinheiroBRL` usa `Decimal` internamente:

```python
from pydantic_brasil import DinheiroBRL

preco = DinheiroBRL("R$ 1.500,50")
print(preco.centavos)   # 150050 (int, perfeito para gateways)
print(preco.formatted)  # "R$ 1.500,50"

# Instanciação direta por centavos
taxa = DinheiroBRL.from_centavos(250) # R$ 2,50

# Aritmética nativa
total = preco + taxa
print(total.formatted)  # "R$ 1.503,00"
```

### Placa Veicular (Mercosul e Tradicional)

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

## 🧪 Qualidade de Código e Testes

```bash
# Executa a suite de testes com relatório de cobertura
pytest --cov=pydantic_brasil --cov-report=term-missing

# Checagem estrita de tipos
mypy pydantic_brasil tests

# Lint e formatação
flake8
black --check .
```

---

## 🤝 Contribuições

Contribuições são muito bem-vindas! Sinta-se à vontade para abrir uma issue ou pull request.

1. Faça um Fork do projeto
2. Crie sua branch de funcionalidade (`git checkout -b feature/MinhaFeature`)
3. Faça commit das suas alterações (`git commit -m 'feat: Minha nova funcionalidade'`)
4. Envie para o branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

---

## 📄 Licença

Distribuído sob a Licença MIT. Consulte o arquivo `LICENSE` para mais detalhes.
