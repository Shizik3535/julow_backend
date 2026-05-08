from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AddCommentReactionRequest(BaseModel):
    """Запрос добавления реакции на комментарий."""

    model_config = ConfigDict(from_attributes=True)

    emoji: str = Field(
        ...,
        description="Unicode emoji",
        examples=["👍"],
    )
