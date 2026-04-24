from __future__ import annotations

from enum import Enum


class TaskPriority(Enum):
    """
    Приоритет задачи.

    Значения:
        CRITICAL: Критический
        HIGH: Высокий
        MEDIUM: Средний
        LOW: Низкий
        NONE: Без приоритета
    """

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"
