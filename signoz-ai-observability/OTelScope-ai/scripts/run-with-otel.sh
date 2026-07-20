#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [[ ! -d ".venv" ]]; then
    echo "Error: .venv does not exist."
    echo "Run: ./scripts/install-dependencies.sh"
    exit 1
fi

if [[ ! -f ".env" ]]; then
    echo "Error: .env does not exist."
    echo "Run: cp .env.example .env"
    exit 1
fi

source .venv/bin/activate

"$PROJECT_ROOT/scripts/check-env.sh"

set -a
source .env
set +a

if ! command -v opentelemetry-instrument >/dev/null 2>&1; then
    echo "Error: opentelemetry-instrument is unavailable."
    echo "Run: ./scripts/install-dependencies.sh"
    exit 1
fi

echo
echo "Starting ${APP_NAME} with OpenTelemetry"
echo "Application: http://${APP_HOST}:${APP_PORT}"
echo "Documentation: http://${APP_HOST}:${APP_PORT}/docs"
echo "SigNoz: http://localhost:8080"
echo

exec opentelemetry-instrument \
    uvicorn app.main:app \
    --host "${APP_HOST}" \
    --port "${APP_PORT}"