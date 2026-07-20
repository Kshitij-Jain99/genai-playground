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

# Export every variable loaded from .env.
set -a
source .env
set +a

if ! command -v opentelemetry-instrument >/dev/null 2>&1; then
    echo "Error: opentelemetry-instrument is not installed."
    echo "Run:"
    echo "  python -m pip install -r requirements.txt"
    echo "  opentelemetry-bootstrap -a install"
    exit 1
fi

echo "Starting ${APP_NAME} with OpenTelemetry"
echo "Service: ${OTEL_SERVICE_NAME}"
echo "Environment: ${APP_ENVIRONMENT}"
echo "Application: http://${APP_HOST}:${APP_PORT}"
echo "Documentation: http://${APP_HOST}:${APP_PORT}/docs"
echo "OTLP endpoint: ${OTEL_EXPORTER_OTLP_ENDPOINT}"
echo "OTLP protocol: ${OTEL_EXPORTER_OTLP_PROTOCOL}"
echo

exec opentelemetry-instrument \
    uvicorn app.main:app \
    --host "${APP_HOST}" \
    --port "${APP_PORT}"
