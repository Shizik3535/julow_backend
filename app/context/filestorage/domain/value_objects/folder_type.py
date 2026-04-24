from __future__ import annotations

from enum import Enum


class FolderType(Enum):
    """
    Тип папки.

    Значения:
        REGULAR: Обычная папка
        PROJECT: Привязана к проекту (auto-created)
        SHARED: Расшаренная папка
        SYSTEM: Системная (не удаляется)
    """

    REGULAR = "regular"
    PROJECT = "project"
    SHARED = "shared"
    SYSTEM = "system"
