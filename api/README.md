# Demand Letter Generator — Backend

Python 3.11+ FastAPI application, PostgreSQL (Alembic), S3, OpenAI. Runs as a standard ASGI process (uvicorn); local development uses Docker Compose for PostgreSQL and the API together.

## Prerequisites

- **Docker & Docker Compose** — recommended for PostgreSQL + API together
- **Python 3.11+** — use a **project virtual environment** (do not install packages globally)

## Virtual environment (required for host-side commands)

Create and use a venv under `api/.venv` (gitignored):

```bash
cd api
python3 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
```

Keep the venv activated when running **Python**, **Alembic**, **uvicorn**, or **ruff**.

## Environment variables

Copy **`api/.env.example`** to **`api/.env`** and fill in values. Docker Compose reads **`api/.env`** automatically for variable substitution (same directory as `docker-compose.yml`).

Key variables (see `shared/config.py` / `get_settings()`):

```env
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO

DB_HOST=postgres
DB_PORT=5432
DB_NAME=demand_letters
DB_USER=dev_user
DB_PASSWORD=dev_password

AWS_REGION=us-east-2
AWS_S3_BUCKET_DOCUMENTS=<documents-bucket>
AWS_S3_BUCKET_EXPORTS=<exports-bucket>
AWS_ACCESS_KEY_ID=<optional>
AWS_SECRET_ACCESS_KEY=<optional>

OPENAI_API_KEY=<key>
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7

CORS_ALLOW_ORIGINS=http://localhost:5173,http://localhost:3000
```

For production, set **`CORS_ALLOW_ORIGINS`** to your real frontend origins (comma-separated). Do not hardcode origins in Python.

## Local development

### Docker Compose (PostgreSQL + API)

From `api/`:

```bash
cp .env.example .env   # then edit .env
docker compose up --build
```

Apply migrations (with venv activated on the host, or `docker compose exec`):

```bash
alembic upgrade head
```

- API: http://localhost:8000  
- Docs: http://localhost:8000/docs  

See **[../docs/docker-local-setup.md](../docs/docker-local-setup.md)** for details.

### API on the host (uvicorn)

With PostgreSQL reachable (e.g. Compose running only `postgres`) and `api/.env` pointing at `DB_HOST=localhost`:

```bash
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

`main.py` is the application entrypoint — it registers all routers.

### Production-style container (no reload)

The **`Dockerfile`** default command runs uvicorn without `--reload`. Compose overrides that for local dev.

```bash
docker build -t dlg-api .
docker run --env-file .env -p 8000:8000 dlg-api
```

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

Uses **Ruff** (`pyproject.toml`):

```bash
source .venv/bin/activate
ruff check .
ruff check --fix .
ruff format .
```

## Layout (high level)

| Path | Role |
|------|------|
| `main.py` | FastAPI app — wires all routers, lifespan, CORS |
| `services/` | Per-service `router.py`, `logic.py`, `schemas.py` |
| `shared/` | Config (`get_settings()`), DB (`get_db()`), S3, exceptions, models |
| `alembic/` | Migrations |
| `scripts/` | Checks, seeds, tests, Alembic wrappers (`migrate-*.sh`) |
| `Dockerfile` | Container image for the API |
| `docker-compose.yml` | PostgreSQL + API for local development |

Architecture rules are documented in **`.cursor/rules/api-patterns.mdc`** (firm scoping, no direct `os.getenv` in services — use `get_settings()`, S3 via `get_s3_client()`, etc.).

## Related docs

- [Docker local setup](../docs/docker-local-setup.md)  
- [Remove Lambda migration notes](../docs/remove-lambda.md)  
- [S3 usage](../docs/s3-usage.md)  
- [S3 bucket setup](../docs/s3-bucket-setup.md)  

Historical Lambda + Serverless deployment notes are archived in **[lambda-deployment.md](../docs/lambda-deployment.md)** (superseded by Docker).
