#!/bin/bash
# Rollback database migrations (downgrade by one revision)
# Usage: ./migration_scripts/migrate-down.sh
# Or from backend directory: ./migration_scripts/migrate-down.sh

cd "$(dirname "$0")/.."
alembic downgrade -1

