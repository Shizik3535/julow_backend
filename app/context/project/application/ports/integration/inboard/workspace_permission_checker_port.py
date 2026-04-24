from __future__ import annotations

from abc import ABC, abstractmethod


class WorkspacePermissionCheckerPort(ABC):
    """
    Inboard-порт: проверка разрешений пользователя в workspace.

    Project BC использует этот порт для:
    - ACL-проверки при создании проекта в workspace (через `projects.create`).
    - Каскадной проверки workspace-роли при запросе project-разрешения
      (см. ProjectRoleBasedPermissionChecker).
    - Проверок на уровне списков проектов workspace.

    Реализация — адаптер в infrastructure слое Project BC,
    делегирующий в WorkspaceMembershipProvider.has_permission
    (outboard Workspace BC), который, в свою очередь, каскадирует
    в орг-роль при необходимости.
    """

    @abstractmethod
    async def has_permission(self, user_id: str, workspace_id: str, permission: str) -> bool:
        """
        Проверить, есть ли у пользователя разрешение в workspace.

        Аргументы:
            user_id: Идентификатор пользователя.
            workspace_id: Идентификатор workspace.
            permission: Требуемое разрешение (например «projects.create»).

        Возвращает:
            True, если разрешение есть, иначе False.
        """

    @abstractmethod
    async def require_permission(self, user_id: str, workspace_id: str, permission: str) -> None:
        """
        Проверить разрешение; выбросить исключение при отсутствии.

        Аргументы:
            user_id: Идентификатор пользователя.
            workspace_id: Идентификатор workspace.
            permission: Требуемое разрешение.

        Выбрасывает:
            InsufficientWorkspacePermissionsException — если разрешения нет.
        """
