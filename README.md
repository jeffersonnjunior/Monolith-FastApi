# Monolith FastAPI

Backend FastAPI com arquitetura modular, banco PostgreSQL assíncrono, migrations com Alembic

## Stack

- Python 3.13
- FastAPI
- SQLAlchemy 2.x (async)
- asyncpg
- Alembic
- PostgreSQL
- Docker Compose
- Pytest + pytest-asyncio

## Estrutura de banco

- `app/core/config`: settings e variáveis por ambiente
- `app/core/db`: engine async, session factory, health check, lifecycle
- `app/core/deps`: injeções (sessão por request)
- `app/models`: entidades ORM e metadata
- `app/dao/repositories`: acesso a dados por repositório
- `migrations`: Alembic + versões

## Variáveis de ambiente

| Variável | Descrição | Default |
|---|---|---|
| `APP_NAME` | Nome da aplicação | `Monolith FastAPI` |
| `APP_ENV` | Ambiente | `local` |
| `APP_DEBUG` | Debug FastAPI | `true` |
| `APP_LOG_LEVEL` | Nível de log | `INFO` |
| `APP_API_V1_PREFIX` | Prefixo da API | `/api/v1` |
| `DB_URL` | URL async do banco | `postgresql+asyncpg://postgres:postgres@localhost:5432/monolith` |
| `DB_ECHO` | Log SQL | `false` |
| `DB_POOL_SIZE` | Tamanho do pool | `10` |
| `DB_MAX_OVERFLOW` | Overflow do pool | `20` |
| `DB_POOL_TIMEOUT` | Timeout do pool (s) | `30` |
| `DB_POOL_RECYCLE` | Recycle do pool (s) | `1800` |
| `DB_POOL_PRE_PING` | Verifica conexão antes de usar | `true` |

## Setup local (sem Docker para API)

1. Instalar dependências:

   ```bash
   uv sync
   ```

2. Subir apenas o PostgreSQL:

   ```bash
   docker compose up -d postgres
   ```

3. Rodar migrations:

   ```bash
   uv run db-upgrade
   ```

4. Subir API:

   ```bash
   uv run run
   ```

## Setup full Docker Compose

```bash
docker compose up --build
```

## Migrations

- Nova revision autogerada:
  ```bash
  uv run db-revision -m "mensagem_da_migration"
  ```
- Aplicar migration:
  ```bash
  uv run db-upgrade
  ```
- Reverter última migration:
  ```bash
  uv run db-downgrade
  ```

## Comandos úteis

- Rodar app: `uv run run`
- Testes: `uv run test`
- Lint: `uv run lint`
- Formatação: `uv run fmt`
- Typecheck: `uv run typecheck`

## Healthcheck

`GET /api/v1/health` retorna:
- status da aplicação
- metadados de versão/ambiente
- status do banco (`up`/`down`)

## Troubleshooting

- **Conexão recusada com banco**: verifique `DB_URL` e se o container `postgres` está saudável (`docker compose ps`).
- **Timeout de pool**: aumente `DB_POOL_SIZE`, `DB_MAX_OVERFLOW` ou revise queries longas.
- **Migrations não detectam modelo**: confirme import do modelo em `migrations/env.py`.
- **Erro de driver**: valide se `asyncpg` está instalado no ambiente (`uv sync`).
