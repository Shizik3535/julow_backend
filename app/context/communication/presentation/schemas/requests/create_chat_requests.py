from __future__ import annotations

from pydantic import BaseModel, Field


class CreateDMRequest(BaseModel):
    """Тело запроса на создание/получение DM."""

    other_user_id: str = Field(..., description="UUID собеседника")


class CreateGroupChatRequest(BaseModel):
    """Тело запроса на создание группового чата."""

    name: str = Field(..., min_length=1, max_length=255, description="Название")


class CreateChannelRequest(BaseModel):
    """Тело запроса на создание канала."""

    name: str = Field(..., min_length=1, max_length=255, description="Название")
    workspace_id: str = Field(..., description="UUID workspace")


class CreateAnnouncementRequest(BaseModel):
    """Тело запроса на создание канала объявлений."""

    name: str = Field(..., min_length=1, max_length=255, description="Название")
    workspace_id: str = Field(..., description="UUID workspace")


class UpdateChatInfoRequest(BaseModel):
    """Тело запроса на обновление информации о чате."""

    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    icon: str | None = Field(default=None, max_length=64)
    color: str | None = Field(default=None, description="HEX-цвет (#RRGGBB)")


class AddChatMemberRequest(BaseModel):
    """Тело запроса на добавление участника."""

    user_id: str = Field(..., description="UUID пользователя")


class ChangeChatMemberRoleRequest(BaseModel):
    """Тело запроса на изменение роли участника."""

    role: str = Field(..., description="owner/admin/member/guest")


class CreateThreadRequest(BaseModel):
    """Тело запроса на создание треда."""

    parent_message_id: str = Field(..., description="UUID родительского сообщения")
    title: str | None = Field(default=None, max_length=255)
