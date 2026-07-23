"""Local knowledge-base retrieval service."""

from dataclasses import dataclass

from app.telemetry.tracing import tracer


@dataclass(frozen=True)
class RetrievalResult:
    """Documents returned by the retrieval service."""

    documents: list[str]
    source: str
    top_k: int


KNOWLEDGE_BASE: list[tuple[tuple[str, ...], str]] = [
    (
        ("slow", "latency", "performance"),
        (
            "High API latency can be investigated using traces, "
            "dependency spans, database timings, and error rates."
        ),
    ),
    (
        ("trace", "tracing", "span"),
        (
            "A trace represents an end-to-end operation. "
            "Spans represent individual operations inside the trace."
        ),
    ),
    (
        ("opentelemetry", "otel"),
        (
            "OpenTelemetry provides APIs and SDKs for collecting "
            "traces, metrics, and logs."
        ),
    ),
    (
        ("signoz", "dashboard"),
        (
            "SigNoz receives OpenTelemetry data and provides "
            "traces, metrics, logs, dashboards, and alerts."
        ),
    ),
]


def search_knowledge_base(
    query: str,
    top_k: int = 2,
) -> RetrievalResult:
    """Search a small deterministic local knowledge base."""

    with tracer.start_as_current_span("retrieval.search") as span:
        normalized_query = query.lower()

        matching_documents: list[str] = []

        for keywords, document in KNOWLEDGE_BASE:
            if any(keyword in normalized_query for keyword in keywords):
                matching_documents.append(document)

        if not matching_documents:
            matching_documents.append(
                "No exact knowledge-base match was found. "
                "Provide a general technical troubleshooting response."
            )

        selected_documents = matching_documents[:top_k]

        span.set_attribute(
            "app.retrieval.source",
            "local-memory",
        )
        span.set_attribute(
            "app.retrieval.query_length",
            len(query),
        )
        span.set_attribute(
            "app.retrieval.document_count",
            len(selected_documents),
        )
        span.set_attribute(
            "app.retrieval.top_k",
            top_k,
        )

        return RetrievalResult(
            documents=selected_documents,
            source="local-memory",
            top_k=top_k,
        )