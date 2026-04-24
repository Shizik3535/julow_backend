from __future__ import annotations

from enum import Enum


class FileStatus(Enum):
    """
    Жизненный цикл файла.

    Значения:
        ACTIVE: Активный
        TRASHED: В корзине (soft delete)
        DELETED: Окончательно удалён
    """

    ACTIVE = "active"
    TRASHED = "trashed"
    DELETED = "deleted"
