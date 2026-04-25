from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.dto.workspace_role_dto import WorkspaceRoleDTO, WorkspaceRoleListDTO
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from app.context.workspace.domain.repositories.workspace_role_repository import WorkspaceRoleRepository
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository


class GetWorkspaceRolesQuery(BaseQuery):
    """
    Запрос ролей workspace.

    Атрибуты:
        caller_id: ID пользователя, выполняющего запрос.
        workspace_id: ID workspace.
        system_only: Только системные роли.
    """

    caller_id: str
    workspace_id: str
    system_only: bool = False


class GetWorkspaceRolesHandler(BaseQueryHandler[GetWorkspaceRolesQuery, WorkspaceRoleListDTO]):
    """Обработчик запроса ролей workspace."""

    REQUIRED_PERMISSION = "roles.read"

    def __init__(
        self,
        role_repo: WorkspaceRoleRepository,
        ws_repo: WorkspaceRepository,
        permission_checker: WorkspacePermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._role_repo = role_repo
        self._ws_repo = ws_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetWorkspaceRolesQuery) -> WorkspaceRoleListDTO:
        ws_id = Id.from_string(query.workspace_id)

        ws = await self._ws_repo.get_by_id(ws_id)
        if ws is None:
            raise WorkspaceNotFoundException(query.workspace_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(query.caller_id),
            workspace_id=ws_id,
            permission=self.REQUIRED_PERMISSION,
        )
        if query.system_only:
            roles = await self._role_repo.get_system_roles()
        else:
            roles = await self._role_repo.get_by_workspace(Id.from_string(query.workspace_id))

        items = [
            WorkspaceRoleDTO(
                id=str(r.id),
                workspace_id=str(r.workspace_id) if r.workspace_id else "",
                name=r.name,
                permissions=r.permissions,
                is_system=r.is_system,
                description=r.description,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
            for r in roles
        ]
        return WorkspaceRoleListDTO(items=items, total=len(items))
