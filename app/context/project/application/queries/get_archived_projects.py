from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.dto.project_dto import ProjectListDTO
from app.context.project.application.queries.get_project import GetProjectHandler
from app.context.project.domain.repositories.project_repository import ProjectRepository


class GetArchivedProjectsQuery(BaseQuery):
    """Запрос получения архивированных проектов workspace."""

    workspace_id: str


class GetArchivedProjectsHandler(BaseQueryHandler[GetArchivedProjectsQuery, ProjectListDTO]):
    """Обработчик получения архивированных проектов."""

    def __init__(self, project_repo: ProjectRepository) -> None:
        super().__init__()
        self._project_repo = project_repo

    async def handle(self, query: GetArchivedProjectsQuery) -> ProjectListDTO:
        projects = await self._project_repo.get_archived_by_workspace(Id.from_string(query.workspace_id))
        items = [GetProjectHandler._to_dto(p) for p in projects]
        return ProjectListDTO(items=items, total=len(items))
