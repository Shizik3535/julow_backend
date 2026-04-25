from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.dto.sprint_dto import SprintDTO
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)
from app.context.project.application.queries.get_sprints_by_project import GetSprintsByProjectHandler
from app.context.project.domain.exceptions.sprint_exceptions import SprintNotFoundException
from app.context.project.domain.repositories.sprint_repository import SprintRepository


class GetSprintQuery(BaseQuery):
    """Запрос получения спринта по ID."""

    caller_id: str
    sprint_id: str


class GetSprintHandler(BaseQueryHandler[GetSprintQuery, SprintDTO]):
    """Обработчик получения спринта по ID."""

    REQUIRED_PERMISSION = "sprints.read"

    def __init__(self, sprint_repo: SprintRepository, permission_checker: ProjectPermissionCheckerPort) -> None:
        super().__init__()
        self._sprint_repo = sprint_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetSprintQuery) -> SprintDTO:
        sprint = await self._sprint_repo.get_by_id(Id.from_string(query.sprint_id))
        if sprint is None:
            raise SprintNotFoundException(query.sprint_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(query.caller_id),
            project_id=sprint.project_id,
            permission=self.REQUIRED_PERMISSION,
        )
        return GetSprintsByProjectHandler._to_dto(sprint)
