"""Simulated LLM generation service."""

from dataclasses import dataclass

from app.core.config import get_settings
from app.telemetry.tracing import tracer

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
    finish_reason: str


def estimate_token_count(text: str) -> int:
    """Return a simple token estimate for the simulated model."""

    return max(1, len(text.split()))


def generate_response(
    question: str,
    rendered_prompt: str,
    context_documents: list[str],
    tool_output: str,
) -> LLMResult:
    """Generate a deterministic simulated LLM response."""

    with tracer.start_as_current_span("llm.generate") as span:
        provider = settings.llm_provider
        requested_model = settings.llm_model
        response_model = settings.llm_model

        context_summary = context_documents[0]

        answer = (
            f"Simulated troubleshooting answer for: {question}. "
            f"Relevant context: {context_summary} "
            f"Diagnostic result: {tool_output}"
        )

        input_tokens = estimate_token_count(rendered_prompt)
        output_tokens = estimate_token_count(answer)
        finish_reason = "stop"

        span.set_attribute(
            "gen_ai.operation.name",
            "chat",
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

        return LLMResult(
            answer=answer,
            provider=provider,
            requested_model=requested_model,
            response_model=response_model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            finish_reason=finish_reason,
        )