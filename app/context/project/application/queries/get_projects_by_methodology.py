from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.context.project.application.dto.project_dto import ProjectListDTO
from app.context.project.application.queries.get_project import GetProjectHandler
from app.context.project.domain.repositories.project_repository import ProjectRepository
from app.context.project.domain.value_objects.methodology import Methodology


class GetProjectsByMethodologyQuery(BaseQuery):
    """Запрос получения проектов по методологии."""

    methodology: str


class GetProjectsByMethodologyHandler(BaseQueryHandler[GetProjectsByMethodologyQuery, ProjectListDTO]):
    """Обработчик получения проектов по методологии."""

    def __init__(self, project_repo: ProjectRepository) -> None:
        super().__init__()
        self._project_repo = project_repo

    async def handle(self, query: GetProjectsByMethodologyQuery) -> ProjectListDTO:
        methodology = Methodology(query.methodology)
        projects = await self._project_repo.get_by_methodology(methodology.value)
        items = [GetProjectHandler._to_dto(p) for p in projects]
        return ProjectListDTO(items=items, total=len(items))
