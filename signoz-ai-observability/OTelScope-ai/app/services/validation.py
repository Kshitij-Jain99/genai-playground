"""AI response validation service."""

from dataclasses import dataclass

from app.telemetry.tracing import tracer


@dataclass(frozen=True)
class ValidationResult:
    """Result of validating an AI response."""

    passed: bool
    rule_count: int


def validate_response(answer: str) -> ValidationResult:
    """Validate the simulated AI response."""

    with tracer.start_as_current_span("response.validate") as span:
        validation_rules = [
            bool(answer.strip()),
            len(answer) <= 5_000,
            "api_key" not in answer.lower(),
        ]

        passed = all(validation_rules)
        rule_count = len(validation_rules)

        span.set_attribute(
            "app.validation.passed",
            passed,
        )
        span.set_attribute(
            "app.validation.rule_count",
            rule_count,
        )
        span.set_attribute(
            "app.response.length",
            len(answer),
        )

        if not passed:
            raise ValueError(
                "Generated response failed validation."
            )

        return ValidationResult(
            passed=passed,
            rule_count=rule_count,
        )