#!/bin/bash
# Rollback database migrations (downgrade by one revision)
# Usage: ./scripts/migrate-down.sh
# Or from api directory: ./scripts/migrate-down.sh

cd "$(dirname "$0")/.."
alembic downgrade -1
