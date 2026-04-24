from __future__ import annotations

from datetime import datetime

from app.shared.application.base_dto import BaseDTO


class OrgRoleDTO(BaseDTO):
    """
    DTO роли организации (Organization BC).

    Атрибуты:
        id: Идентификатор роли.
        org_id: ID организации (пустая строка для системных ролей).
        name: Название роли.
        permissions: Список разрешений.
        is_system: Является ли роль системной.
        description: Описание роли.
        scope: Область действия роли.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    id: str
    org_id: str = ""
    name: str = ""
    permissions: list[str] = []
    is_system: bool = False
    description: str | None = None
    scope: str = "ORG"
    created_at: datetime
    updated_at: datetime


class OrgRoleListDTO(BaseDTO):
    """Список ролей с общим количеством."""

    items: list[OrgRoleDTO]
    total: int
