# Docker Setup for Local Development

The backend runs as a **FastAPI + uvicorn** process. **`api/docker-compose.yml`** starts **PostgreSQL 15** and the **API** in one stack. The API image is built from **`api/Dockerfile`**.

The webapp (Vite/React) is not containerized here; run it separately. See the repository root README for the frontend.

## Overview

| Service | Role |
|---------|------|
| `postgres` | PostgreSQL 15, database `demand_letters`, user `dev_user` |
| `api` | FastAPI app (`main:app`), hot reload in Compose, port **8000** |

## Prerequisites

- Docker Engine + Docker Compose (v2)
- An **`api/.env`** file (copy from **`api/.env.example`**)

Compose loads **`api/.env`** from the same directory as `docker-compose.yml` for variable substitution (e.g. `${OPENAI_API_KEY}`).

## Environment variables

Create **`api/.env`** (see **`api/.env.example`**). Minimum for a working stack:

```env
OPENAI_API_KEY=your_openai_key_here
AWS_ACCESS_KEY_ID=your_aws_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_here
AWS_REGION=us-east-2
AWS_S3_BUCKET_DOCUMENTS=your_documents_bucket_name
AWS_S3_BUCKET_EXPORTS=your_exports_bucket_name
```

`docker-compose.yml` also sets **`DB_HOST=postgres`**, **`DB_NAME`**, **`DB_USER`**, **`DB_PASSWORD`**, and defaults for **`CORS_ALLOW_ORIGINS`** suitable for local Vite/React. Override **`CORS_ALLOW_ORIGINS`** in `.env` if your frontend runs on another origin.

## Starting services

Run all commands from **`api/`**:

```bash
cd api
docker compose up
```

Detached mode:

```bash
docker compose up -d
```

Rebuild after Dockerfile or dependency changes:

```bash
docker compose up --build
```

## Stopping services

```bash
docker compose down
```

Remove volumes (wipes PostgreSQL data):

```bash
docker compose down -v
```

## Logs

```bash
docker compose logs
docker compose logs api
docker compose logs postgres
docker compose logs -f api
```

## Accessing services

| Service | URL / connection |
|---------|------------------|
| API | http://localhost:8000 |
| OpenAPI docs | http://localhost:8000/docs |
| PostgreSQL (host) | `localhost:5432`, db `demand_letters`, user `dev_user`, password `dev_password` |

## Database migrations

After the stack is up:

```bash
cd api
docker compose exec api alembic upgrade head
```

Or from the host with venv and `DB_HOST=localhost` if only Postgres is running in Docker.

## Production image (no hot reload)

The **`Dockerfile`** default **`CMD`** runs:

`uvicorn main:app --host 0.0.0.0 --port 8000`

Compose overrides this for development with **`--reload`**. For deployment, build the same image and pass environment variables (or secrets) appropriate to your host (ECS, Fly.io, bare VM, etc.).

## Troubleshooting

### Port already in use

If **5432** or **8000** is taken, stop the conflicting process or change the **ports** mapping in `docker-compose.yml`.

### API cannot reach Postgres

Ensure `postgres` is healthy: `docker compose ps`. The API **`depends_on`** waits for the Postgres healthcheck.

### Environment variables not applied

- Put variables in **`api/.env`** (same folder as `docker-compose.yml`).
- Restart: `docker compose down && docker compose up`.

### Healthcheck failures

The API service healthcheck uses **`curl`** against **`http://localhost:8000/health`**. The **`Dockerfile`** installs **`curl`**. If startup fails (e.g. missing **`OPENAI_API_KEY`** or invalid S3 config), check **`docker compose logs api`**.

## Development workflow

1. `cd api && cp .env.example .env` and edit **`.env`**
2. `docker compose up -d`
3. `docker compose exec api alembic upgrade head`
4. Edit code — hot reload is enabled via the Compose **command** override
5. `docker compose down` when finished

## Historical note

The project previously deployed the API to **AWS Lambda** via Serverless. That path is removed; see **`docs/remove-lambda.md`** and **`docs/lambda-deployment.md`** (archived reference).
