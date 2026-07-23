"""Prompt rendering service."""

from dataclasses import dataclass

from app.telemetry.tracing import tracer
from time import sleep

from app.core.scenarios import Scenario, get_scenario_timings


@dataclass(frozen=True)
class RenderedPrompt:
    """Internal representation of a rendered prompt."""

    text: str
    template_name: str
    template_version: str


def render_prompt(
    question: str,
    context_documents: list[str],
    scenario: Scenario,
) -> PromptResult:
    """Create the simulated LLM prompt."""

timings = get_scenario_timings(scenario)

with tracer.start_as_current_span("prompt.render") as span:
    sleep(timings.prompt_seconds)

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