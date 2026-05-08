from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.context.communication.presentation.schemas.responses.attachment_response import (
    AttachmentResponse,
)
from app.context.communication.presentation.schemas.responses.reaction_response import (
    ReactionResponse,
)


class MessageResponse(BaseModel):
    """Ответ с данными сообщения чата."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID сообщения")
    chat_id: str = Field(..., description="UUID чата")
    thread_id: str | None = Field(default=None, description="UUID треда")
    sender_id: str = Field(..., description="UUID отправителя")
    content: str | None = Field(default=None, description="Текст")
    content_format: str = Field(default="markdown", description="Формат содержимого")
    message_type: str = Field(default="text", description="Тип сообщения")
    reply_to_id: str | None = Field(default=None, description="UUID сообщения-ответа")
    attachments: list[AttachmentResponse] = Field(default_factory=list)
    reactions: list[ReactionResponse] = Field(default_factory=list)
    is_edited: bool = Field(default=False, description="Было ли отредактировано")
    is_deleted: bool = Field(default=False, description="Soft-deleted ли")
    created_at: datetime | None = Field(default=None, description="Время создания (UTC)")
    updated_at: datetime | None = Field(
        default=None, description="Время последнего обновления (UTC)"
    )


class MessageListResponse(BaseModel):
    """Ответ со списком сообщений."""

    model_config = ConfigDict(from_attributes=True)

    items: list[MessageResponse] = Field(default_factory=list)
    total: int = Field(default=0)
    has_more: bool = Field(default=False)
