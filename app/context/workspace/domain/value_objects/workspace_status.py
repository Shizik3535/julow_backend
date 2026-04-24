from __future__ import annotations

from enum import Enum


class WorkspaceStatus(Enum):
    """
    Статус workspace.

    Значения:
        ACTIVE: Workspace активен
        ARCHIVED: Workspace архивирован
        SUSPENDED: Workspace приостановлен
        PENDING_DELETION: Запрос на удаление workspace
    """

    ACTIVE = "active"
    ARCHIVED = "archived"
    SUSPENDED = "suspended"
    PENDING_DELETION = "pending_deletion"
