from __future__ import annotations

from datetime import datetime

from app.shared.application.base_dto import BaseDTO


class WorkspaceRoleDTO(BaseDTO):
    """
    DTO роли workspace (Workspace BC).

    Атрибуты:
        id: Идентификатор роли.
        workspace_id: ID workspace (пустая строка для системных).
        name: Название роли.
        permissions: Список разрешений.
        is_system: Является ли роль системной.
        description: Описание.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    id: str
    workspace_id: str
    name: str
    permissions: list[str]
    is_system: bool
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class WorkspaceRoleListDTO(BaseDTO):
    """Список ролей workspace."""

    items: list[WorkspaceRoleDTO]
    total: int
