from __future__ import annotations

from app.shared.application.base_dto import BaseDTO
from app.context.identity.application.dto.session_dto import SessionDTO


class SessionListDTO(BaseDTO):
    """
    DTO списка сессий (Identity BC).

    Обёртка для возврата списка сессий из QueryHandler.

    Атрибуты:
        items: Список сессий.
        total: Общее количество.
    """

    items: list[SessionDTO]
    total: int
