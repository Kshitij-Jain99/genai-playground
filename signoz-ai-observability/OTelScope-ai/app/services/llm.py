"""Simulated LLM generation service."""

from dataclasses import dataclass
from time import perf_counter

from app.core.config import get_settings
from app.telemetry.metrics import (
    gen_ai_estimated_cost,
    gen_ai_input_tokens,
    gen_ai_output_tokens,
    gen_ai_request_count,
    gen_ai_request_duration,
)
from app.telemetry.tracing import tracer
from app.telemetry.logging import get_logger
from time import perf_counter, sleep

from app.core.scenarios import Scenario, get_scenario_timings

logger = get_logger(__name__)
settings = get_settings()


@dataclass(frozen=True)
class LLMResult:
    """Result returned by the simulated language model."""

    answer: str
    provider: str
    requested_model: str
    response_model: str
    input_tokens: int
    output_tokens: int
    estimated_cost: float
    finish_reason: str


def estimate_token_count(text: str) -> int:
    """Return a simple token estimate for the simulated model."""

    return max(1, len(text.split()))

def should_simulate_failure(question: str) -> bool:
    """Return whether a development-only LLM failure was requested."""

    return (
        settings.app_environment == "development"
        and question.strip().lower() == "simulate llm failure"
    )


def estimate_request_cost(
    input_tokens: int,
    output_tokens: int,
) -> float:
    """Estimate request cost using configured demo prices."""

    input_cost = (
        input_tokens / 1_000
    ) * settings.llm_input_cost_per_1k_tokens

    output_cost = (
        output_tokens / 1_000
    ) * settings.llm_output_cost_per_1k_tokens

    return input_cost + output_cost


def generate_response(
    question: str,
    rendered_prompt: str,
    context_documents: list[str],
    tool_output: str,
    scenario: Scenario,
) -> LLMResult:
    """Generate a deterministic simulated LLM response."""

    started_at = perf_counter()

    provider = settings.llm_provider
    requested_model = settings.llm_model
    response_model = settings.llm_model
    operation = "chat"

    timings = get_scenario_timings(scenario)

    metric_attributes = {
        "provider": provider,
        "model": requested_model,
        "environment": settings.app_environment,
        "operation": operation,
        "scenario": scenario.value,
    }

    try:
        with tracer.start_as_current_span("llm.generate") as span:
            span.set_attribute(
                "app.scenario",
                scenario.value,
            )

            logger.info(
                "LLM request started",
                extra={
                    "event": "llm_request_started",
                    "operation": operation,
                    "provider": provider,
                    "model": requested_model,
                    "status": "started",
                    "scenario": scenario.value,
                },
            )

            sleep(timings.llm_seconds)

            if scenario in {Scenario.ERROR, Scenario.FAILURE}:
                raise RuntimeError(
                    "Simulated LLM provider failure."
                )

            context_summary = (
                context_documents[0]
                if context_documents
                else "No retrieval context was available."
            )

            if scenario == Scenario.HIGH_TOKEN:
                answer = create_high_token_answer()
            else:
                answer = (
                    f"Simulated troubleshooting answer for: {question}. "
                    f"Relevant context: {context_summary} "
                    f"Diagnostic result: {tool_output}"
                )

            input_tokens = estimate_token_count(rendered_prompt)
            output_tokens = estimate_token_count(answer)

            estimated_cost = estimate_request_cost(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )

            finish_reason = "stop"

            span.set_attribute(
                "gen_ai.operation.name",
                operation,
            )
            span.set_attribute(
                "gen_ai.provider.name",
                provider,
            )
            span.set_attribute(
                "gen_ai.request.model",
                requested_model,
            )
            span.set_attribute(
                "gen_ai.response.model",
                response_model,
            )
            span.set_attribute(
                "gen_ai.usage.input_tokens",
                input_tokens,
            )
            span.set_attribute(
                "gen_ai.usage.output_tokens",
                output_tokens,
            )
            span.set_attribute(
                "gen_ai.response.finish_reasons",
                [finish_reason],
            )
            span.set_attribute(
                "app.llm.simulated",
                True,
            )
            span.set_attribute(
                "app.llm.prompt_length",
                len(rendered_prompt),
            )
            span.set_attribute(
                "app.llm.response_length",
                len(answer),
            )
            span.set_attribute(
                "app.llm.estimated_cost",
                estimated_cost,
            )

            success_attributes = {
                **metric_attributes,
                "status": "success",
            }

            gen_ai_request_count.add(
                1,
                attributes=success_attributes,
            )
            gen_ai_input_tokens.add(
                input_tokens,
                attributes=success_attributes,
            )
            gen_ai_output_tokens.add(
                output_tokens,
                attributes=success_attributes,
            )
            gen_ai_estimated_cost.add(
                estimated_cost,
                attributes=success_attributes,
            )

            duration_seconds = perf_counter() - started_at

            logger.info(
                "LLM request completed",
                extra={
                    "event": "llm_request_completed",
                    "operation": operation,
                    "provider": provider,
                    "model": response_model,
                    "status": "success",
                    "scenario": scenario.value,
                    "finish_reason": finish_reason,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "estimated_cost": round(
                        estimated_cost,
                        8,
                    ),
                    "duration_ms": round(
                        duration_seconds * 1_000,
                        3,
                    ),
                },
            )

            return LLMResult(
                answer=answer,
                provider=provider,
                requested_model=requested_model,
                response_model=response_model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                estimated_cost=estimated_cost,
                finish_reason=finish_reason,
            )

    except Exception as error:
        gen_ai_request_count.add(
            1,
            attributes={
                **metric_attributes,
                "status": "error",
            },
        )

        logger.exception(
            "LLM request failed",
            extra={
                "event": "llm_request_failed",
                "operation": operation,
                "provider": provider,
                "model": requested_model,
                "status": "error",
                "scenario": scenario.value,
                "retry_count": 0,
                "error_category": "provider_error",
                "error_type": type(error).__name__,
            },
        )

        raise

    finally:
        duration_seconds = perf_counter() - started_at

        gen_ai_request_duration.record(
            duration_seconds,
            attributes={
                **metric_attributes,
                "status": (
                    "error"
                    if scenario in {Scenario.ERROR, Scenario.FAILURE}
                    else "success"
                ),
            },
        )

def create_high_token_answer() -> str:
    """Create a deterministic large response for token dashboards."""

    paragraph = (
        "OpenTelemetry traces reveal latency across application operations, "
        "metrics show aggregate performance and error behaviour, and "
        "structured logs provide detailed correlated diagnostic context. "
    )

    return paragraph * 120
