from __future__ import annotations

from datetime import datetime
from typing import Any

from app.shared.application.base_dto import BaseDTO


class WorkspaceDTO(BaseDTO):
    """
    DTO workspace (Workspace BC).

    Атрибуты:
        id: Идентификатор workspace.
        name: Название workspace.
        status: Статус (ACTIVE, ARCHIVED, SUSPENDED, PENDING_DELETION).
        workspace_type: Тип (PERSONAL, TEAM, ENTERPRISE).
        organization_id: ID организации (None — независимый).
        parent_workspace_id: ID родительского workspace (None — корневой).
        personalization: Настройки персонализации (dict).
        owner_ids: Список ID владельцев.
        security_policy: Политика безопасности (dict).
        membership_policy: Политика членства (dict).
        limits: Лимиты workspace (dict).
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    id: str
    name: str
    status: str
    workspace_type: str
    organization_id: str | None = None
    parent_workspace_id: str | None = None
    personalization: dict[str, Any] | None = None
    owner_ids: list[str] | None = None
    security_policy: dict[str, Any] | None = None
    membership_policy: dict[str, Any] | None = None
    limits: dict[str, Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class WorkspaceListDTO(BaseDTO):
    """Список workspace."""

    items: list[WorkspaceDTO]
    total: int
