from __future__ import annotations

from abc import ABC, abstractmethod


class OrganizationMembershipPort(ABC):
    """
    Inboard-порт: проверка членства в организации.

    Profile BC использует этот порт для ACL-проверки при установке
    ProfileVisibility.ORGANIZATION_ONLY — пользователь должен состоять
    в организации.

    Реализация — адаптер в infrastructure-слое Profile BC,
    который делегирует в соответствующий provider из Identity/Workspace BC.
    """

    @abstractmethod
    async def is_member(self, user_id: str, organization_id: str) -> bool:
        """
        Проверить, состоит ли пользователь в организации.

        Аргументы:
            user_id: Идентификатор пользователя (UUID строка).
            organization_id: Идентификатор организации.

        Возвращает:
            True, если пользователь состоит в организации.
        """

    @abstractmethod
    async def share_organization(self, user_id_a: str, user_id_b: str) -> bool:
        """
        Проверить, состоят ли два пользователя в одной организации.

        Используется для ACL-проверки при ProfileVisibility.ORGANIZATION_ONLY.

        Аргументы:
            user_id_a: Идентификатор первого пользователя.
            user_id_b: Идентификатор второго пользователя.

        Возвращает:
            True, если пользователи имеют как минимум одно общее активное членство.
        """
