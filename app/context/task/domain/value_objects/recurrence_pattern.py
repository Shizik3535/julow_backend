from __future__ import annotations

from enum import Enum


class RecurrencePattern(Enum):
    """
    Паттерн повторения задачи.

    Значения:
        DAILY: Ежедневно
        WEEKLY: Еженедельно
        BIWEEKLY: Раз в две недели
        MONTHLY: Ежемесячно
        QUARTERLY: Ежеквартально
    """

    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
