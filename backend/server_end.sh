#!/bin/bash
# Stop Docker Compose services
# Usage: ./end_server.sh

cd "$(dirname "$0")"
docker-compose down

