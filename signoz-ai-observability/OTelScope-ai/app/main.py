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
        "An OpenTelemetry-instrumented AI application "
        "for learning GenAI observability with SigNoz."
    ),
    version=settings.app_version,
    lifespan=lifespan,
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
    """Return a deterministic simulated AI response."""

    answer = f"This is a simulated answer for: {request.question}"

    return AskResponse(
        answer=answer,
        provider=settings.llm_provider,
        model=settings.llm_model,
    )