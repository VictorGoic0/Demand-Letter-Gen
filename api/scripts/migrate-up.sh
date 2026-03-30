#!/bin/bash
# Run database migrations (upgrade to latest)
# Usage: ./scripts/migrate-up.sh
# Or from api directory: ./scripts/migrate-up.sh

cd "$(dirname "$0")/.."
alembic upgrade head
