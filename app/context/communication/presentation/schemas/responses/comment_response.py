from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.context.communication.presentation.schemas.responses.attachment_response import (
    AttachmentResponse,
)
from app.context.communication.presentation.schemas.responses.reaction_response import (
    ReactionResponse,
)


class CommentResponse(BaseModel):
    """Ответ с данными комментария."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID комментария")
    author_id: str = Field(..., description="UUID автора")
    target_type: str = Field(..., description="Тип комментируемой сущности")
    target_id: str = Field(..., description="UUID комментируемой сущности")
    content: str | None = Field(default=None, description="Текст комментария")
    content_format: str = Field(default="markdown", description="Формат содержимого")
    parent_comment_id: str | None = Field(
        default=None, description="UUID родительского комментария"
    )
    attachments: list[AttachmentResponse] = Field(
        default_factory=list, description="Вложения"
    )
    reactions: list[ReactionResponse] = Field(
        default_factory=list, description="Реакции"
    )
    is_pinned: bool = Field(default=False, description="Закреплён ли")
    is_system: bool = Field(default=False, description="Системный ли")
    is_deleted: bool = Field(default=False, description="Soft-deleted ли")
    created_at: datetime | None = Field(default=None, description="Время создания (UTC)")
    updated_at: datetime | None = Field(
        default=None, description="Время последнего обновления (UTC)"
    )
