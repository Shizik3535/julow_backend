from __future__ import annotations

from enum import Enum


class BoundedContextRef(Enum):
    """Ссылка на BC-источник данных для аналитики.

    Domain слой Analytics BC не импортирует другие BC; этот enum используется
    только как opaque-маркер для маршрутизации запроса на infrastructure слое
    (ACL → конкретный BC). Расширяется добавлением значения.
    """

    IDENTITY = "identity"
    PROFILE = "profile"
    ORGANIZATION = "organization"
    WORKSPACE = "workspace"
    PROJECT = "project"
    TASK = "task"
    COMMUNICATION = "communication"
    FILESTORAGE = "filestorage"
    TIMETRACKING = "timetracking"
    NOTIFICATION = "notification"
    SECURITY = "security"
    BILLING = "billing"
    ANALYTICS = "analytics"
