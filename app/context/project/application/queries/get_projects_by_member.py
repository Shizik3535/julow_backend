from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.dto.project_dto import ProjectListDTO
from app.context.project.application.queries.get_project import GetProjectHandler
from app.context.project.domain.repositories.project_repository import ProjectRepository


class GetProjectsByMemberQuery(BaseQuery):
    """Запрос получения проектов, где пользователь — участник."""

    user_id: str


class GetProjectsByMemberHandler(BaseQueryHandler[GetProjectsByMemberQuery, ProjectListDTO]):
    """Обработчик получения проектов пользователя."""

    def __init__(self, project_repo: ProjectRepository) -> None:
        super().__init__()
        self._project_repo = project_repo

    async def handle(self, query: GetProjectsByMemberQuery) -> ProjectListDTO:
        projects = await self._project_repo.get_by_member(Id.from_string(query.user_id))
        items = [GetProjectHandler._to_dto(p) for p in projects]
        return ProjectListDTO(items=items, total=len(items))
