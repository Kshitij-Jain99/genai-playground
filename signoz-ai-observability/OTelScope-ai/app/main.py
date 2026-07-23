"""Main FastAPI application for OTelScope AI."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.models.chat import AskRequest, AskResponse
from app.services.agent import run_agent
from app.telemetry.logging import configure_logging, get_logger

settings = get_settings()

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Handle application startup and shutdown events."""

    logger.info(
        "Application started",
        extra={
            "event": "application_started",
            "operation": "application.lifecycle",
            "status": "success",
            "app_version": settings.app_version,
        },
    )

    yield

    logger.info(
        "Application stopped",
        extra={
            "event": "application_stopped",
            "operation": "application.lifecycle",
            "status": "success",
            "app_version": settings.app_version,
        },
    )

    print(
        f"Starting {settings.app_name} "
        f"version={settings.app_version} "
        f"environment={settings.app_environment}"
    )

    yield

    print(f"Stopping {settings.app_name}")


app = FastAPI(
    title=settings.app_name,
    description=(
        "An OpenTelemetry-instrumented AI application "
        "for learning GenAI observability with SigNoz."
    ),
    version=settings.app_version,
    lifespan=lifespan,
)

@app.exception_handler(RuntimeError)
async def runtime_error_handler(
    _: Request,
    error: RuntimeError,
) -> JSONResponse:
    """Return a safe response for simulated provider failures."""

    logger.error(
        "Request failed",
        extra={
            "event": "request_failed",
            "operation": "POST /ask",
            "status": "error",
            "error_category": "runtime_error",
            "error_type": type(error).__name__,
        },
    )

    return JSONResponse(
        status_code=503,
        content={
            "detail": "The simulated AI provider is unavailable."
        },
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://127.0.0.1",
        f"http://localhost:{settings.app_port}",
        f"http://127.0.0.1:{settings.app_port}",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get(
    "/",
    tags=["General"],
    summary="Project information",
)
async def root() -> dict[str, str]:
    """Return project information."""

    return {
        "project": settings.app_name,
        "service": settings.app_service_name,
        "version": settings.app_version,
        "environment": settings.app_environment,
        "documentation": "/docs",
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Check application health",
)
async def health() -> dict[str, str]:
    """Return the current health status."""

    return {
        "status": "healthy",
        "service": settings.app_service_name,
        "version": settings.app_version,
        "environment": settings.app_environment,
    }


@app.post(
    "/ask",
    response_model=AskResponse,
    tags=["AI"],
    summary="Ask the simulated AI assistant",
)
async def ask(request: AskRequest) -> AskResponse:
    """Run the simulated observable AI workflow."""

    result = run_agent(
        question=request.question,
        session_id=request.session_id,
    )

    return AskResponse(
        answer=result.answer,
        provider=result.provider,
        model=result.model,
        request_id=result.request_id,
        session_id=result.session_id,
    )