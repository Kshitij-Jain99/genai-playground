"""Request and response models for the AI endpoint."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AskRequest(BaseModel):
    """A user's question submitted to the simulated AI assistant."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "question": "Why is my API slow?",
                    "session_id": "demo-session-001",
                }
            ]
        }
    )

    question: str = Field(
        ...,
        min_length=1,
        max_length=2_000,
        description="Technical question submitted to the assistant.",
    )

    session_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=128,
        description=(
            "Optional non-sensitive session identifier."
        ),
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        """Trim surrounding whitespace and reject blank questions."""

        normalized_question = value.strip()

        if not normalized_question:
            raise ValueError(
                "Question must not be empty or contain only whitespace."
            )

        return normalized_question

    @field_validator("session_id")
    @classmethod
    def validate_session_id(
        cls,
        value: str | None,
    ) -> str | None:
        """Normalize and validate the optional session identifier."""

        if value is None:
            return None

        normalized_session_id = value.strip()

        if not normalized_session_id:
            raise ValueError(
                "Session ID must not contain only whitespace."
            )

        return normalized_session_id


class AskResponse(BaseModel):
    """Response returned by the simulated AI assistant."""

    answer: str = Field(
        ...,
        description="Generated simulated answer.",
    )

    provider: str = Field(
        ...,
        description="Configured LLM provider.",
    )

    model: str = Field(
        ...,
        description="Configured LLM model.",
    )

    request_id: str = Field(
        ...,
        description="Identifier used to correlate the request with telemetry.",
    )

    session_id: str = Field(
        ...,
        description="Non-sensitive conversation session identifier.",
    )