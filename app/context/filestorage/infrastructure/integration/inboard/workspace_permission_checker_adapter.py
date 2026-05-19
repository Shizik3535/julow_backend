from __future__ import annotations

from typing import Awaitable, Callable

from app.context.filestorage.application.exceptions.authorization_exceptions import (
    InsufficientFileStoragePermissionsException,
)
from app.context.filestorage.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.application.ports.integration.outboard.workspace_membership_provider import (
    WorkspaceMembershipProvider,
)

# Разрешения, которые каскадируются на уровень проекта:
# если пользователь — участник проекта в workspace, он может читать файлы.
_PROJECT_CASCADE_PERMISSIONS = {"files.read", "storage.read"}

# Callback: (user_id, workspace_id) → bool
ProjectMembershipChecker = Callable[[str, str], Awaitable[bool]]


class WorkspacePermissionCheckerAdapter(WorkspacePermissionCheckerPort):
    """
    Реализация WorkspacePermissionCheckerPort для FileStorage BC.

    Делегирует в WorkspaceMembershipProvider (outboard Workspace BC),
    который инкапсулирует каскад workspace-роль → орг-роль.

    Для read-разрешений (``files.read``, ``storage.read``) каскадирует
    на уровень проекта: если пользователь — участник любого проекта
    в workspace, разрешение выдаётся.
    """

    def __init__(
        self,
        workspace_membership_provider: WorkspaceMembershipProvider,
        project_membership_checker: ProjectMembershipChecker | None = None,
    ) -> None:
        self._provider = workspace_membership_provider
        self._project_check = project_membership_checker

    async def has_permission(
        self, user_id: str, workspace_id: str, permission: str
    ) -> bool:
        if await self._provider.has_permission(
            workspace_id=workspace_id,
            user_id=user_id,
            permission=permission,
        ):
            return True

        # Каскад: project-membership даёт read-доступ к файлам workspace
        if (
            permission in _PROJECT_CASCADE_PERMISSIONS
            and self._project_check is not None
            and await self._project_check(user_id, workspace_id)
        ):
            return True

        return False

    async def require_permission(
        self, user_id: str, workspace_id: str, permission: str
    ) -> None:
        if not await self.has_permission(
            user_id=user_id, workspace_id=workspace_id, permission=permission
        ):
            raise InsufficientFileStoragePermissionsException(
                permission=permission, workspace_id=workspace_id
            )
