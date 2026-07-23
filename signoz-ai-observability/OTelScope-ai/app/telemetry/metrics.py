"""Shared OpenTelemetry metric instruments for OTelScope AI."""

from opentelemetry import metrics

from app.core.config import get_settings

settings = get_settings()

meter = metrics.get_meter(
    name="otelscope-ai",
    version=settings.app_version,
)


# ---------------------------------------------------------------------------
# GenAI metrics
# ---------------------------------------------------------------------------

gen_ai_request_count = meter.create_counter(
    name="app.gen_ai.request.count",
    unit="{request}",
    description="Total number of GenAI generation requests.",
)

gen_ai_input_tokens = meter.create_counter(
    name="app.gen_ai.input_tokens",
    unit="{token}",
    description="Total estimated GenAI input tokens.",
)

gen_ai_output_tokens = meter.create_counter(
    name="app.gen_ai.output_tokens",
    unit="{token}",
    description="Total estimated GenAI output tokens.",
)

gen_ai_estimated_cost = meter.create_counter(
    name="app.gen_ai.estimated_cost",
    unit="USD",
    description="Total estimated GenAI request cost in US dollars.",
)

gen_ai_request_duration = meter.create_histogram(
    name="app.gen_ai.request.duration",
    unit="s",
    description="Duration of GenAI generation operations in seconds.",
)


# ---------------------------------------------------------------------------
# Agent metrics
# ---------------------------------------------------------------------------

agent_run_count = meter.create_counter(
    name="app.agent.run.count",
    unit="{run}",
    description="Total number of AI agent runs.",
)

agent_run_duration = meter.create_histogram(
    name="app.agent.run.duration",
    unit="s",
    description="Duration of complete AI agent runs in seconds.",
)

agent_error_count = meter.create_counter(
    name="app.agent.error.count",
    unit="{error}",
    description="Total number of failed AI agent runs.",
)


# ---------------------------------------------------------------------------
# Retrieval metrics
# ---------------------------------------------------------------------------

retrieval_duration = meter.create_histogram(
    name="app.retrieval.duration",
    unit="s",
    description="Duration of knowledge-base retrieval operations in seconds.",
)


# ---------------------------------------------------------------------------
# Tool metrics
# ---------------------------------------------------------------------------

tool_execution_count = meter.create_counter(
    name="app.tool.execution.count",
    unit="{execution}",
    description="Total number of tool executions.",
)