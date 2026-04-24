from __future__ import annotations

from enum import Enum


class SprintStatus(Enum):
    """
    Статус спринта.

    Значения:
        PLANNING: Планирование
        ACTIVE: Активный
        COMPLETED: Завершён
        CANCELLED: Отменён
    """

    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
