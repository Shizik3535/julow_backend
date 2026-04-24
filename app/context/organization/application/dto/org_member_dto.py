from __future__ import annotations

from datetime import datetime

from app.shared.application.base_dto import BaseDTO


class OrgMemberDTO(BaseDTO):
    """
    DTO участника организации (Organization BC).

    Атрибуты:
        id: Идентификатор записи участника.
        user_id: ID пользователя из Identity BC.
        display_name: Отображаемое имя в рамках организации.
        role_id: ID роли (ссылка на OrgRole).
        joined_at: Время присоединения.
        is_active: Активен ли участник.
        invited_by: ID пригласившего.
    """

    id: str
    user_id: str
    display_name: str | None = None
    role_id: str = ""
    joined_at: datetime
    is_active: bool = True
    invited_by: str | None = None


class OrgMemberListDTO(BaseDTO):
    """Список участников организации с общим количеством."""

    items: list[OrgMemberDTO]
    total: int
