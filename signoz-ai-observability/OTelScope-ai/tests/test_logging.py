"""Tests for structured application logging."""

import json
import logging

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