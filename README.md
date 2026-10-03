# pydantic-brasil 🇧🇷

[![Versão PyPI](https://img.shields.io/pypi/v/pydantic-brasil?color=blue&style=flat-square)](https://pypi.org/project/pydantic-brasil/)
[![Versões Python](https://img.shields.io/pypi/pyversions/pydantic-brasil?style=flat-square)](https://pypi.org/project/pydantic-brasil/)
[![Downloads/mês](https://img.shields.io/pypi/dm/pydantic-brasil?color=blue&label=downloads%2Fm%C3%AAs&style=flat-square)](https://pypistats.org/packages/pydantic-brasil)
[![Total de Downloads](https://img.shields.io/pepy/dt/pydantic-brasil?color=green&label=total%20downloads&style=flat-square)](https://pepy.tech/project/pydantic-brasil)
[![Testes de CI](https://github.com/Luan1Schons/pydantic-brasil/actions/workflows/test.yml/badge.svg)](https://github.com/Luan1Schons/pydantic-brasil/actions/workflows/test.yml)
[![Cobertura](https://img.shields.io/badge/coverage-94%25-brightgreen?style=flat-square)](https://github.com/Luan1Schons/pydantic-brasil)
[![Pydantic v2](https://img.shields.io/badge/pydantic-v2-E92063?logo=pydantic&logoColor=white&style=flat-square)](https://docs.pydantic.dev/)
[![Tipagem Estrita](https://img.shields.io/badge/typing-Mypy%20Strict-blue?style=flat-square)](https://mypy.readthedocs.io/)
[![Licença: MIT](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Stars](https://img.shields.io/github/stars/Luan1Schons/pydantic-brasil?style=social)](https://github.com/Luan1Schons/pydantic-brasil)

**Tipos de dados e validadores brasileiros modernos e de alta performance desenvolvidos nativamente para Pydantic v2 e FastAPI.**

---

## 💡 Por que usar o pydantic-brasil?

- **🚀 Desenvolvido nativamente para Pydantic v2**: Conectado diretamente ao núcleo `pydantic-core` via `__get_pydantic_core_schema__`, sem hacks ou regexes lentas de pré-validação.
- **🛡️ Pronto para o CNPJ Alfanumérico 2026**: Compatibilidade completa tanto com o CNPJ numérico tradicional quanto com o novo padrão alfanumérico regulamentado pela Receita Federal do Brasil.
- **🔒 Mascaramento em conformidade com a LGPD**: Propriedade `.masked` nativa em todos os documentos (`123.***.***-00`) para exibição em interfaces, logs seguros e telemetria.
- **🗄️ Otimizado para Bancos de Dados**: `model_dump()` serializa documentos, telefones e CEPs diretamente em dígitos puros e desformatados (`"12345678900"`), permitindo indexação eficiente em PostgreSQL, MySQL, SQLite e MongoDB.
- **📦 Sem Dependências Externas**: Construído unicamente sobre `pydantic>=2.0.0` e `typing-extensions`. Não traz pacotes pesados ou desatualizados.
- **🎯 100% Tipado (PEP 561)**: Total compatibilidade com IDEs (VS Code, Cursor, PyCharm) e checadores estritos como `mypy --strict` e `pyright`.
- **🧪 Geradores de Dados Válidos para Testes**: Todos os documentos contam com `.generate()` para acelerar a criação de fixtures e testes automatizados.
- **🌐 Suporte OpenAPI / FastAPI**: Documentação interativa Swagger UI (`/docs`) e Redoc geradas automaticamente com exemplos e descrições ricas.

---

## 📦 Tipos Brasileiros Suportados (22 Tipos)

### Documentos Pessoais, Fiscais e E-commerce
| Tipo | Alias | Propriedades Principais | Descrição |
| :--- | :--- | :--- | :--- |
| `CPF` | — | `.fiscal_region`, `.formatted`, `.digits`, `.masked`, `.generate()` | Cadastro de Pessoas Físicas com Módulo 11 e região fiscal emissora. |
| `CNPJ` | — | `.is_matriz`, `.is_filial`, `.branch_number`, `.formatted`, `.digits`, `.masked`, `.generate()` | Cadastro Nacional da Pessoa Jurídica (tradicional + alfanumérico 2026). |
| `CPFouCNPJ` | `DocumentoBR` | `.is_cpf`, `.is_cnpj`, `.as_cpf()`, `.as_cnpj()` | Documento fiscal polimórfico com auto-detecção entre CPF e CNPJ. |
| `InscricaoEstadual` | — | `.state`, `.is_isento`, `.formatted`, `.digits`, `.masked` | Validação específica por UF (SP, RJ, MG, RS, PR, SC), produtor rural 'P' e ISENTO. |
| `ChaveDFe` | `ChaveAcessoNFe`, `ChaveNFe` | `.uf`, `.ano_mes`, `.cnpj_emitente`, `.modelo`, `.serie`, `.numero`, `.formatted`, `.generate()` | Chave oficial de 44 dígitos da SEFAZ para NF-e, NFC-e, CT-e e MDF-e com Módulo 11. |
| `GTIN` | `EAN`, `EAN13` | `.is_brazilian`, `.gtin_type`, `.dv`, `.formatted`, `.masked`, `.generate()` | Código de Barras GS1 (GTIN-8, 12, 13 e 14) com detecção de produtos brasileiros (789/790). |

### Endereço, Logística e Meios de Pagamento
| Tipo | Alias | Propriedades Principais | Descrição |
| :--- | :--- | :--- | :--- |
| `CEP` | — | `.state`, `.formatted`, `.digits`, `.generate()` | Código de Endereçamento Postal com inferência automática de UF. |
| `RastreioCorreios` | `CodigoRastreio` | `.service_code`, `.serial_number`, `.origin_country`, `.is_national`, `.tracking_url`, `.generate()` | Rastreamento de encomendas dos Correios no padrão internacional S10 da UPU (13 caracteres). |
| `TelefoneBR` | — | `.ddd`, `.e164`, `.whatsapp_link`, `.is_mobile`, `.is_landline`, `.generate()` | Celular (9 dígitos) e fixo (8 dígitos) com validação de DDDs da ANATEL e link WhatsApp. |
| `ChavePIX` | `PixKey` | `.key_type`, `.normalized`, `.formatted`, `.masked`, `.generate_evp()` | Validação e tipagem oficial Bacen (CPF, CNPJ, E-mail, Telefone, Chave Aleatória/EVP). |
| `BoletoBancario` | `LinhaDigitavel`, `CodigoBarrasBoleto` | `.codigo_barras`, `.linha_digitavel`, `.banco`, `.data_vencimento`, `.valor`, `.is_arrecadacao`, `.generate()` | Boletos de cobrança (47 dígitos) e arrecadação/concessionárias (48 dígitos) FEBRABAN. |
| `IBANBrasil` | `IBAN` | `.country_code`, `.check_digits`, `.ispb`, `.banco`, `.agencia`, `.conta`, `.tipo_conta`, `.generate()` | Conta Internacional Brasileira regulamentada pelo Bacen (29 caracteres) com Módulo 97. |
| `DinheiroBRL` | `BRL` | `.centavos`, `.formatted`, `from_centavos()`, operações matemáticas | Precisão monetária financeira via `Decimal` (evita bugs de arredondamento de float). |
| `BancoBR` | `CodigoBanco` | `.code`, `.name`, `.short_name`, `.ispb`, `.formatted`, `search()` | Catálogo oficial de bancos e instituições de pagamento homologadas no Bacen. |

### Cidadania, Trabalho e Saúde
| Tipo | Alias | Propriedades Principais | Descrição |
| :--- | :--- | :--- | :--- |
| `PIS` | `PASEP`, `NIS`, `NIT` | `.formatted`, `.digits`, `.masked`, `.generate()` | Identificação do trabalhador CLT / servidor com verificação Módulo 11. |
| `TituloEleitor` | `TituloEleitoral` | `.state`, `.uf_code`, `.formatted`, `.digits`, `.masked`, `.generate()` | Título eleitoral com validação de UF e dois dígitos verificadores (TSE). |
| `CNS` | `CartaoSUS` | `.is_definitivo`, `.is_provisorio`, `.formatted`, `.digits`, `.masked`, `.generate()` | Cartão Nacional de Saúde (SUS) definitivo (1, 2) e provisório (7, 8, 9). |
| `CertidaoCivil` | `Certidao` | `.year`, `.type_code`, `.type_name`, `.cartorio_cns`, `.formatted`, `.generate()` | Padrão unificado do CNJ (32 dígitos) para Nascimento, Casamento e Óbito. |
| `ProcessoCNJ` | `ProcessoJudicial` | `.year`, `.segment_id`, `.segment_name`, `.tribunal`, `.formatted`, `.generate()` | Numeração Única de Processos Judiciais (20 dígitos) com Módulo 97 (ISO 7064). |

### Trânsito e Veículos
| Tipo | Alias | Propriedades Principais | Descrição |
| :--- | :--- | :--- | :--- |
| `PlacaVeiculo` | — | `.is_mercosul`, `.is_antiga`, `.to_mercosul()`, `.to_antiga()` | Placas padrão Mercosul (`ABC1D23`) e padrão antigo cinza (`ABC-1234`) com conversão. |
| `RENAVAM` | — | `.formatted`, `.digits`, `.masked`, `.generate()` | Registro Nacional de Veículos Automotores (11 dígitos) com Módulo 11. |
| `CNH` | — | `.formatted`, `.digits`, `.masked`, `.generate()` | Carteira Nacional de Habilitação (11 dígitos) com verificação dupla de DV. |

---

## 🚀 Instalação

```bash
pip install pydantic-brasil
```

Ou com Poetry:

```bash
poetry add pydantic-brasil
```

Ou com uv:

```bash
uv add pydantic-brasil
```

---

## 🛠️ Exemplos de Uso

### 1. Modelo de Cadastro Completo

```python
from pydantic import BaseModel
from pydantic_brasil import (
    CPF,
    CNPJ,
    CEP,
    TelefoneBR,
    ChavePIX,
    DinheiroBRL,
    PIS,
    CNS,
    BancoBR,
)

class Cliente(BaseModel):
    nome: str
    cpf: CPF
    cnpj_empresa: CNPJ
    cep: CEP
    telefone: TelefoneBR
    chave_pix: ChavePIX
    limite_credito: DinheiroBRL
    pis: PIS
    cns: CNS
    banco: BancoBR

# Aceita pontuado, dígitos puros, inteiros, etc.
cliente = Cliente(
    nome="Ana Souza",
    cpf="123.456.789-09",
    cnpj_empresa="12.ABC.345/0001-67",  # Suporta CNPJ alfanumérico 2026!
    cep="01310-100",
    telefone="(11) 98765-4321",
    chave_pix="ana.souza@email.com",
    limite_credito="R$ 15.000,50",
    pis="120.41440.45-9",
    cns="123 4567 8901 0002",
    banco="Nubank",  # Busca automática por nome comercial ou código COMPE ("260")
)

# Acesso a propriedades ricas
print(cliente.cpf.formatted)          # "123.456.789-09"
print(cliente.cpf.masked)             # "123.***.***-09" (Seguro para LGPD)
print(cliente.cpf.fiscal_region)      # ["SP"]

print(cliente.telefone.e164)          # "+5511987654321"
print(cliente.telefone.whatsapp_link) # "https://wa.me/5511987654321"

print(cliente.chave_pix.key_type)     # PixKeyType.EMAIL
print(cliente.limite_credito.centavos)# 1500050 (int puro, ideal para gateways como Asaas/Pagar.me)

print(cliente.banco.code)             # "260"
print(cliente.banco.name)             # "Nu Pagamentos S.A. - Instituição de Pagamento"
print(cliente.banco.ispb)             # "18236120"

# Serialização limpa para salvar no banco de dados:
print(cliente.model_dump())
# {
#     "nome": "Ana Souza",
#     "cpf": "12345678909",
#     "cnpj_empresa": "12ABC345000167",
#     "cep": "01310100",
#     "telefone": "11987654321",
#     "chave_pix": "ana.souza@email.com",
#     "limite_credito": 15000.5,
#     "pis": "12041440459",
#     "cns": "123456789010002",
#     "banco": "260"
# }
```

### 2. Integração com FastAPI

Os tipos do `pydantic-brasil` geram metadados OpenAPI automaticamente:

```python
from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_brasil import CPF, ChavePIX, DinheiroBRL

app = FastAPI(title="API de Pagamentos PIX")

class SolicitacaoTransferencia(BaseModel):
    cpf_origem: CPF
    chave_pix_destino: ChavePIX
    valor: DinheiroBRL

@app.post("/transferir")
def transferir(dados: SolicitacaoTransferencia):
    return {
        "status": "sucesso",
        "tipo_chave": dados.chave_pix_destino.key_type,
        "chave_destino": dados.chave_pix_destino.normalized,
        "valor_em_centavos": dados.valor.centavos,
        "pagador": dados.cpf_origem.masked,
    }
```

---

## 🔍 Exemplos Práticos por Domínio

### CNPJ Alfanumérico 2026

A partir de 2026, a Receita Federal do Brasil passa a emitir CNPJs com caracteres alfanuméricos na base (`12.ABC.345/0001-67`). O `pydantic-brasil` suporta ambas as especificações:

```python
from pydantic_brasil import CNPJ

# CNPJ tradicional
cnpj_antigo = CNPJ("12.345.678/0001-95")

# CNPJ alfanumérico 2026
cnpj_novo = CNPJ("12.ABC.345/0001-67")
print(cnpj_novo.is_matriz)      # True
print(cnpj_novo.branch_number)  # "0001"
print(cnpj_novo.masked)         # "12.***.***/0001-67"
```

### Processo Judicial CNJ (Numeração Única)

Validação matemática estrita de processos judiciais utilizando Módulo 97 (ISO 7064):

```python
from pydantic_brasil import ProcessoCNJ

proc = ProcessoCNJ("0001234-71.2024.8.26.0100")
print(proc.year)         # 2024
print(proc.segment_name) # "Justiça dos Estados e do Distrito Federal"
print(proc.tribunal)     # "26" (TJSP)
print(proc.origin)       # "0100" (Comarca da Capital)
```

### Título de Eleitor e Identificação de UF

```python
from pydantic_brasil import TituloEleitor

titulo = TituloEleitor.generate(state="MG")
print(titulo.state)      # "MG"
print(titulo.uf_code)    # "02"
print(titulo.formatted)  # "1234 5678 02 14"
```

### Conversão de Placas de Veículos (Mercosul ↔ Antiga)

```python
from pydantic_brasil import PlacaVeiculo

placa = PlacaVeiculo("ABC-1234")
print(placa.is_antiga)       # True
print(placa.to_mercosul())   # "ABC1C34"

mercosul = PlacaVeiculo("ABC1C34")
print(mercosul.is_mercosul)  # True
print(mercosul.to_antiga())  # "ABC-1234"
```

### Dinheiro BRL e Precisão Financeira

```python
from pydantic_brasil import DinheiroBRL

preco = DinheiroBRL("R$ 1.250,50")
print(preco.centavos)   # 125050 (int)
print(preco.formatted)  # "R$ 1.250,50"

# Criar a partir de centavos recebidos de gateway
tarifa = DinheiroBRL.from_centavos(490) # R$ 4,90

total = preco + tarifa
print(total.formatted)  # "R$ 1.255,40"
```

### Catálogo de Bancos Brasileiros (COMPE / ISPB)

```python
from pydantic_brasil import BancoBR

# Por código numérico (ex: 1 é normalizado para "001")
banco1 = BancoBR(1)          # Banco do Brasil ("001")
banco2 = BancoBR("260")      # Nubank
banco3 = BancoBR("Inter")    # Busca por nome -> "077"

# Busca rápida de bancos no catálogo Bacen
bancos_cooperativos = BancoBR.search("cooperativo")
```

### Chave de Acesso DF-e (NF-e, NFC-e, CT-e, MDF-e)

Validação matemática de 44 dígitos no Módulo 11 da SEFAZ com extração completa de metadados:

```python
from pydantic_brasil import ChaveDFe

chave = ChaveDFe("352410000000000000550010000123451123456781")
print(chave.uf)             # "SP"
print(chave.uf_code)        # 35
print(chave.year)           # 2024
print(chave.month)          # 10
print(chave.modelo_nome)    # "NF-e (Nota Fiscal Eletrônica)"
print(chave.serie)          # "001"
print(chave.numero)         # "000012345"
print(chave.cnpj_emitente)  # CNPJ("00000000000000")
print(chave.formatted)      # "3524 1000 0000 0000 0055 0010 0001 2345 1123 4567 81"
```

### Boletos Bancários e Linha Digitável (FEBRABAN)

Conversão automática bidirecional entre linha digitável e código de barras, com extração de vencimento e valor:

```python
from pydantic_brasil import BoletoBancario

# Aceita tanto a linha digitável (47 dígitos) quanto o código de barras (44 dígitos)
boleto = BoletoBancario("00190.00009 01234.567802 00000.000001 5 100000000000")
print(boleto.banco.name)        # "Banco do Brasil S.A."
print(boleto.valor.formatted)   # "R$ 100,00"
print(boleto.data_vencimento)   # 2025-02-22 (calculado via fator FEBRABAN)
print(boleto.codigo_barras)     # "00195100000000000000000012345678000000000001"
print(boleto.is_arrecadacao)    # False (ou True se for água/luz/tributo com 48 dígitos)
```

### Rastreamento de Encomendas dos Correios (Padrão S10)

```python
from pydantic_brasil import RastreioCorreios

encomenda = RastreioCorreios("QC123456785BR")
print(encomenda.service_code)   # "QC"
print(encomenda.is_national)    # True
print(encomenda.tracking_url)   # "https://rastreamento.correios.com.br/app/index.php?codigo=QC123456785BR"
print(encomenda.formatted)      # "QC 12345678 5 BR"
```

### IBAN Brasileiro (Conta Internacional Bacen)

```python
from pydantic_brasil import IBANBrasil

iban = IBANBrasil("BR1200000000000010000123456C1")
print(iban.country_code)  # "BR"
print(iban.agencia)       # "00001"
print(iban.conta)         # "0000123456"
print(iban.tipo_conta)    # "C" (Conta Corrente)
print(iban.banco.name)    # "Banco do Brasil S.A."
```

### Código de Barras GTIN / EAN (GS1 Brasil)

```python
from pydantic_brasil import GTIN

produto = GTIN("7891000315507")
print(produto.is_brazilian)  # True (prefixo 789/790 atribuído à GS1 Brasil)
print(produto.gtin_type)     # "GTIN-13" (EAN-13)
```

---

## 🧪 Qualidade, Testes e Tipagem

```bash
# Executar suíte de testes com cobertura de código
pytest --cov=pydantic_brasil --cov-report=term-missing

# Verificação estrita de tipos
mypy pydantic_brasil tests

# Linting e estilo
flake8
black --check .
```

---

## 🤝 Contribuições

Contribuições, correções de bugs e sugestões de novos documentos brasileiros são extremamente bem-vindas!

1. Faça um Fork do projeto
2. Crie uma branch de funcionalidade (`git checkout -b feature/MeuDocumento`)
3. Adicione testes unitários e verifique com `pytest` e `mypy`
4. Envie o commit (`git commit -m 'feat: Adiciona validador para Documento'`)
5. Abra um Pull Request

Consulte o guia completo em [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📋 Changelog

Veja todas as novidades e histórico de versões em [CHANGELOG.md](CHANGELOG.md).

---

## 📄 Licença

Distribuído sob a Licença MIT. Consulte o arquivo `LICENSE` para mais detalhes.

