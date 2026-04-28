from __future__ import annotations

from datetime import datetime

from app.shared.application.base_dto import BaseDTO


class TeamDTO(BaseDTO):
    """
    DTO команды (Organization BC).

    Атрибуты:
        id: Идентификатор команды.
        org_id: ID организации.
        name: Название команды.
        description: Описание.
        lead_id: ID лидера команды.
        member_ids: Список ID участников.
        icon: Название иконки.
        is_active: Активна ли команда.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    id: str
    org_id: str
    name: str
    description: str | None = None
    lead_id: str | None = None
    member_ids: list[str] = []
    icon: str | None = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class TeamListDTO(BaseDTO):
    """Список команд с общим количеством."""

    items: list[TeamDTO]
    total: int
