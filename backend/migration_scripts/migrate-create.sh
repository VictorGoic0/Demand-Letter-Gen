#!/bin/bash
# Create a new migration file
# Usage: ./migration_scripts/migrate-create.sh "migration_message"
# Or from backend directory: ./migration_scripts/migrate-create.sh "migration_message"

if [ -z "$1" ]; then
    echo "Error: Migration message is required"
    echo "Usage: ./migration_scripts/migrate-create.sh \"migration_message\""
    exit 1
fi

cd "$(dirname "$0")/.."
alembic revision --autogenerate -m "$1"

