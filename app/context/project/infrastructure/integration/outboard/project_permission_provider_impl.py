from __future__ import annotations

from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)
from app.context.project.application.ports.integration.outboard.project_permission_provider import (
    ProjectPermissionProvider,
)
from app.shared.domain.value_objects.id_vo import Id


class ProjectPermissionProviderImpl(ProjectPermissionProvider):
    """
    Реализация outboard-порта `ProjectPermissionProvider`.

    Делегирует проверку в `ProjectPermissionCheckerPort`, чтобы единый
    каскадный алгоритм (Project → Workspace → Org) использовался как
    внутри Project BC, так и при запросах из других BC.
    """

    def __init__(self, checker: ProjectPermissionCheckerPort) -> None:
        self._checker = checker

    async def has_permission(self, user_id: str, project_id: str, permission: str) -> bool:
        return await self._checker.has_permission(
            user_id=Id.from_string(user_id),
            project_id=Id.from_string(project_id),
            permission=permission,
        )
