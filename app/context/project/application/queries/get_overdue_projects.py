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


class GetOverdueProjectsQuery(BaseQuery):
    """Запрос просроченных проектов.

    Атрибуты:
        caller_id: ID пользователя, выполняющего запрос.
        workspace_id: ID workspace (опционально, для workspace-level запроса).
    """

    caller_id: str
    workspace_id: str | None = None


class GetOverdueProjectsHandler(BaseQueryHandler[GetOverdueProjectsQuery, ProjectListDTO]):
    """Обработчик получения просроченных проектов."""

    REQUIRED_PERMISSION = "project.read"

    def __init__(
        self,
        project_repo: ProjectRepository,
        permission_checker: ProjectPermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._project_repo = project_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetOverdueProjectsQuery) -> ProjectListDTO:
        if query.workspace_id is not None:
            projects = await self._project_repo.get_overdue_by_workspace(
                Id.from_string(query.workspace_id),
            )
            accessible = []
            for p in projects:
                if await self._permission_checker.has_permission(
                    user_id=Id.from_string(query.caller_id),
                    project_id=p.id,
                    permission=self.REQUIRED_PERMISSION,
                ):
                    accessible.append(p)
        else:
            # «Мои» просроченные проекты — где пользователь участник или владелец
            caller_uuid = Id.from_string(query.caller_id)
            member_projects = await self._project_repo.get_by_member(caller_uuid)
            member_ids = {str(p.id) for p in member_projects}
            projects = await self._project_repo.get_overdue_projects()
            accessible = [p for p in projects if str(p.id) in member_ids]

        items = [GetProjectHandler._to_dto(p) for p in accessible]
        return ProjectListDTO(items=items, total=len(items))
