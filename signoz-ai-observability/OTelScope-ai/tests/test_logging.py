"""Tests for structured application logging."""

import json
import logging
import sys

import app.telemetry.logging as telemetry_logging
from app.telemetry.logging import JsonLogFormatter


def create_log_record(
    *,
    level: int = logging.INFO,
    event: str = "test_event",
) -> logging.LogRecord:
    """Create a test Python log record."""

    record = logging.LogRecord(
        name="test",
        level=level,
        pathname=__file__,
        lineno=1,
        msg="Test log",
        args=(),
        exc_info=None,
    )

    record.event = event
    record.operation = "test.operation"
    record.status = "success"

    return record


def test_json_formatter_returns_valid_json() -> None:
    formatter = JsonLogFormatter()
    record = create_log_record()

    formatted_log = formatter.format(record)
    log_data = json.loads(formatted_log)

    assert log_data["level"] == "info"
    assert log_data["event"] == "test_event"
    assert log_data["operation"] == "test.operation"
    assert log_data["status"] == "success"


def test_json_formatter_includes_service() -> None:
    formatter = JsonLogFormatter()
    record = create_log_record()

    log_data = json.loads(formatter.format(record))

    assert log_data["service"] == "otelscope-ai-api"
    assert log_data["environment"] == "development"


def test_json_formatter_has_trace_fields() -> None:
    formatter = JsonLogFormatter()
    record = create_log_record()

    log_data = json.loads(formatter.format(record))

    assert "trace_id" in log_data
    assert "span_id" in log_data


def test_json_formatter_does_not_include_message_by_default() -> None:
    formatter = JsonLogFormatter()
    record = create_log_record()

    log_data = json.loads(formatter.format(record))

    assert "message" not in log_data


def test_configure_logging_preserves_otel_handlers(
    monkeypatch,
) -> None:
    class FakeOtelHandler(logging.Handler):
        __module__ = "opentelemetry.sdk._logs"

        def emit(self, record: logging.LogRecord) -> None:
            pass

    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers[:]
    original_level = root_logger.level
    had_configured_flag = hasattr(
        root_logger,
        "_otelscope_configured",
    )
    original_configured = getattr(
        root_logger,
        "_otelscope_configured",
        None,
    )
    otel_handler = FakeOtelHandler()

    try:
        root_logger.handlers = [otel_handler]
        monkeypatch.delattr(
            root_logger,
            "_otelscope_configured",
            raising=False,
        )

        telemetry_logging.configure_logging()

        assert otel_handler in root_logger.handlers
        assert any(
            isinstance(handler, logging.StreamHandler)
            and handler.stream is sys.stdout
            for handler in root_logger.handlers
        )
    finally:
        root_logger.handlers = original_handlers
        root_logger.setLevel(original_level)

        if had_configured_flag:
            root_logger._otelscope_configured = original_configured
        else:
            root_logger.__dict__.pop(
                "_otelscope_configured",
                None,
            )
