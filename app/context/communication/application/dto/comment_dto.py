from __future__ import annotations

from datetime import datetime

from app.shared.application.base_dto import BaseDTO

from app.context.communication.application.dto.attachment_dto import AttachmentDTO
from app.context.communication.application.dto.reaction_dto import ReactionDTO


class CommentDTO(BaseDTO):
    """
    DTO комментария (Communication BC).

    Атрибуты:
        id: UUID комментария.
        author_id: UUID автора (пустая строка для системных).
        target_type: Тип комментируемой сущности (task/project/...).
        target_id: UUID комментируемой сущности (opaque).
        content: Содержимое (текст).
        content_format: Формат содержимого (markdown/wysiwyg).
        parent_comment_id: UUID родительского комментария (для ответов).
        attachments: Вложения.
        reactions: Реакции.
        is_pinned: Закреплён ли.
        is_system: Системный ли.
        is_deleted: Soft-deleted ли.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    id: str
    author_id: str
    target_type: str
    target_id: str
    content: str | None = None
    content_format: str = "markdown"
    parent_comment_id: str | None = None
    attachments: list[AttachmentDTO] = []
    reactions: list[ReactionDTO] = []
    is_pinned: bool = False
    is_system: bool = False
    is_deleted: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CommentListDTO(BaseDTO):
    """Список комментариев с метаданными пагинации."""

    items: list[CommentDTO] = []
    total: int = 0
