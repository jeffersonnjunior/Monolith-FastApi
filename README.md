# Monolith FastAPI

Esqueleto profissional de backend em FastAPI com estrutura modular por pacotes, tipagem estática e tooling de qualidade desde o início.

## Requisitos

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)

## Setup

1. Criar ambiente e instalar dependências:

   ```bash
   uv sync
   ```

2. Criar arquivo de ambiente local:

   ```bash
   cp .env.example .env
   ```

3. Instalar hooks de pre-commit:

   ```bash
   uv run pre-commit install
   ```

## Comandos úteis

- Rodar aplicação:

  ```bash
  uv run run
  ```

- Lint:

  ```bash
  uv run lint
  ```

- Formatação:

  ```bash
  uv run fmt
  ```

- Type check:

  ```bash
  uv run typecheck
  ```

- Testes:

  ```bash
  uv run test
  ```

## Endpoint inicial

- `GET /api/v1/health`

Resposta esperada:

```json
{
  "status": "ok",
  "service": "Monolith FastAPI",
  "version": "0.1.0",
  "environment": "local"
}
```