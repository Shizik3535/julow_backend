from __future__ import annotations

from enum import Enum


class FileAccessLevel(Enum):
    """
    Уровень доступа к файлу/папке.

    Значения:
        VIEW: Просмотр
        COMMENT: Просмотр + комментирование
        EDIT: Редактирование
        ADMIN: Администрирование
        OWNER: Владелец
    """

    VIEW = "view"
    COMMENT = "comment"
    EDIT = "edit"
    ADMIN = "admin"
    OWNER = "owner"
