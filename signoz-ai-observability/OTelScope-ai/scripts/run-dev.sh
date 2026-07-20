#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [[ ! -d ".venv" ]]; then
    echo "Error: .venv does not exist."
    echo "Create it using: python3 -m venv .venv"
    exit 1
fi

if [[ ! -f ".env" ]]; then
    echo "Error: .env does not exist."
    echo "Create it using: cp .env.example .env"
    exit 1
fi

source .venv/bin/activate

set -a
source .env
set +a

echo "Starting ${APP_NAME}"
echo "Service: ${APP_SERVICE_NAME}"
echo "Environment: ${APP_ENVIRONMENT}"
echo "Address: http://${APP_HOST}:${APP_PORT}"
echo "Documentation: http://${APP_HOST}:${APP_PORT}/docs"

exec uvicorn app.main:app \
    --host "${APP_HOST}" \
    --port "${APP_PORT}" \
    --reload
