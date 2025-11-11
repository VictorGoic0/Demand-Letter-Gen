# Docker Setup for Local Development

This directory contains documentation for the Docker setup used for local development of the Demand Letter Generator.

## Overview

The Docker setup includes:
- **PostgreSQL 15**: Database service for local development
- **Backend**: FastAPI application with hot reload enabled

**Note:** The frontend runs locally without Docker. See the main README for frontend setup instructions.

## Prerequisites

- Docker Desktop (or Docker Engine + Docker Compose)
- Environment variables configured (see below)

## Environment Variables

Before starting the services, ensure you have the following environment variables set in your shell or `.env` file:

```bash
OPENAI_API_KEY=your_openai_key_here
AWS_ACCESS_KEY_ID=your_aws_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_here
AWS_REGION=us-east-2
S3_BUCKET_DOCUMENTS=your_documents_bucket_name
S3_BUCKET_EXPORTS=your_exports_bucket_name
```

You can create a `.env` file in the `backend/` directory (same directory as `docker-compose.yml`) with these variables, and Docker Compose will automatically load them.

## Starting Services

**Note:** All docker-compose commands should be run from the `backend/` directory.

To start all services:

```bash
cd backend
docker-compose up
```

To start services in detached mode (background):

```bash
cd backend
docker-compose up -d
```

To start services and rebuild containers:

```bash
cd backend
docker-compose up --build
```

## Stopping Services

To stop all services:

```bash
cd backend
docker-compose down
```

To stop services and remove volumes (this will delete database data):

```bash
cd backend
docker-compose down -v
```

## Viewing Logs

To view logs from all services:

```bash
cd backend
docker-compose logs
```

To view logs from a specific service:

```bash
cd backend
docker-compose logs backend
docker-compose logs postgres
```

To follow logs in real-time:

```bash
cd backend
docker-compose logs -f
```

To follow logs from a specific service:

```bash
cd backend
docker-compose logs -f backend
```

## Rebuilding Containers

If you make changes to Dockerfiles or need to rebuild:

```bash
cd backend
docker-compose build
```

To rebuild without cache:

```bash
cd backend
docker-compose build --no-cache
```

To rebuild and restart services:

```bash
cd backend
docker-compose up --build
```

## Accessing Services

Once services are running:

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
  - Database: `demand_letters`
  - User: `dev_user`
  - Password: `dev_password`

## Database Migrations

After starting the services, run database migrations:

```bash
# Enter the backend container
cd backend
docker-compose exec backend bash

# Run migrations
alembic upgrade head

# Or run from host (if alembic is installed locally)
cd backend
alembic upgrade head
```

## Troubleshooting

### Port Already in Use

If you get an error that port 5432 or 8000 is already in use:

1. Check what's using the port:
   ```bash
   # For PostgreSQL (5432)
   lsof -i :5432
   
   # For Backend (8000)
   lsof -i :8000
   ```

2. Either stop the conflicting service or change the port mapping in `backend/docker-compose.yml`

**Note:** PostgreSQL uses port 5432 on the host (instead of the default 5432) to allow multiple PostgreSQL Docker containers from different projects to run simultaneously. If 5432 is also in use, you can change it to any other available port (e.g., 5434, 5435) in the docker-compose.yml file.

### Database Connection Issues

If the backend can't connect to PostgreSQL:

1. Ensure PostgreSQL service is healthy:
   ```bash
   cd backend
   docker-compose ps
   ```

2. Check PostgreSQL logs:
   ```bash
   cd backend
   docker-compose logs postgres
   ```

3. Wait for PostgreSQL to be ready (healthcheck should pass)

### Backend Not Reloading

If code changes aren't being picked up:

1. Ensure volume mounts are correct in `backend/docker-compose.yml`
2. Check that the backend service is running with `--reload` flag
3. Check backend logs for errors:
   ```bash
   cd backend
   docker-compose logs -f backend
   ```

### Container Won't Start

1. Check logs for errors:
   ```bash
   cd backend
   docker-compose logs
   ```

2. Verify Docker has enough resources allocated (Docker Desktop > Settings > Resources)

3. Try rebuilding without cache:
   ```bash
   cd backend
   docker-compose build --no-cache
   docker-compose up
   ```

### Database Data Persistence

Database data is stored in a Docker volume named `postgres_data`. To completely reset the database:

```bash
cd backend
docker-compose down -v
docker-compose up
```

**Warning:** This will delete all data in the database.

### Environment Variables Not Loading

If environment variables aren't being picked up:

1. Ensure variables are set in your shell or `.env` file
2. Check that `.env` file is in the `backend/` directory (same directory as `docker-compose.yml`)
3. Restart services after adding/changing variables:
   ```bash
   cd backend
   docker-compose down
   docker-compose up
   ```

## Development Workflow

1. Start services: `cd backend && docker-compose up -d`
2. Run migrations: `cd backend && alembic upgrade head`
3. Make code changes (hot reload is enabled)
4. View logs: `cd backend && docker-compose logs -f backend`
5. Stop services when done: `cd backend && docker-compose down`

## Production Build

For production Lambda deployments, use `backend/Dockerfile.lambda` which creates an optimized multi-stage build for AWS Lambda. This is used during the serverless deployment process, not for local development.

