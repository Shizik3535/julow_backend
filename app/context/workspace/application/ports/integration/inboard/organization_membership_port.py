from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class OrganizationMembershipPort(ABC):
    """
    Inboard-порт: получение данных членства в организации из Organization BC.

    Workspace BC использует этот порт для:
    - ACL-проверок при auto_add_from_org (добавление участников из организации).
    - Проверки, что пользователь является членом организации.

    Реализация — адаптер в infrastructure, делегирующий в
    OrganizationMembershipProvider (outboard Organization BC).
    """

    @abstractmethod
    async def is_org_member(self, org_id: str, user_id: str) -> bool:
        """Проверить, является ли пользователь членом организации."""

    @abstractmethod
    async def get_org_members(self, org_id: str) -> list[dict[str, Any]]:
        """Получить список участников организации."""
