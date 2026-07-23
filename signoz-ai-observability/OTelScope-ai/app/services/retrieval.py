"""Local knowledge-base retrieval service."""

from dataclasses import dataclass
from time import perf_counter

from app.core.config import get_settings
from app.telemetry.metrics import retrieval_duration
from app.telemetry.tracing import tracer
from app.telemetry.logging import get_logger
from time import perf_counter, sleep

from app.core.scenarios import Scenario, get_scenario_timings

settings = get_settings()

logger = get_logger(__name__)


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
    scenario: Scenario,
    top_k: int = 2,
) -> RetrievalResult:
    """Search the deterministic local knowledge base."""

    started_at = perf_counter()
    source = "local-memory"
    status = "success"
    document_count = 0

    timings = get_scenario_timings(scenario)

    try:
        with tracer.start_as_current_span("retrieval.search") as span:
            sleep(timings.retrieval_seconds)

            if scenario == Scenario.RETRIEVAL_EMPTY:
                selected_documents: list[str] = []
            else:
                normalized_query = query.lower()
                matching_documents: list[str] = []

                for keywords, document in KNOWLEDGE_BASE:
                    if any(
                        keyword in normalized_query
                        for keyword in keywords
                    ):
                        matching_documents.append(document)

                if not matching_documents:
                    matching_documents.append(
                        "No exact knowledge-base match was found. "
                        "Provide a general troubleshooting response."
                    )

                selected_documents = matching_documents[:top_k]

            document_count = len(selected_documents)

            span.set_attribute(
                "app.scenario",
                scenario.value,
            )
            span.set_attribute(
                "app.retrieval.source",
                source,
            )
            span.set_attribute(
                "app.retrieval.query_length",
                len(query),
            )
            span.set_attribute(
                "app.retrieval.document_count",
                document_count,
            )
            span.set_attribute(
                "app.retrieval.top_k",
                top_k,
            )
            span.set_attribute(
                "app.retrieval.empty",
                document_count == 0,
            )

            duration_seconds = perf_counter() - started_at

            logger.info(
                "Retrieval completed",
                extra={
                    "event": "retrieval_completed",
                    "operation": "retrieval.search",
                    "status": "success",
                    "scenario": scenario.value,
                    "retrieval_source": source,
                    "document_count": document_count,
                    "top_k": top_k,
                    "duration_ms": round(
                        duration_seconds * 1_000,
                        3,
                    ),
                },
            )

            return RetrievalResult(
                documents=selected_documents,
                source=source,
                top_k=top_k,
            )

    except Exception:
        status = "error"

        logger.exception(
            "Retrieval failed",
            extra={
                "event": "retrieval_failed",
                "operation": "retrieval.search",
                "status": status,
                "scenario": scenario.value,
                "retrieval_source": source,
            },
        )

        raise

    finally:
        duration_seconds = perf_counter() - started_at

        retrieval_duration.record(
            duration_seconds,
            attributes={
                "source": source,
                "environment": settings.app_environment,
                "status": status,
                "scenario": scenario.value,
            },
        )