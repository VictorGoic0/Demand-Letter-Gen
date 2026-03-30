# TDD: Remove Lambda — Normalize Backend to Standard FastAPI Deployment

## Context

The backend was architected for AWS Lambda + API Gateway using the Serverless Framework. This introduced structural artifacts that exist solely to satisfy Lambda's invocation model — not to serve application logic. Now that the project is being restructured, these artifacts should be removed and the backend should run as a standard FastAPI process (uvicorn, Docker container, or any server-based runtime).

---

## What Was Lambda-Driven

The following exist *only* because of Lambda and have no place in a standard server deployment:

| Artifact | Why It Existed | Status After This TDD |
|---|---|---|
| `handlers/` folder (top-level) | Per-service Lambda entrypoints wrapping Mangum | **Delete** |
| `services/*/handler.py` | Per-service mini FastAPI app + Mangum handler | **Delete** |
| `handlers/base.py` | `LambdaHandler`, `create_lambda_app`, `create_handler` (Mangum) | **Delete** |
| `serverless.yml` | Serverless Framework deployment manifest | **Delete** |
| `package.json` / `package-lock.json` | Only existed for Serverless Framework (Node tooling) | **Delete** |
| `load-env-production.sh` | Shell script to load env vars before `npx serverless` | **Delete** |
| `health_handler` in `main.py` | Lambda-style event/context handler at bottom of main | **Remove from main.py** |
| `SERVERLESS_STAGE` env var handling in `base.py` | API Gateway base path from stage name | **Remove from main.py** |
| `mangum` in `requirements.txt` | ASGI-to-Lambda adapter | **Remove** |
| Comment "local dev only" in `main.py` | `main.py` was demoted because each service had its own Lambda entrypoint | **`main.py` becomes the real entrypoint** |

---

## What Stays Unchanged

These are genuine application structure decisions, not Lambda artifacts:

- `services/<name>/router.py`, `logic.py`, `schemas.py` — stays exactly as-is
- `shared/` — stays exactly as-is
- `alembic/` — stays exactly as-is
- `scripts/` — stays exactly as-is
- `api/pyproject.toml` (ruff config) — stays (or minor cleanup)

---

## Target Folder Structure

```
api/
  services/
    ai_service/
      router.py
      logic.py
      schemas.py
      openai_client.py
      prompts.py
      __init__.py
    auth_service/
      router.py
      logic.py
      schemas.py
      __init__.py
    document_service/
      router.py
      logic.py
      schemas.py
      __init__.py
    letter_service/
      router.py
      logic.py
      schemas.py
      docx_generator.py
      __init__.py
    parser_service/
      router.py
      logic.py
      schemas.py
      pdf_parser.py
      __init__.py
    template_service/
      router.py
      logic.py
      schemas.py
      __init__.py

  shared/
    models/
    schemas/
    base.py
    config.py
    database.py
    db_utils.py
    exceptions.py
    s3_client.py
    utils.py
    __init__.py

  alembic/
  scripts/
  main.py              ← Real entrypoint (uvicorn target). No more "local dev only".
  Dockerfile           ← New: container entrypoint
  .env.example         ← New: document required env vars
  requirements.txt
  requirements-dev.txt
  pyproject.toml
```

No `handlers/` folder. No `serverless.yml`. No `package.json`.

---

## Implementation Plan

### PR 1 — Delete Lambda Artifacts

**Goal:** Remove all Lambda-specific files. No behavior change to application logic.

#### Files to Delete
- `handlers/` (entire folder)
- `services/ai_service/handler.py`
- `services/auth_service/` — note: `handler.py` does not exist here currently; skip
- `services/document_service/handler.py`
- `services/letter_service/handler.py`
- `services/parser_service/handler.py`
- `services/template_service/handler.py`
- `serverless.yml`
- `package.json`
- `package-lock.json`
- `load-env-production.sh`

#### Files to Modify

**`main.py`**
- Remove the `health_handler(event, context)` Lambda function at the bottom
- Remove the `"local dev only"` comment from the module docstring — this is now the real entrypoint
- Clean up any `SERVERLESS_STAGE` references (currently in `handlers/base.py`, not `main.py` directly — but double-check)
- Keep the lifespan startup checks (DB + S3 health) — these are good production behavior

**`requirements.txt`**
- Remove `mangum>=0.17.0`

---

### PR 2 — Add Dockerfile + Production Entrypoint

**Goal:** Replace the Lambda deployment model with a container-based one.

#### New: `api/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### New: `api/.env.example`

Document all required environment variables (replacing what `serverless.yml` previously listed):

```env
ENVIRONMENT=development

DB_HOST=
DB_PORT=5432
DB_NAME=
DB_USER=
DB_PASSWORD=

AWS_REGION=us-east-2
AWS_S3_BUCKET_DOCUMENTS=
AWS_S3_BUCKET_EXPORTS=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

OPENAI_API_KEY=

CORS_ALLOW_ORIGINS=http://localhost:5173
LOG_LEVEL=INFO
DEBUG=false
```

#### Update: `api/docker-compose.yml`

Update the `api` service to use the Dockerfile instead of any Lambda-specific run command. Ensure the compose file mounts `.env` and exposes port 8000.

---

### PR 3 — `shared/s3_client.py` Simplification

**Goal:** Remove the Lambda environment detection hack (`AWS_EXECUTION_ENV`).

Currently `s3_client.py` checks `AWS_EXECUTION_ENV` to decide whether to use IAM role credentials (Lambda) or explicit env var credentials (local). After removing Lambda, this distinction disappears.

The new behavior:
- Always use explicit credentials from `get_settings().aws` if `access_key_id` is set
- If not set, fall back to boto3's default credential chain (instance profile, ECS task role, env vars, `~/.aws/credentials`) — this handles ECS/EC2 deployment naturally without special-casing

```python
# Current (Lambda-aware):
if os.getenv("AWS_EXECUTION_ENV"):
    client = boto3.client("s3", region_name=region)
else:
    client = boto3.client("s3", region_name=region, aws_access_key_id=key, ...)

# Target (credential-chain aware):
settings = get_settings()
kwargs = {"region_name": settings.aws.region}
if settings.aws.access_key_id:
    kwargs["aws_access_key_id"] = settings.aws.access_key_id
    kwargs["aws_secret_access_key"] = settings.aws.secret_access_key
client = boto3.client("s3", **kwargs)
```

---

### PR 4 — `shared/config.py` Cleanup

**Goal:** Remove Lambda-specific config accommodations.

- Remove `extra="ignore"` from `AWSConfig.model_config` if it was added solely to suppress Lambda's injected `AWS_*` env vars. (In a container deployment, you control the environment — no unexpected vars.)
- Remove `SERVERLESS_STAGE` from any settings model if it was added there
- Verify `CORSConfig.allow_origins` is properly sourced from env — production origins should come from env, not be hardcoded in Python files

---

## Files With Hardcoded Netlify Domain to Audit

The Netlify domain was hardcoded in multiple places during the Lambda deployment fix. After this restructuring, CORS origins must come exclusively from `get_settings().cors.allow_origins`, which reads from the `CORS_ALLOW_ORIGINS` env var.

Files to audit and fix:
- `api/handlers/base.py` — `cors_origins` default list (deleted in PR 1, moot)
- `api/main.py` — hardcoded list in wildcard fallback block (fix in PR 1)

After PR 1, the only place the Netlify domain appears should be in `.env.production` (or whatever env file the deployment uses) as a value for `CORS_ALLOW_ORIGINS`.

---

## What Does NOT Change

- All service business logic (`logic.py`) — untouched
- All routers (`router.py`) — untouched
- All Pydantic schemas — untouched
- All SQLAlchemy models — untouched
- Database session management (`get_db()`) — untouched
- Exception handling pattern — untouched
- Alembic migrations — untouched
- `docker-compose.yml` for local Postgres — largely untouched

---

## Definition of Done

- [x] `handlers/` folder does not exist
- [x] No `handler.py` file exists inside any `services/` subfolder
- [x] `serverless.yml`, `package.json`, `package-lock.json` do not exist
- [x] `mangum` is not in `requirements.txt`
- [x] `main.py` module docstring no longer says "local dev only"
- [x] `main.py` has no Lambda event handler functions
- [x] `shared/s3_client.py` has no reference to `AWS_EXECUTION_ENV`
- [x] All hardcoded CORS origin strings are removed from Python source files
- [x] `api/Dockerfile` exists and builds successfully
- [x] `api/.env.example` documents all required env vars
- [x] `uvicorn main:app` starts the server and all endpoints respond correctly
- [x] Local dev workflow documented (replace `serverless.yml`-based deploy scripts with Docker/uvicorn commands)
