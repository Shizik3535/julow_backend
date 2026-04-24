from __future__ import annotations

from enum import Enum


class StorageOwnerType(Enum):
    """
    Тип владельца хранилища.

    Новые типы владельцев = значение enum.

    Значения:
        WORKSPACE: Workspace
        ORGANIZATION: Организация
    """

    WORKSPACE = "workspace"
    ORGANIZATION = "organization"
