from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChatMemberResponse(BaseModel):
    """Ответ с данными участника чата."""

    model_config = ConfigDict(from_attributes=True)

    user_id: str = Field(..., description="UUID пользователя")
    role: str = Field(..., description="Роль (owner/admin/member/guest)")
    joined_at: datetime | None = Field(default=None, description="Время присоединения")
    last_read_at: datetime | None = Field(
        default=None, description="Время последнего прочтения"
    )


class ThreadResponse(BaseModel):
    """Ответ с данными треда."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID треда")
    parent_message_id: str = Field(..., description="UUID родительского сообщения")
    title: str | None = Field(default=None, description="Заголовок треда")
    is_resolved: bool = Field(default=False, description="Закрыт ли")
    created_at: datetime | None = Field(default=None, description="Время создания (UTC)")


class ChatResponse(BaseModel):
    """Ответ с данными чата."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID чата")
    chat_type: str = Field(..., description="dm/group/channel/announcement")
    name: str | None = Field(default=None, description="Название")
    description: str | None = Field(default=None, description="Описание")
    icon: str | None = Field(default=None, description="Имя иконки")
    color: str | None = Field(default=None, description="HEX-цвет")
    workspace_id: str | None = Field(default=None, description="UUID workspace")
    members: list[ChatMemberResponse] = Field(
        default_factory=list, description="Участники"
    )
    threads: list[ThreadResponse] = Field(
        default_factory=list, description="Треды"
    )
    last_message_at: datetime | None = Field(
        default=None, description="Время последнего сообщения"
    )
    is_archived: bool = Field(default=False, description="Архивирован ли")
    created_at: datetime | None = Field(default=None, description="Время создания (UTC)")
    updated_at: datetime | None = Field(
        default=None, description="Время последнего обновления (UTC)"
    )


class ChatListResponse(BaseModel):
    """Ответ со списком чатов."""

    model_config = ConfigDict(from_attributes=True)

    items: list[ChatResponse] = Field(default_factory=list)
    total: int = Field(default=0)
