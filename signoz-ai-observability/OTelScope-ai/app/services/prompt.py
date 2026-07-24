"""Prompt rendering service."""

from dataclasses import dataclass

from opentelemetry import trace

from app.core.scenarios import (
    Scenario,
    get_scenario_timings,
    simulate_delay,
)

tracer = trace.get_tracer(__name__)


@dataclass(frozen=True)
class PromptResult:
    """Rendered prompt metadata."""

    text: str
    template_name: str
    template_version: str


def render_prompt(
    question: str,
    context_documents: list[str],
    scenario: Scenario,
) -> PromptResult:
    """Render the deterministic technical-support prompt."""

    timings = get_scenario_timings(scenario)

    with tracer.start_as_current_span("prompt.render") as span:
        simulate_delay(timings.prompt_seconds)

        context_text = "\n".join(context_documents)

        rendered_prompt = (
            "You are a technical support assistant.\n\n"
            f"Context:\n{context_text}\n\n"
            f"Question:\n{question}"
        )

        span.set_attribute(
            "app.scenario",
            scenario.value,
        )
        span.set_attribute(
            "app.prompt.template_name",
            "technical-support",
        )
        span.set_attribute(
            "app.prompt.template_version",
            "1.0",
        )
        span.set_attribute(
            "app.prompt.question_length",
            len(question),
        )
        span.set_attribute(
            "app.prompt.rendered_length",
            len(rendered_prompt),
        )
        span.set_attribute(
            "app.prompt.context_count",
            len(context_documents),
        )

        return PromptResult(
            text=rendered_prompt,
            template_name="technical-support",
            template_version="1.0",
        )