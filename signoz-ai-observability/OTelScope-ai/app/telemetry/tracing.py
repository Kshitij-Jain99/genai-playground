"""Shared OpenTelemetry tracing utilities."""

from opentelemetry import trace

from app.core.config import get_settings

settings = get_settings()

tracer = trace.get_tracer(
    "otelscope-ai",
    settings.app_version,
)