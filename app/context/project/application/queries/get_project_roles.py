from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.dto.project_role_dto import ProjectRoleDTO, ProjectRoleListDTO
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)
from app.context.project.domain.aggregates.project_role import ProjectRole
from app.context.project.domain.repositories.project_role_repository import ProjectRoleRepository


class GetProjectRolesQuery(BaseQuery):
    """Запрос получения ролей проекта (системные + кастомные)."""

    caller_id: str
    project_id: str


class GetProjectRolesHandler(BaseQueryHandler[GetProjectRolesQuery, ProjectRoleListDTO]):
    """Обработчик получения ролей проекта."""

    REQUIRED_PERMISSION = "roles.read"

    def __init__(self, role_repo: ProjectRoleRepository, permission_checker: ProjectPermissionCheckerPort) -> None:
        super().__init__()
        self._role_repo = role_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetProjectRolesQuery) -> ProjectRoleListDTO:
        project_id = Id.from_string(query.project_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(query.caller_id),
            project_id=project_id,
            permission=self.REQUIRED_PERMISSION,
        )
        roles = await self._role_repo.get_by_project(project_id)
        items = [self._to_dto(r) for r in roles]
        return ProjectRoleListDTO(items=items, total=len(items))

    @staticmethod
    def _to_dto(r: ProjectRole) -> ProjectRoleDTO:
        return ProjectRoleDTO(
            id=str(r.id),
            project_id=str(r.project_id) if r.project_id else "",
            name=r.name,
            permissions=r.permissions,
            is_system=r.is_system,
            description=r.description,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
