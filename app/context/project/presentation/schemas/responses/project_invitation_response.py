from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProjectInvitationResponse(BaseModel):
    """
    Ответ с данными приглашения в проект.

    Поля:
        id: UUID приглашения.
        project_id: UUID проекта.
        workspace_id: UUID workspace проекта.
        email: Email приглашаемого (для email-приглашений).
        link: Данные токена ссылки/кода (dict) или None.
        role_id: UUID роли проекта.
        invited_by: UUID пригласившего.
        invited_at: Время отправки (UTC).
        status: pending / accepted / declined / expired / revoked.
        user_id: UUID пользователя, принявшего/отклонившего.
        project_name: Имя проекта (для отображения в UI).
        workspace_slug: Slug workspace (для построения ссылок).
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID приглашения")
    project_id: str = Field(..., description="UUID проекта")
    workspace_id: str = Field(..., description="UUID workspace")
    email: str | None = Field(default=None, description="Email приглашаемого")
    link: dict[str, Any] | None = Field(default=None, description="Данные ссылки/кода")
    role_id: str = Field(..., description="UUID роли проекта")
    invited_by: str = Field(..., description="UUID пригласившего")
    invited_at: datetime = Field(..., description="Время приглашения (UTC)")
    status: str = Field(..., description="Статус приглашения")
    user_id: str | None = Field(default=None, description="UUID принявшего/отклонившего")
    project_name: str | None = Field(default=None, description="Имя проекта")
    workspace_slug: str | None = Field(default=None, description="Slug workspace")
    created_at: datetime | None = Field(None, description="Дата создания (UTC)")
    updated_at: datetime | None = Field(None, description="Дата последнего обновления (UTC)")
