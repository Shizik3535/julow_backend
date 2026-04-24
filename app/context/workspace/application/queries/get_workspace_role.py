from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.dto.workspace_role_dto import WorkspaceRoleDTO
from app.context.workspace.application.exceptions.authorization_exceptions import (
    InsufficientWorkspacePermissionsException,
)
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.domain.exceptions.workspace_role_exceptions import WorkspaceRoleNotFoundException
from app.context.workspace.domain.repositories.workspace_role_repository import WorkspaceRoleRepository


class GetWorkspaceRoleQuery(BaseQuery):
    """
    Запрос роли workspace по ID.

    Атрибуты:
        caller_id: ID пользователя, выполняющего запрос.
        role_id: ID роли.
    """

    caller_id: str
    role_id: str


class GetWorkspaceRoleHandler(BaseQueryHandler[GetWorkspaceRoleQuery, WorkspaceRoleDTO]):
    """Обработчик запроса роли workspace по ID."""

    REQUIRED_PERMISSION = "roles.read"

    def __init__(
        self,
        role_repo: WorkspaceRoleRepository,
        permission_checker: WorkspacePermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._role_repo = role_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetWorkspaceRoleQuery) -> WorkspaceRoleDTO:
        role = await self._role_repo.get_by_id(Id.from_string(query.role_id))
        if role is None:
            raise WorkspaceRoleNotFoundException(query.role_id)

        # Системные роли читаемы любым аутентифицированным пользователем; для кастомных
        # требуем разрешение `roles.read` в владельце workspace.
        if role.workspace_id is not None:
            await self._permission_checker.require_permission(
                user_id=Id.from_string(query.caller_id),
                workspace_id=role.workspace_id,
                permission=self.REQUIRED_PERMISSION,
            )

        return WorkspaceRoleDTO(
            id=str(role.id),
            workspace_id=str(role.workspace_id) if role.workspace_id else "",
            name=role.name,
            permissions=role.permissions,
            is_system=role.is_system,
            description=role.description,
            created_at=role.created_at,
            updated_at=role.updated_at,
        )
