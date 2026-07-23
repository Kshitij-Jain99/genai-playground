"""Main AI agent workflow orchestration service."""

from dataclasses import dataclass
from time import perf_counter
from uuid import uuid4

from opentelemetry.trace import Status, StatusCode
from app.telemetry.logging import get_logger

from app.core.config import get_settings
from app.services.llm import generate_response
from app.services.prompt import render_prompt
from app.services.retrieval import search_knowledge_base
from app.services.tools import execute_diagnostic_tool
from app.services.validation import validate_response
from app.telemetry.metrics import (
    agent_error_count,
    agent_run_count,
    agent_run_duration,
)
from app.telemetry.tracing import tracer

settings = get_settings()
logger = get_logger(__name__)

@dataclass(frozen=True)
class AgentResult:
    """Final result returned by the AI agent workflow."""

    answer: str
    provider: str
    model: str
    request_id: str
    session_id: str


def run_agent(
    question: str,
    session_id: str | None = None,
) -> AgentResult:
    """Run the complete simulated AI workflow."""

    request_id = str(uuid4())
    resolved_session_id = session_id or str(uuid4())

    started_at = perf_counter()
    status = "success"

    agent_name = "technical-support-agent"

    common_metric_attributes = {
        "agent_name": agent_name,
        "environment": settings.app_environment,
    }

    agent_run_count.add(
        1,
        attributes=common_metric_attributes,
    )

    with tracer.start_as_current_span("agent.run") as span:
        span.set_attribute(
            "app.agent.name",
            agent_name,
        )
        span.set_attribute(
            "app.agent.version",
            settings.app_version,
        )
        span.set_attribute(
            "app.request.id",
            request_id,
        )
        span.set_attribute(
            "app.session.id",
            resolved_session_id,
        )

        logger.info(
            "Agent run started",
            extra={
                "event": "agent_run_started",
                "operation": "agent.run",
                "status": "started",
                "agent_name": agent_name,
                "agent_version": settings.app_version,
            },
        )

        try:
            retrieval_result = search_knowledge_base(
                query=question,
                top_k=2,
            )

            prompt_result = render_prompt(
                question=question,
                context_documents=retrieval_result.documents,
            )

            tool_result = execute_diagnostic_tool(
                question=question,
            )

            llm_result = generate_response(
                question=question,
                rendered_prompt=prompt_result.text,
                context_documents=retrieval_result.documents,
                tool_output=tool_result.output,
            )

            validation_result = validate_response(
                answer=llm_result.answer,
            )

            span.set_attribute(
                "app.agent.success",
                validation_result.passed,
            )

            duration_seconds = perf_counter() - started_at

            logger.info(
                "Agent run completed",
                extra={
                    "event": "agent_run_completed",
                    "operation": "agent.run",
                    "provider": llm_result.provider,
                    "model": llm_result.response_model,
                    "status": "success",
                    "agent_name": agent_name,
                    "duration_ms": round(
                        duration_seconds * 1_000,
                        3,
                    ),
                },
            )

            return AgentResult(
                answer=llm_result.answer,
                provider=llm_result.provider,
                model=llm_result.response_model,
                request_id=request_id,
                session_id=resolved_session_id,
            )

        except Exception as error:
            status = "error"

            span.set_attribute(
                "app.agent.success",
                False,
            )

            span.record_exception(error)

            span.set_status(
                Status(
                    StatusCode.ERROR,
                    str(error),
                )
            )

            agent_error_count.add(
                1,
                attributes={
                    **common_metric_attributes,
                    "error_type": type(error).__name__,
                },
            )

            logger.exception(
                "Agent run failed",
                extra={
                    "event": "agent_run_failed",
                    "operation": "agent.run",
                    "status": "error",
                    "agent_name": agent_name,
                    "error_category": "workflow_error",
                    "error_type": type(error).__name__,
                },
            )

            raise

        finally:
            duration_seconds = perf_counter() - started_at

            agent_run_duration.record(
                duration_seconds,
                attributes={
                    **common_metric_attributes,
                    "status": status,
                },
            )