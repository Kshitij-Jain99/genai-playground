"""Simulated tool execution service."""

from dataclasses import dataclass

from app.core.config import get_settings
from app.telemetry.metrics import tool_execution_count
from app.telemetry.tracing import tracer

settings = get_settings()


@dataclass(frozen=True)
class ToolResult:
    """Result returned by a simulated tool."""

    name: str
    tool_type: str
    success: bool
    output: str


def execute_diagnostic_tool(question: str) -> ToolResult:
    """Execute a safe simulated diagnostic tool."""

    tool_name = "service-health-check"
    tool_type = "simulated"

    try:
        with tracer.start_as_current_span("tool.execute") as span:
            success = True

            if "health" in question.lower():
                output = "The simulated service health check passed."
            else:
                output = "No additional diagnostic action was required."

            span.set_attribute(
                "app.tool.name",
                tool_name,
            )
            span.set_attribute(
                "app.tool.type",
                tool_type,
            )
            span.set_attribute(
                "app.tool.success",
                success,
            )

            tool_execution_count.add(
                1,
                attributes={
                    "tool_name": tool_name,
                    "tool_type": tool_type,
                    "environment": settings.app_environment,
                    "status": "success",
                },
            )

            return ToolResult(
                name=tool_name,
                tool_type=tool_type,
                success=success,
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
            },
        )
        raise