from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.dto.project_role_dto import ProjectRoleDTO
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)
from app.context.project.application.queries.get_project_roles import GetProjectRolesHandler
from app.context.project.domain.exceptions.project_role_exceptions import ProjectRoleNotFoundException
from app.context.project.domain.repositories.project_role_repository import ProjectRoleRepository


class GetProjectRoleQuery(BaseQuery):
    """Запрос получения роли проекта по ID."""

    caller_id: str
    role_id: str


class GetProjectRoleHandler(BaseQueryHandler[GetProjectRoleQuery, ProjectRoleDTO]):
    """Обработчик получения роли проекта по ID."""

    REQUIRED_PERMISSION = "roles.read"

    def __init__(self, role_repo: ProjectRoleRepository, permission_checker: ProjectPermissionCheckerPort) -> None:
        super().__init__()
        self._role_repo = role_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetProjectRoleQuery) -> ProjectRoleDTO:
        role = await self._role_repo.get_by_id(Id.from_string(query.role_id))
        if role is None:
            raise ProjectRoleNotFoundException(query.role_id)
        project_id = role.project_id if role.project_id else Id.from_string(query.role_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(query.caller_id),
            project_id=project_id,
            permission=self.REQUIRED_PERMISSION,
        )
        return GetProjectRolesHandler._to_dto(role)
