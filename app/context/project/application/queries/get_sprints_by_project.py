from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.dto.sprint_dto import SprintDTO, SprintListDTO
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)
from app.context.project.domain.aggregates.sprint import Sprint
from app.context.project.domain.repositories.sprint_repository import SprintRepository


class GetSprintsByProjectQuery(BaseQuery):
    """Запрос получения всех спринтов проекта."""

    caller_id: str
    project_id: str


class GetSprintsByProjectHandler(BaseQueryHandler[GetSprintsByProjectQuery, SprintListDTO]):
    """Обработчик получения всех спринтов проекта."""

    REQUIRED_PERMISSION = "sprints.read"

    def __init__(self, sprint_repo: SprintRepository, permission_checker: ProjectPermissionCheckerPort) -> None:
        super().__init__()
        self._sprint_repo = sprint_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetSprintsByProjectQuery) -> SprintListDTO:
        project_id = Id.from_string(query.project_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(query.caller_id),
            project_id=project_id,
            permission=self.REQUIRED_PERMISSION,
        )
        sprints = await self._sprint_repo.get_by_project(project_id)
        items = [self._to_dto(s) for s in sprints]
        return SprintListDTO(items=items, total=len(items))

    @staticmethod
    def _to_dto(s: Sprint) -> SprintDTO:
        return SprintDTO(
            id=str(s.id),
            project_id=str(s.project_id),
            name=s.name,
            goal=s.goal.value if s.goal else None,
            status=s.status.value,
            date_range={"start": str(s.date_range.start), "end": str(s.date_range.end)} if s.date_range else None,
            retro={"template_name": s.retro.template_name} if s.retro else None,
            created_at=s.created_at,
            updated_at=s.updated_at,
        )
