from __future__ import annotations

from abc import ABC, abstractmethod


class WorkspacePermissionCheckerPort(ABC):
    """
    Inboard-порт: проверка разрешений пользователя в workspace.

    FileStorage BC использует этот порт для авторизации операций
    над файлами, папками и хранилищем (`files.read`, `files.write`,
    `files.share`, `files.admin`, `storage.admin` и т.п.).

    Реализация — адаптер в infrastructure-слое FileStorage BC,
    делегирующий в WorkspaceMembershipProvider.has_permission
    (outboard Workspace BC), который инкапсулирует каскад
    workspace-роль → орг-роль.
    """

    @abstractmethod
    async def has_permission(self, user_id: str, workspace_id: str, permission: str) -> bool:
        """Проверить наличие разрешения."""

    @abstractmethod
    async def require_permission(self, user_id: str, workspace_id: str, permission: str) -> None:
        """
        Проверить разрешение; выбросить
        ``InsufficientFileStoragePermissionsException`` при отсутствии.
        """
