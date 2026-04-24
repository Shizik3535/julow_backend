from __future__ import annotations

from app.context.project.application.ports.integration.outboard.project_permission_provider import (
    ProjectPermissionProvider,
)
from app.context.task.application.exceptions.authorization_exceptions import (
    InsufficientTaskPermissionsException,
)
from app.context.task.application.ports.authorization.task_permission_checker_port import (
    TaskPermissionCheckerPort,
)


class TaskPermissionCheckerAdapter(TaskPermissionCheckerPort):
    """
    Реализация `TaskPermissionCheckerPort` для Task BC.

    Делегирует проверку разрешений в outboard-порт Project BC
    (`ProjectPermissionProvider`), который инкапсулирует каскад
    ProjectRole → WorkspaceRole → OrgRole.

    Task BC не владеет собственным пространством ролей: `tasks.<action>`
    — это permission-группа, настраиваемая в системных ролях Project/Workspace/Org
    (см. `SYSTEM_PROJECT_ROLES`, `SYSTEM_WORKSPACE_ROLES`, `SYSTEM_ORG_ROLES`).
    """

    def __init__(self, project_permission_provider: ProjectPermissionProvider) -> None:
        self._provider = project_permission_provider

    async def has_permission(self, user_id: str, project_id: str, permission: str) -> bool:
        return await self._provider.has_permission(
            user_id=user_id,
            project_id=project_id,
            permission=permission,
        )

    async def require_permission(self, user_id: str, project_id: str, permission: str) -> None:
        if not await self.has_permission(user_id=user_id, project_id=project_id, permission=permission):
            raise InsufficientTaskPermissionsException(
                permission=permission,
                project_id=project_id,
                user_id=user_id,
            )
