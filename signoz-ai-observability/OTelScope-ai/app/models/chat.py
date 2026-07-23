"""Request and response models for the chat API."""

from pydantic import BaseModel, Field, field_validator

from app.core.scenarios import Scenario


class AskRequest(BaseModel):
    """Request body for the agent workflow."""

    question: str = Field(
        min_length=1,
        max_length=2_000,
    )

    session_id: str | None = Field(
        default=None,
        max_length=200,
    )

    scenario: Scenario = Scenario.NORMAL

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        """Trim and reject blank questions."""

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError("Question must not be blank.")

        return normalized_value

    @field_validator("session_id")
    @classmethod
    def validate_session_id(
        cls,
        value: str | None,
    ) -> str | None:
        """Trim and reject explicitly blank session identifiers."""

        if value is None:
            return None

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError("Session ID must not be blank.")

        return normalized_value


class AskResponse(BaseModel):
    """Response returned by the agent workflow."""

    answer: str
    provider: str
    model: str
    request_id: str
    session_id: str
    scenario: Scenario