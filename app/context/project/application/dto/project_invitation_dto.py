from __future__ import annotations

from datetime import datetime
from typing import Any

from app.shared.application.base_dto import BaseDTO


class ProjectInvitationDTO(BaseDTO):
    """
    DTO приглашения в проект (Project BC).

    Атрибуты:
        id: Идентификатор приглашения.
        project_id: ID проекта.
        workspace_id: ID workspace.
        email: Email (для email-приглашений).
        link: Данные токена ссылки/кода (dict) или None.
        role_id: ID роли проекта.
        invited_by: ID пригласившего.
        invited_at: Время приглашения.
        status: Статус (pending, accepted, declined, expired, revoked).
        user_id: ID пользователя, принявшего/отклонившего.
        project_name: Удобное имя проекта (для отображения в UI).
        workspace_slug: Slug workspace (для построения ссылок).
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    id: str
    project_id: str
    workspace_id: str
    email: str | None = None
    link: dict[str, Any] | None = None
    role_id: str
    invited_by: str
    invited_at: datetime
    status: str
    user_id: str | None = None
    project_name: str | None = None
    workspace_slug: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ProjectInvitationListDTO(BaseDTO):
    """Список приглашений в проект."""

    items: list[ProjectInvitationDTO]
    total: int
