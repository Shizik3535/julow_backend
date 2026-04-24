from __future__ import annotations

from app.shared.application.base_dto import BaseDTO


class RoleDTO(BaseDTO):
    """
    DTO роли (Identity BC).

    Атрибуты:
        id: Идентификатор роли.
        name: Название роли.
        permissions: Список разрешений.
        is_system: Является ли роль системной.
        description: Описание роли.
    """

    id: str
    name: str
    permissions: list[str]
    is_system: bool
    description: str | None = None
