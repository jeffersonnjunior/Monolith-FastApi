# Monolith FastAPI

Esqueleto profissional de backend em FastAPI com estrutura modular por pacotes, tipagem estática e tooling de qualidade desde o início.

## Requisitos

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)

## Setup

1. Instalar dependências:

   ```bash
   uv sync
   ```

2. (Opcional) Criar arquivo `.env` para sobrescrever variáveis padrão.

3. Instalar hooks:

   ```bash
   uv run pre-commit install
   ```

## Comandos

- Rodar app: `uv run run`
- Lint: `uv run lint`
- Formatar: `uv run fmt`
- Typecheck: `uv run typecheck`
- Testes: `uv run test`

## Endpoint inicial

- `GET /api/v1/health`