# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [0.3.0] - 2026-10-02

### Adicionado
- **`ChaveDFe`** (`ChaveAcessoNFe`, `ChaveNFe`) — Chave de acesso SEFAZ 44 dígitos (NF-e 55, NFC-e 65, CT-e 57, MDF-e 58). Módulo 11. Propriedades: `uf_ibge`, `ano`, `mes`, `cnpj_emitente`, `modelo`, `serie`, `numero_nf`, `tipo_emissao`, `codigo_numerico`. Método `.generate()`.
- **`BoletoBancario`** (`LinhaDigitavel`, `CodigoBarrasBoleto`) — Boleto bancário 47 dígitos e arrecadação 48 dígitos (FEBRABAN). Módulo 10 e 11, conversão linha digitável ↔ código de barras, data de vencimento com fator pós-virada 2025, extração de `DinheiroBRL`.
- **`RastreioCorreios`** (`CodigoRastreio`) — Rastreio Correios 13 caracteres (UPU S10), Módulo 11 ponderado, `categoria_servico`, `tracking_url`. Método `.generate()`.
- **`GTIN`** (`EAN`, `EAN13`) — GTIN-8/12/13/14 (GS1). Módulo 10 pesos alternados 3/1. Prefixo brasileiro 789/790. Método `.generate()`.
- **`IBANBrasil`** (`IBAN`) — IBAN 29 caracteres (Bacen Circular 3.625). ISO 7064 Módulo 97. Propriedades: `ispb`, `agencia`, `conta`, `tipo_conta`, `titular`. Método `.generate()`.
- Base: controle `SERIALIZE_AS_DIGITS: ClassVar[bool]` em `BrazilianType` para tipos alfanuméricos.

### Alterado
- README atualizado com 22 tipos suportados.
- `pyproject.toml`: versão `0.3.0`, keywords expandidas.

---

## [0.2.0] - 2026-10-02

### Adicionado
- **`PIS`** (`PASEP`) — PIS/PASEP 11 dígitos com DV ponderado.
- **`TituloEleitor`** — Título de eleitor 12 dígitos, DV duplo e mapeamento de UF.
- **`CNS`** — Cartão Nacional de Saúde provisório e definitivo (15 dígitos).
- **`ProcessoCNJ`** — Número único de processo judicial CNJ (20 dígitos).
- **`CertidaoCivil`** — Certidão de nascimento/casamento/óbito (32 dígitos).
- **`BancoBR`** — Código de banco (3 dígitos, 200+ bancos FEBRABAN/ISPB).
- Tradução completa do projeto para pt-BR.

### Removido
- `README.en.md` — README agora é exclusivamente em pt-BR.

---

## [0.1.0] - 2026-10-01

### Adicionado
- **`CPF`** — Validação com Módulo 11.
- **`CNPJ`** — Numérico e alfanumérico 2026 (IN RFB 2.229/2024).
- **`CEP`** — Máscara `00000-000`.
- **`TelefonesBR`** (`TelefoneCelular`, `TelefoneFixo`) — Validação de DDD e número.
- **`ChavePix`** — CPF, CNPJ, e-mail, telefone ou EVP (UUID v4).
- **`DinheiroBRL`** — Tipo monetário BRL com `Decimal`.
- **`PlacaVeiculo`** (`PlacaMercosul`, `PlacaTradicional`) — Formatos antigo e Mercosul.
- **`RENAVAM`** — Módulo 11.
- **`CNH`** — DV duplo.
- **`InscricaoEstadual`** — 27 estados + DF.
- Suporte nativo Pydantic v2 core schema, integração FastAPI/OpenAPI, tipagem PEP 561.
