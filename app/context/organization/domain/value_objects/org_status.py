from __future__ import annotations

from enum import Enum


class OrgStatus(Enum):
    """
    Статус организации.

    Значения:
        ACTIVE: Организация активна
        SUSPENDED: Организация приостановлена
        PENDING_DELETION: Запрос на удаление организации
    """

    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING_DELETION = "pending_deletion"
