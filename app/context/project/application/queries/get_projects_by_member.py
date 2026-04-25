from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.dto.project_dto import ProjectListDTO
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)
from app.context.project.application.queries.get_project import GetProjectHandler
from app.context.project.domain.repositories.project_repository import ProjectRepository


class GetProjectsByMemberQuery(BaseQuery):
    """Запрос получения проектов, где пользователь — участник."""

    caller_id: str
    user_id: str


class GetProjectsByMemberHandler(BaseQueryHandler[GetProjectsByMemberQuery, ProjectListDTO]):
    """Обработчик получения проектов пользователя."""

    REQUIRED_PERMISSION = "project.read"

    def __init__(self, project_repo: ProjectRepository, permission_checker: ProjectPermissionCheckerPort) -> None:
        super().__init__()
        self._project_repo = project_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetProjectsByMemberQuery) -> ProjectListDTO:
        projects = await self._project_repo.get_by_member(Id.from_string(query.user_id))
        accessible = []
        for p in projects:
            if await self._permission_checker.has_permission(
                user_id=Id.from_string(query.caller_id),
                project_id=p.id,
                permission=self.REQUIRED_PERMISSION,
            ):
                accessible.append(p)
        items = [GetProjectHandler._to_dto(p) for p in accessible]
        return ProjectListDTO(items=items, total=len(items))
