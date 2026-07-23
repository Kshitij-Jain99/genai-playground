"""AI response validation service."""

from dataclasses import dataclass

from app.telemetry.tracing import tracer
from app.telemetry.logging import get_logger
from time import sleep

from app.core.scenarios import Scenario, get_scenario_timings

logger = get_logger(__name__)

@dataclass(frozen=True)
class ValidationResult:
    """Result of validating an AI response."""

    passed: bool
    rule_count: int


def validate_response(
    answer: str,
    scenario: Scenario,
) -> ValidationResult:
    """Validate the simulated AI response."""

    timings = get_scenario_timings(scenario)

    with tracer.start_as_current_span("response.validate") as span:
        sleep(timings.validation_seconds)

        validation_rules = [
            bool(answer.strip()),
            len(answer) <= 50_000,
            "api_key" not in answer.lower(),
        ]

        passed = all(validation_rules)
        rule_count = len(validation_rules)

        span.set_attribute(
            "app.scenario",
            scenario.value,
        )
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
            logger.error(
                "Response validation failed",
                extra={
                    "event": "response_validation_failed",
                    "operation": "response.validate",
                    "status": "error",
                    "scenario": scenario.value,
                    "validation_rule_count": rule_count,
                    "response_length": len(answer),
                },
            )

            raise ValueError(
                "Generated response failed validation."
            )

        logger.info(
            "Response validation completed",
            extra={
                "event": "response_validation_completed",
                "operation": "response.validate",
                "status": "success",
                "scenario": scenario.value,
                "validation_rule_count": rule_count,
                "response_length": len(answer),
            },
        )

        return ValidationResult(
            passed=passed,
            rule_count=rule_count,
        )