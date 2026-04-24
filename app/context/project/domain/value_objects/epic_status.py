from __future__ import annotations

from enum import Enum


class EpicStatus(Enum):
    """
    Статус эпика.

    Значения:
        OPEN: Открыт
        IN_PROGRESS: В работе
        DONE: Завершён
        CANCELLED: Отменён
    """

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"
