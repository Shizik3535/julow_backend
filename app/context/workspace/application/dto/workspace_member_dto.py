from __future__ import annotations

from datetime import datetime

from app.shared.application.base_dto import BaseDTO


class WorkspaceMemberDTO(BaseDTO):
    """
    DTO участника workspace (Workspace BC).

    Атрибуты:
        id: Идентификатор записи участника.
        user_id: ID пользователя.
        display_name: Отображаемое имя в рамках workspace.
        role_id: ID роли.
        joined_at: Время присоединения.
        is_active: Активен ли участник.
        source: Источник (DIRECT, ORGANIZATION, PARENT_WORKSPACE, INVITATION_LINK).
        invited_by: ID пригласившего.
    """

    id: str
    user_id: str
    display_name: str | None = None
    role_id: str
    joined_at: datetime
    is_active: bool
    source: str
    invited_by: str | None = None


class WorkspaceMemberListDTO(BaseDTO):
    """Список участников workspace."""

    items: list[WorkspaceMemberDTO]
    total: int
