from __future__ import annotations

from datetime import datetime

from app.shared.application.base_dto import BaseDTO

from app.context.communication.application.dto.attachment_dto import AttachmentDTO
from app.context.communication.application.dto.reaction_dto import ReactionDTO


class MessageDTO(BaseDTO):
    """
    DTO сообщения чата (Communication BC).

    Атрибуты:
        id: UUID сообщения.
        chat_id: UUID чата.
        thread_id: UUID треда (None — основное сообщение).
        sender_id: UUID отправителя ("" для system).
        content: Содержимое (текст).
        content_format: markdown/wysiwyg.
        message_type: text/system/file/voice/etc.
        reply_to_id: UUID сообщения, на которое отвечают.
        attachments: Вложения.
        reactions: Реакции.
        is_edited: Было ли отредактировано.
        is_deleted: Soft-deleted ли.
        created_at: Время отправки.
        updated_at: Время последнего обновления.
    """

    id: str
    chat_id: str
    thread_id: str | None = None
    sender_id: str
    content: str | None = None
    content_format: str = "markdown"
    message_type: str = "text"
    reply_to_id: str | None = None
    attachments: list[AttachmentDTO] = []
    reactions: list[ReactionDTO] = []
    is_edited: bool = False
    is_deleted: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None


class MessageListDTO(BaseDTO):
    """Список сообщений с метаданными пагинации."""

    items: list[MessageDTO] = []
    total: int = 0
    has_more: bool = False
