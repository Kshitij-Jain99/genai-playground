"""Simulated tool execution service."""

from dataclasses import dataclass

from app.telemetry.tracing import tracer


@dataclass(frozen=True)
class ToolResult:
    """Result returned by a simulated tool."""

    name: str
    tool_type: str
    success: bool
    output: str


def execute_diagnostic_tool(question: str) -> ToolResult:
    """Execute a safe simulated diagnostic tool."""

    with tracer.start_as_current_span("tool.execute") as span:
        tool_name = "service-health-check"
        tool_type = "simulated"
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

        return ToolResult(
            name=tool_name,
            tool_type=tool_type,
            success=success,
            output=output,
        )