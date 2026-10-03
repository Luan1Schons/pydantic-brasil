# Como Contribuir

Obrigado pelo interesse em contribuir com o **pydantic-brasil**! 🇧🇷

## Reportar um Bug

Abra uma [issue](https://github.com/Luan1Schons/pydantic-brasil/issues/new?template=bug_report.md) descrevendo:
- Versão do pydantic-brasil e Python
- Código mínimo para reproduzir o erro
- Comportamento esperado vs. observado

## Sugerir um Novo Tipo

Abra uma [issue](https://github.com/Luan1Schons/pydantic-brasil/issues/new?template=feature_request.md) com:
- Nome do tipo e descrição
- Referência normativa oficial (RFB, FEBRABAN, Bacen, etc.)
- Algoritmo do dígito verificador (se aplicável)

## Contribuir com Código

### Pré-requisitos

```bash
git clone https://github.com/Luan1Schons/pydantic-brasil
cd pydantic-brasil
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

### Padrão de Implementação

Todo novo tipo deve:
1. Herdar de `BrazilianType` em `pydantic_brasil/base.py`
2. Implementar `_validate()` com mensagens de erro em **pt-BR**
3. Ter método `.generate()` que retorna valor válido aleatório
4. Ser exportado em `pydantic_brasil/__init__.py`
5. Ter testes com cobertura ≥ 90% em `tests/test_<nome>.py`

### Quality Gates (obrigatório antes do PR)

```bash
black pydantic_brasil tests
flake8 pydantic_brasil tests
mypy pydantic_brasil tests
pytest
```

### Pull Request

- Branch: `feat/<nome-do-tipo>` ou `fix/<descricao>`
- Título: Conventional Commits (`feat: add NovaTipo`)
- Descrição: referência normativa, algoritmo do DV, exemplos válidos e inválidos

## Código de Conduta

Este projeto segue o [Contributor Covenant](https://www.contributor-covenant.org/pt-br/).
