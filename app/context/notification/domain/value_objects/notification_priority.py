from __future__ import annotations

from enum import Enum


class NotificationPriority(Enum):
    """
    Приоритет уведомления.

    Значения:
        LOW: Низкий
        MEDIUM: Средний
        HIGH: Высокий
        URGENT: Срочный
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
