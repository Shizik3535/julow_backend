from __future__ import annotations

from enum import Enum


class MeetingStatus(Enum):
    """
    Статус совещания.

    Значения:
        SCHEDULED: Запланировано
        IN_PROGRESS: В процессе
        COMPLETED: Завершено
        CANCELLED: Отменено
    """

    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
