from __future__ import annotations

from enum import Enum


class NotificationPriority(Enum):
    """
    Приоритет уведомления.

    Значения:
        LOW: Низкий
        NORMAL: Обычный
        HIGH: Высокий
        URGENT: Срочный
    """

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
