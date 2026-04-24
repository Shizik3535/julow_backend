from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.dto.project_dto import ProjectListDTO
from app.context.project.application.queries.get_project import GetProjectHandler
from app.context.project.domain.repositories.project_repository import ProjectRepository


class GetProjectsByWorkspaceQuery(BaseQuery):
    """Запрос получения проектов workspace."""

    workspace_id: str


class GetProjectsByWorkspaceHandler(BaseQueryHandler[GetProjectsByWorkspaceQuery, ProjectListDTO]):
    """Обработчик получения проектов workspace."""

    def __init__(self, project_repo: ProjectRepository) -> None:
        super().__init__()
        self._project_repo = project_repo

    async def handle(self, query: GetProjectsByWorkspaceQuery) -> ProjectListDTO:
        projects = await self._project_repo.get_by_workspace(Id.from_string(query.workspace_id))
        items = [GetProjectHandler._to_dto(p) for p in projects]
        return ProjectListDTO(items=items, total=len(items))
