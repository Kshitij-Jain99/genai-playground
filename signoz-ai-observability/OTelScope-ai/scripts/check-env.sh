#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [[ ! -f ".env" ]]; then
    echo "Error: .env does not exist."
    echo "Create it with:"
    echo "  cp .env.example .env"
    exit 1
fi

# Check syntax without exposing values.
bash -n .env

set -a
source .env
set +a

required_variables=(
    APP_NAME
    APP_SERVICE_NAME
    APP_ENVIRONMENT
    APP_VERSION
    APP_HOST
    APP_PORT
    OTEL_SERVICE_NAME
    OTEL_RESOURCE_ATTRIBUTES
    OTEL_EXPORTER_OTLP_ENDPOINT
    OTEL_EXPORTER_OTLP_PROTOCOL
    OTEL_TRACES_EXPORTER
    OTEL_METRICS_EXPORTER
    OTEL_LOGS_EXPORTER
    OTEL_TRACES_SAMPLER
    LLM_PROVIDER
    LLM_MODEL
)

missing=0

for variable in "${required_variables[@]}"; do
    if [[ -z "${!variable:-}" ]]; then
        echo "Missing required variable: ${variable}"
        missing=1
    fi
done

if [[ "$OTEL_EXPORTER_OTLP_PROTOCOL" == "http/protobuf" ]] &&
   [[ "$OTEL_EXPORTER_OTLP_ENDPOINT" != *":4318"* ]]; then
    echo "Warning: http/protobuf is normally paired with OTLP port 4318."
fi

if [[ "$OTEL_EXPORTER_OTLP_PROTOCOL" == "grpc" ]] &&
   [[ "$OTEL_EXPORTER_OTLP_ENDPOINT" != *":4317"* ]]; then
    echo "Warning: grpc is normally paired with OTLP port 4317."
fi

if [[ "$missing" -ne 0 ]]; then
    echo
    echo "Environment validation failed."
    exit 1
fi

echo "Environment validation passed."
echo
echo "Application"
echo "  Name: ${APP_NAME}"
echo "  Service: ${APP_SERVICE_NAME}"
echo "  Environment: ${APP_ENVIRONMENT}"
echo "  Version: ${APP_VERSION}"
echo "  Address: http://${APP_HOST}:${APP_PORT}"
echo
echo "OpenTelemetry"
echo "  Service: ${OTEL_SERVICE_NAME}"
echo "  Endpoint: ${OTEL_EXPORTER_OTLP_ENDPOINT}"
echo "  Protocol: ${OTEL_EXPORTER_OTLP_PROTOCOL}"
echo "  Traces: ${OTEL_TRACES_EXPORTER}"
echo "  Metrics: ${OTEL_METRICS_EXPORTER}"
echo "  Logs: ${OTEL_LOGS_EXPORTER}"
echo "  Sampler: ${OTEL_TRACES_SAMPLER}"
echo
echo "LLM"
echo "  Provider: ${LLM_PROVIDER}"
echo "  Model: ${LLM_MODEL}"

if [[ -n "${LLM_API_KEY:-}" ]]; then
    echo "  API key configured: yes"
else
    echo "  API key configured: no"
fi
