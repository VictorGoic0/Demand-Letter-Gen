# Demand Letter Generator — Backend

Python 3.11+ FastAPI services, AWS Lambda deployment (Serverless), PostgreSQL (Alembic), S3, OpenAI.

## Prerequisites

- **Docker & Docker Compose** — local PostgreSQL and optional containerized API
- **Python 3.11+** — use a **project virtual environment** (do not install packages globally)
- **Node.js 18+** — Serverless CLI and `npm` scripts in this folder

## Virtual environment (required for host-side commands)

Create and use a venv under `api/.venv` (gitignored):

```bash
cd api
python3 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
```

Keep the venv activated when running **Python**, **Alembic**, **uvicorn**, **ruff**, or **`npm run lint` / `lint:fix` / `format`** here — those scripts invoke tools installed in the venv.

## Environment variables

Create **`api/.env`** for local development (see also `shared/config.py` / `get_settings()`). Example:

```env
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO

DB_HOST=postgres
DB_PORT=5432
DB_NAME=demand_letters
DB_USER=dev_user
DB_PASSWORD=dev_password

AWS_ACCESS_KEY_ID=<key>
AWS_SECRET_ACCESS_KEY=<key>
AWS_REGION=us-east-2
S3_BUCKET_DOCUMENTS=<documents-bucket>
S3_BUCKET_EXPORTS=<exports-bucket>

OPENAI_API_KEY=<key>
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7

CORS_ALLOW_ORIGINS=*
```

**Production deploy:** load secrets before Serverless commands, e.g. `source load-env-production.sh` (expects `api/.env.production`), then `npm run deploy:prod`. See [`../docs/lambda-deployment.md`](../docs/lambda-deployment.md) and `serverless.yml`.

## Local development

### Option A: Docker Compose (database + API)

From `api/`:

```bash
docker-compose up
```

Apply migrations (with venv activated, or `docker-compose exec`):

```bash
alembic upgrade head
```

- API: http://localhost:8000  
- Docs: http://localhost:8000/docs  

### Option B: API on the host (uvicorn)

With Postgres reachable (e.g. Compose up for `postgres` only, or local DB) and `.env` set:

```bash
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

`main.py` is the **local dev** all-in-one app; Lambda uses per-service `handler.py` files.

## Database migrations (Alembic)

```bash
cd api
source .venv/bin/activate
alembic upgrade head
```

Helpers (from repo root or `api/`):

- `./scripts/migrate-up.sh`
- `./scripts/migrate-down.sh`
- `./scripts/migrate-create.sh "message"`

Create migration after model changes under `shared/models/`:

```bash
alembic revision --autogenerate -m "Description"
```

Review generated files in `alembic/versions/` before applying. Never edit migrations already applied in production.

## Linting and formatting

Uses **Ruff** (`pyproject.toml`). Workflow matches `.cursor/rules/linting.mdc`:

```bash
source .venv/bin/activate
ruff check .
ruff check --fix .
ruff format .
```

Or:

```bash
npm run lint
npm run lint:fix
npm run format
```

## Optional checks

**DB connectivity / schema (`test_db.py`):**

```bash
source .venv/bin/activate
python test_db.py
```

Or from the API container: `docker-compose exec api python test_db.py`.

## Layout (high level)

| Path | Role |
|------|------|
| `main.py` | Local FastAPI app wiring all routers |
| `services/` | Per-service `router.py`, `logic.py`, `schemas.py`, `handler.py` |
| `shared/` | Config (`get_settings()`), DB (`get_db()`), S3, exceptions, models |
| `alembic/` | Migrations |
| `handlers/` | Shared Lambda handler utilities |
| `scripts/` | Checks, seeds, tests, Alembic wrappers (`migrate-*.sh`) |
| `serverless.yml` | Lambda functions and API Gateway |

Architecture rules are documented in **`.cursor/rules/api-patterns.mdc`** (firm scoping, no direct `os.getenv` in services — use `get_settings()`, S3 via `get_s3_client()`, etc.).

## Related docs

- [Docker local setup](../docs/docker-local-setup.md)  
- [Lambda deployment](../docs/lambda-deployment.md)  
- [S3 usage](../docs/s3-usage.md)  
- [S3 bucket setup](../docs/s3-bucket-setup.md)  
