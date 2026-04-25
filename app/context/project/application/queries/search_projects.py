from __future__ import annotations

from typing import Any

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.dto.project_dto import ProjectListDTO
from app.context.project.application.queries.get_project import GetProjectHandler
from app.context.project.domain.repositories.project_repository import ProjectRepository


class SearchProjectsQuery(BaseQuery):
    """Запрос поиска проектов."""

    offset: int = 0
    limit: int = 100
    filters: dict[str, Any] | None = None


class SearchProjectsHandler(BaseQueryHandler[SearchProjectsQuery, ProjectListDTO]):
    """Обработчик поиска проектов."""

    def __init__(self, project_repo: ProjectRepository) -> None:
        super().__init__()
        self._project_repo = project_repo

    async def handle(self, query: SearchProjectsQuery) -> ProjectListDTO:
        filters = query.filters or {}
        search_text = filters.get("query", "")
        workspace_id_str = filters.get("workspace_id")
        ws_id = Id.from_string(workspace_id_str) if workspace_id_str else None

        projects = await self._project_repo.search(
            query=search_text,
            workspace_id=ws_id,
        )
        # Apply offset/limit
        total = len(projects)
        items = [GetProjectHandler._to_dto(p) for p in projects[query.offset : query.offset + query.limit]]
        return ProjectListDTO(items=items, total=total)
