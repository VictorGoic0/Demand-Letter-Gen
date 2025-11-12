#!/bin/bash
# Restart Docker Compose services
# Usage: ./restart_server.sh

cd "$(dirname "$0")"
docker-compose restart

