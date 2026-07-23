"""Request and response models for the AI endpoint."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AskRequest(BaseModel):
    """A user's question submitted to the simulated AI assistant."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "question": "Why is my API slow?"
                }
            ]
        }
    )

    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Technical question submitted to the assistant.",
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        """Trim whitespace and reject blank questions."""

        value = value.strip()

        if not value:
            raise ValueError(
                "Question must not be empty or contain only whitespace."
            )

        return value


class AskResponse(BaseModel):
    """Response returned by the simulated AI assistant."""

    answer: str = Field(
        ...,
        description="Generated answer.",
    )

    provider: str = Field(
        ...,
        description="Configured LLM provider.",
    )

    model: str = Field(
        ...,
        description="Configured LLM model.",
    )