from __future__ import annotations

from abc import ABC, abstractmethod


class OrganizationMembershipPort(ABC):
    """
    Inboard-порт: проверка членства в организации (ACL).

    Project BC использует этот порт для проверки, что пользователь
    состоит в организации (например, для видимости
    ProjectVisibility.ORGANIZATION).

    Реализация — адаптер в infrastructure слое Project BC,
    делегирующий в OrganizationMembershipProvider (outboard Organization BC).
    """

    @abstractmethod
    async def is_org_member(self, org_id: str, user_id: str) -> bool:
        """Проверить, является ли пользователь членом организации."""
