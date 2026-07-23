#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(
    cd "$(dirname "${BASH_SOURCE[0]}")/.."
    pwd
)"

cd "$PROJECT_ROOT"

if [[ ! -d ".venv" ]]; then
    echo "Error: virtual environment .venv does not exist."
    echo "Create it with:"
    echo "  python3 -m venv .venv"
    exit 1
fi

if [[ ! -f ".env" ]]; then
    echo "Error: .env file is missing."
    echo "Create it with:"
    echo "  cp .env.example .env"
    exit 1
fi

source .venv/bin/activate

if ! command -v opentelemetry-instrument >/dev/null 2>&1; then
    echo "Error: opentelemetry-instrument is not installed."
    echo "Install the project dependencies first."
    exit 1
fi

set -a
source .env
set +a

required_variables=(
    "OTEL_SERVICE_NAME"
    "OTEL_EXPORTER_OTLP_ENDPOINT"
    "OTEL_EXPORTER_OTLP_PROTOCOL"
    "OTEL_TRACES_EXPORTER"
)

for variable_name in "${required_variables[@]}"; do
    if [[ -z "${!variable_name:-}" ]]; then
        echo "Error: ${variable_name} is missing or empty in .env."
        exit 1
    fi
done

APP_HOST="${APP_HOST:-127.0.0.1}"
APP_PORT="${APP_PORT:-8001}"

echo "Starting OTelScope AI with OpenTelemetry"
echo "Service: ${OTEL_SERVICE_NAME}"
echo "Environment: ${APP_ENVIRONMENT:-development}"
echo "Application: http://${APP_HOST}:${APP_PORT}"
echo "Swagger UI: http://${APP_HOST}:${APP_PORT}/docs"
echo "OTLP endpoint: ${OTEL_EXPORTER_OTLP_ENDPOINT}"
echo "OTLP protocol: ${OTEL_EXPORTER_OTLP_PROTOCOL}"

exec opentelemetry-instrument \
    uvicorn app.main:app \
    --host "$APP_HOST" \
    --port "$APP_PORT" \
    --reload