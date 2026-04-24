from __future__ import annotations

from enum import Enum


class RecurrencePattern(Enum):
    """
    Паттерн повторения.

    Дубликат из Task BC — может расходиться в будущем.

    Значения:
        DAILY: Ежедневно
        WEEKLY: Еженедельно
        BIWEEKLY: Раз в две недели
        MONTHLY: Ежемесячно
    """

    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
