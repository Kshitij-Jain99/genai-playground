"""Simulated tool execution service."""

from dataclasses import dataclass

from app.core.config import get_settings
from app.telemetry.metrics import tool_execution_count
from app.telemetry.tracing import tracer
from app.telemetry.logging import get_logger
from time import sleep

from app.core.scenarios import Scenario, get_scenario_timings

settings = get_settings()

logger = get_logger(__name__)


@dataclass(frozen=True)
class ToolResult:
    """Result returned by a simulated tool."""

    name: str
    tool_type: str
    success: bool
    output: str


def execute_diagnostic_tool(
    question: str,
    scenario: Scenario,
) -> ToolResult:
    """Execute a deterministic simulated diagnostic tool."""

    tool_name = "service-health-check"
    tool_type = "simulated"
    timings = get_scenario_timings(scenario)

    try:
        with tracer.start_as_current_span("tool.execute") as span:
            span.set_attribute(
                "app.scenario",
                scenario.value,
            )
            span.set_attribute(
                "app.tool.name",
                tool_name,
            )
            span.set_attribute(
                "app.tool.type",
                tool_type,
            )

            logger.info(
                "Tool execution started",
                extra={
                    "event": "tool_execution_started",
                    "operation": "tool.execute",
                    "status": "started",
                    "scenario": scenario.value,
                    "tool_name": tool_name,
                    "tool_type": tool_type,
                },
            )

            sleep(timings.tool_seconds)

            if scenario == Scenario.TOOL_FAILURE:
                span.set_attribute(
                    "app.tool.success",
                    False,
                )

                raise RuntimeError(
                    "Simulated diagnostic tool failure."
                )

            if "health" in question.lower():
                output = "The simulated service health check passed."
            else:
                output = "No additional diagnostic action was required."

            span.set_attribute(
                "app.tool.success",
                True,
            )

            tool_execution_count.add(
                1,
                attributes={
                    "tool_name": tool_name,
                    "tool_type": tool_type,
                    "environment": settings.app_environment,
                    "status": "success",
                    "scenario": scenario.value,
                },
            )

            logger.info(
                "Tool execution completed",
                extra={
                    "event": "tool_execution_completed",
                    "operation": "tool.execute",
                    "status": "success",
                    "scenario": scenario.value,
                    "tool_name": tool_name,
                    "tool_type": tool_type,
                },
            )

            return ToolResult(
                name=tool_name,
                tool_type=tool_type,
                success=True,
                output=output,
            )

    except Exception:
        tool_execution_count.add(
            1,
            attributes={
                "tool_name": tool_name,
                "tool_type": tool_type,
                "environment": settings.app_environment,
                "status": "error",
                "scenario": scenario.value,
            },
        )

        logger.exception(
            "Tool execution failed",
            extra={
                "event": "tool_execution_failed",
                "operation": "tool.execute",
                "status": "error",
                "scenario": scenario.value,
                "tool_name": tool_name,
                "tool_type": tool_type,
            },
        )

        raise