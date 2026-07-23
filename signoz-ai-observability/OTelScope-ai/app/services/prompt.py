"""Prompt rendering service."""

from dataclasses import dataclass

from app.telemetry.tracing import tracer


@dataclass(frozen=True)
class RenderedPrompt:
    """Internal representation of a rendered prompt."""

    text: str
    template_name: str
    template_version: str


def render_prompt(
    question: str,
    context_documents: list[str],
) -> RenderedPrompt:
    """Create the simulated LLM prompt."""

    with tracer.start_as_current_span("prompt.render") as span:
        template_name = "technical-support"
        template_version = "1.0"

        context = "\n".join(context_documents)

        rendered_text = (
            "You are a technical troubleshooting assistant.\n"
            "Use the supplied context when relevant.\n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{question}"
        )

        span.set_attribute(
            "app.prompt.template_name",
            template_name,
        )
        span.set_attribute(
            "app.prompt.template_version",
            template_version,
        )
        span.set_attribute(
            "app.prompt.question_length",
            len(question),
        )
        span.set_attribute(
            "app.prompt.context_document_count",
            len(context_documents),
        )
        span.set_attribute(
            "app.prompt.rendered_length",
            len(rendered_text),
        )

        return RenderedPrompt(
            text=rendered_text,
            template_name=template_name,
            template_version=template_version,
        )