from __future__ import annotations

from enum import Enum


class WorkflowStatusCategory(Enum):
    """
    Категория статуса workflow.

    Группирует произвольные статусы в агрегированные категории.

    Значения:
        TODO: К выполнению
        IN_PROGRESS: В работе
        DONE: Выполнено
        CANCELLED: Отменено
        BLOCKED: Заблокировано
        REVIEW: На ревью
    """

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"
    REVIEW = "review"
