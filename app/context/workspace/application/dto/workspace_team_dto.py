from __future__ import annotations

from datetime import datetime

from app.shared.application.base_dto import BaseDTO


class WorkspaceTeamDTO(BaseDTO):
    """
    DTO команды workspace (Workspace BC).

    Атрибуты:
        id: Идентификатор команды.
        workspace_id: ID workspace.
        name: Название команды.
        description: Описание.
        lead_id: ID лидера.
        member_ids: Список ID участников.
        icon: Название иконки.
        is_active: Активна ли команда.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    id: str
    workspace_id: str
    name: str
    description: str | None = None
    lead_id: str | None = None
    member_ids: list[str] | None = None
    icon: str | None = None
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None


class WorkspaceTeamListDTO(BaseDTO):
    """Список команд workspace."""

    items: list[WorkspaceTeamDTO]
    total: int
