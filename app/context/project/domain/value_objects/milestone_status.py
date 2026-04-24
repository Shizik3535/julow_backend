from __future__ import annotations

from enum import Enum


class MilestoneStatus(Enum):
    """
    Статус milestone.

    Значения:
        NOT_STARTED: Не начат
        IN_PROGRESS: В работе
        COMPLETED: Завершён
        OVERDUE: Просрочен
    """

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
