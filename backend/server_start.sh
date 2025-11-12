#!/bin/bash
# Start Docker Compose services
# Usage: ./start_server.sh

cd "$(dirname "$0")"
docker-compose up -d

