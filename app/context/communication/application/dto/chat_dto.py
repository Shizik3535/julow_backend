from __future__ import annotations

from datetime import datetime

from app.shared.application.base_dto import BaseDTO


class ChatMemberDTO(BaseDTO):
    """DTO участника чата."""

    user_id: str
    role: str
    joined_at: datetime | None = None
    last_read_at: datetime | None = None


class ThreadDTO(BaseDTO):
    """DTO треда внутри чата."""

    id: str
    parent_message_id: str
    title: str | None = None
    is_resolved: bool = False
    created_at: datetime | None = None


class ChatDTO(BaseDTO):
    """
    DTO чата (Communication BC).

    Атрибуты:
        id: UUID чата.
        chat_type: dm/group/channel/announcement.
        name: Название (для group/channel/announcement).
        description: Описание.
        icon: Имя иконки.
        color: HEX-цвет.
        workspace_id: UUID workspace (для channel/announcement).
        members: Участники.
        threads: Треды.
        last_message_at: Время последнего сообщения.
        is_archived: Архивирован ли.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    id: str
    chat_type: str
    name: str | None = None
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    workspace_id: str | None = None
    members: list[ChatMemberDTO] = []
    threads: list[ThreadDTO] = []
    last_message_at: datetime | None = None
    is_archived: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ChatListDTO(BaseDTO):
    """Список чатов с метаданными пагинации."""

    items: list[ChatDTO] = []
    total: int = 0
