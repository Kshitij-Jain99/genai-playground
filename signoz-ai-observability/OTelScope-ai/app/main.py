"""Main FastAPI application for OTelScope AI."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.models.chat import AskRequest, AskResponse

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Handle application startup and shutdown events."""

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
        "A learning project for OpenTelemetry instrumentation, "
        "SigNoz dashboards, and Generative AI observability."
    ),
    version=settings.app_version,
    lifespan=lifespan,
)

# This is acceptable for local Phase 1 development.
# Restrict allowed origins before exposing the application publicly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1"],
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
    """Return basic information about the project."""

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
    """Return the current health status of the API."""

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
    """Return a deterministic simulated AI response."""

    normalized_question = request.question.strip()

    answer = (
        "This is a simulated answer for: "
        f"{normalized_question}"
    )

    return AskResponse(
        answer=answer,
        provider=settings.llm_provider,
        model=settings.llm_model,
    )
