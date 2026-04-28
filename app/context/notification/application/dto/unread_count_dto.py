from __future__ import annotations

from app.shared.application.base_dto import BaseDTO


class UnreadCountDTO(BaseDTO):
    """
    DTO количества непрочитанных уведомлений.

    Атрибуты:
        total: Общее количество непрочитанных.
        by_workspace: Количество по workspace.
    """

    total: int = 0
    by_workspace: dict[str, int] = {}
