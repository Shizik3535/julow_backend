from __future__ import annotations

from abc import ABC, abstractmethod


class OrganizationPermissionProvider(ABC):
    """
    Outboard-порт: предоставляет проверку орг-разрешений другим BC.

    Другие BC (Workspace, Profile, ...) инжектируют этот порт через DI
    для проверки, обладает ли пользователь указанным разрешением в
    организации. Логика wildcard-матчинга («org.*», «workspaces.*»,
    «members.*») инкапсулирована внутри Organization BC.

    Реализация находится в infrastructure-слое Organization BC.
    """

    @abstractmethod
    async def has_permission(self, user_id: str, org_id: str, permission: str) -> bool:
        """
        Проверяет, есть ли у пользователя указанное разрешение в организации.

        Аргументы:
            user_id: Идентификатор пользователя.
            org_id: Идентификатор организации.
            permission: Требуемое разрешение (например «workspaces.members.read»).

        Возвращает:
            True, если разрешение есть, иначе False.
        """
