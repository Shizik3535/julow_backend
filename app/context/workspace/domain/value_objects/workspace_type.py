from __future__ import annotations

from enum import Enum


class WorkspaceType(Enum):
    """
    Тип workspace.

    Значения:
        PERSONAL: Один пользователь, ограниченные функции
        TEAM: Стандартный набор функций
        ENTERPRISE: Полный набор + SSO + аудит
    """

    PERSONAL = "personal"
    TEAM = "team"
    ENTERPRISE = "enterprise"
