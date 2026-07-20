"""Request and response models for the AI endpoint."""

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    """A user's question submitted to the simulated AI assistant."""

    question: str = Field(
        ...,
        min_length=1,
        max_length=2_000,
        description="The technical question to send to the assistant.",
        examples=["Why is my API slow?"],
    )


class AskResponse(BaseModel):
    """Response returned by the simulated AI assistant."""

    answer: str
    provider: str
    model: str
