from __future__ import annotations

from datetime import datetime
from typing import Any

from app.shared.application.base_dto import BaseDTO


class WorkspaceInvitationDTO(BaseDTO):
    """
    DTO приглашения в workspace (Workspace BC).

    Атрибуты:
        id: Идентификатор приглашения.
        workspace_id: ID workspace.
        email: Email (для email-приглашений).
        link: Данные токена ссылки (dict) или None.
        role_id: ID роли.
        invited_by: ID пригласившего.
        invited_at: Время приглашения.
        status: Статус (PENDING, ACCEPTED, DECLINED, EXPIRED, REVOKED).
        approved_by: ID подтвердившего.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    id: str
    workspace_id: str
    email: str | None = None
    link: dict[str, Any] | None = None
    role_id: str
    invited_by: str
    invited_at: datetime
    status: str
    approved_by: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class WorkspaceInvitationListDTO(BaseDTO):
    """Список приглашений workspace."""

    items: list[WorkspaceInvitationDTO]
    total: int
