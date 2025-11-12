#!/bin/bash
# Run database migrations (upgrade to latest)
# Usage: ./migration_scripts/migrate-up.sh
# Or from backend directory: ./migration_scripts/migrate-up.sh

cd "$(dirname "$0")/.."
alembic upgrade head

