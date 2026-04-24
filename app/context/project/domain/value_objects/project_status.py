from __future__ import annotations

from enum import Enum


class ProjectStatus(Enum):
    """
    Статус проекта.

    Значения:
        ACTIVE: Проект активен
        ARCHIVED: Проект архивирован
        SUSPENDED: Проект приостановлен
        PENDING_DELETION: Запрос на удаление проекта
    """

    ACTIVE = "active"
    ARCHIVED = "archived"
    SUSPENDED = "suspended"
    PENDING_DELETION = "pending_deletion"
