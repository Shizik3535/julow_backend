from __future__ import annotations

from abc import ABC, abstractmethod


class OrganizationPermissionCheckerPort(ABC):
    """
    Inboard-порт: проверка разрешений пользователя в организации.

    Workspace BC использует этот порт для:
    - ACL-проверки при создании workspace, привязанного к организации.
    - Каскадной проверки орг-роли при запросе workspace-разрешения
      (см. WorkspaceRoleBasedPermissionChecker).
    - Проверки при получении списка workspace организации.

    Реализация — адаптер в infrastructure слое Workspace BC,
    делегирующий в OrganizationPermissionProvider (outboard Organization BC).
    """

    @abstractmethod
    async def has_permission(self, user_id: str, org_id: str, permission: str) -> bool:
        """
        Проверить, есть ли у пользователя разрешение в организации.

        Аргументы:
            user_id: Идентификатор пользователя.
            org_id: Идентификатор организации.
            permission: Требуемое разрешение (например «workspaces.members.read»).

        Возвращает:
            True, если разрешение есть, иначе False.
        """
