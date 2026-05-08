from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.context.communication.presentation.schemas.responses.comment_response import (
    CommentResponse,
)


class CommentListResponse(BaseModel):
    """Ответ со списком комментариев."""

    model_config = ConfigDict(from_attributes=True)

    items: list[CommentResponse] = Field(default_factory=list)
    total: int = Field(default=0, description="Общее количество")
