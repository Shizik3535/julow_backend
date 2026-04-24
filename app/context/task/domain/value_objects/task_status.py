from __future__ import annotations

from enum import Enum


class TaskStatus(Enum):
    """
    Жизненный цикл задачи в рамках Task BC.

    Не путать с workflow status из Project BC.
    ACTIVE — рабочее состояние, ARCHIVED — архив, DELETED — soft delete.

    Значения:
        ACTIVE: Активная задача
        ARCHIVED: Архивированная задача
        DELETED: Удалённая задача (soft delete)
    """

    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
