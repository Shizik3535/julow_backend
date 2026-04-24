from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.dto.project_role_dto import ProjectRoleDTO
from app.context.project.application.queries.get_project_roles import GetProjectRolesHandler
from app.context.project.domain.exceptions.project_role_exceptions import ProjectRoleNotFoundException
from app.context.project.domain.repositories.project_role_repository import ProjectRoleRepository


class GetProjectRoleQuery(BaseQuery):
    """Запрос получения роли проекта по ID."""

    role_id: str


class GetProjectRoleHandler(BaseQueryHandler[GetProjectRoleQuery, ProjectRoleDTO]):
    """Обработчик получения роли проекта по ID."""

    def __init__(self, role_repo: ProjectRoleRepository) -> None:
        super().__init__()
        self._role_repo = role_repo

    async def handle(self, query: GetProjectRoleQuery) -> ProjectRoleDTO:
        role = await self._role_repo.get_by_id(Id.from_string(query.role_id))
        if role is None:
            raise ProjectRoleNotFoundException(query.role_id)
        return GetProjectRolesHandler._to_dto(role)
