# pydantic-brasil 🇧🇷

[![PyPI version](https://img.shields.io/pypi/v/pydantic-brasil?color=blue&style=flat-square)](https://pypi.org/project/pydantic-brasil/)
[![Python versions](https://img.shields.io/pypi/pyversions/pydantic-brasil?style=flat-square)](https://pypi.org/project/pydantic-brasil/)
[![CI Tests](https://github.com/Luan1Schons/pydantic-brasil/actions/workflows/test.yml/badge.svg)](https://github.com/Luan1Schons/pydantic-brasil/actions/workflows/test.yml)
[![Coverage](https://img.shields.io/badge/coverage-94%25-brightgreen?style=flat-square)](https://github.com/Luan1Schons/pydantic-brasil)
[![Pydantic v2](https://img.shields.io/badge/pydantic-v2-E92063?logo=pydantic&logoColor=white&style=flat-square)](https://docs.pydantic.dev/)
[![Types](https://img.shields.io/badge/typing-Mypy%20Strict-blue?style=flat-square)](https://mypy.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](https://opensource.org/licenses/MIT)

**Modern, high-performance Brazilian data types and validators built natively for Pydantic v2 and FastAPI.**

*Documentação principal em Português disponível em [README.md](README.md).*

---

## 📦 Supported Brazilian Types (17 Types)

- **Personal & Tax**: `CPF`, `CNPJ` (Traditional + 2026 Alphanumeric), `CPFouCNPJ` (`DocumentoBR`), `InscricaoEstadual`
- **Address & Banking**: `CEP`, `TelefoneBR`, `ChavePIX` (`PixKey`), `DinheiroBRL` (`BRL`), `BancoBR` (`CodigoBanco`)
- **Labor, Health & Civic**: `PIS` (`PASEP`, `NIS`, `NIT`), `CNS` (`CartaoSUS`), `TituloEleitor` (`TituloEleitoral`), `CertidaoCivil` (`Certidao`), `ProcessoCNJ` (`ProcessoJudicial`)
- **Vehicles & Transit**: `PlacaVeiculo` (Mercosul + Legacy), `RENAVAM`, `CNH`

For full documentation, usage examples, and guides, refer to [README.md](README.md).
