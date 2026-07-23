"""Structured application logging with OpenTelemetry trace correlation."""

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from opentelemetry import trace

from app.core.config import get_settings

settings = get_settings()

_STANDARD_LOG_RECORD_FIELDS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "taskName",
    "thread",
    "threadName",
}


def get_trace_context() -> tuple[str | None, str | None]:
    """Return the current OpenTelemetry trace and span identifiers."""

    current_span = trace.get_current_span()
    span_context = current_span.get_span_context()

    if not span_context.is_valid:
        return None, None

    trace_id = format(span_context.trace_id, "032x")
    span_id = format(span_context.span_id, "016x")

    return trace_id, span_id


class JsonLogFormatter(logging.Formatter):
    """Format Python log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        trace_id, span_id = get_trace_context()

        timestamp = datetime.fromtimestamp(
            record.created,
            tz=UTC,
        ).isoformat()

        log_data: dict[str, Any] = {
            "timestamp": timestamp,
            "level": record.levelname.lower(),
            "event": getattr(record, "event", record.getMessage()),
            "service": getattr(
                record,
                "service",
                settings.app_service_name,
            ),
            "environment": getattr(
                record,
                "environment",
                settings.app_environment,
            ),
            "operation": getattr(record, "operation", None),
            "provider": getattr(record, "provider", None),
            "model": getattr(record, "model", None),
            "status": getattr(record, "status", None),
            "trace_id": trace_id,
            "span_id": span_id,
        }

        for key, value in record.__dict__.items():
            if key in _STANDARD_LOG_RECORD_FIELDS:
                continue

            if key in log_data:
                continue

            if key.startswith("otel"):
                continue

            if value is not None:
                log_data[key] = value

        if record.exc_info:
            exception_type = record.exc_info[0]

            if exception_type is not None:
                log_data["error_type"] = exception_type.__name__

        return json.dumps(
            log_data,
            default=str,
            separators=(",", ":"),
        )


def configure_logging() -> None:
    """Configure the root Python logger once."""

    root_logger = logging.getLogger()

    if getattr(root_logger, "_otelscope_configured", False):
        return

    log_level_name = settings.app_log_level.upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonLogFormatter())

    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    root_logger._otelscope_configured = True  # type: ignore[attr-defined]


def get_logger(name: str) -> logging.Logger:
    """Return a configured application logger."""

    configure_logging()

    return logging.getLogger(name)