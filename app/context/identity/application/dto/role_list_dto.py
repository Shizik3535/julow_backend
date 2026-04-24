from __future__ import annotations

from app.shared.application.base_dto import BaseDTO
from app.context.identity.application.dto.role_dto import RoleDTO


class RoleListDTO(BaseDTO):
    """
    DTO списка ролей (Identity BC).

    Обёртка для возврата списка ролей из QueryHandler.

    Атрибуты:
        items: Список ролей.
        total: Общее количество.
    """

    items: list[RoleDTO]
    total: int
