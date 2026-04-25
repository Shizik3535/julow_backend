from __future__ import annotations

from typing import Any

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.dto.project_dto import ProjectListDTO
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)
from app.context.project.application.queries.get_project import GetProjectHandler
from app.context.project.domain.repositories.project_repository import ProjectRepository


class SearchProjectsQuery(BaseQuery):
    """Запрос поиска проектов."""

    caller_id: str
    search_text: str | None = None
    workspace_id: str | None = None
    offset: int = 0
    limit: int = 500
    filters: dict[str, Any] | None = None


class SearchProjectsHandler(BaseQueryHandler[SearchProjectsQuery, ProjectListDTO]):
    """Обработчик поиска проектов."""

    REQUIRED_PERMISSION = "project.read"

    def __init__(self, project_repo: ProjectRepository, permission_checker: ProjectPermissionCheckerPort) -> None:
        super().__init__()
        self._project_repo = project_repo
        self._permission_checker = permission_checker

    async def handle(self, query: SearchProjectsQuery) -> ProjectListDTO:
        projects = await self._project_repo.search(
            search_text=query.search_text,
            workspace_id=Id.from_string(query.workspace_id) if query.workspace_id else None,
            offset=query.offset,
            limit=query.limit,
        )
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
