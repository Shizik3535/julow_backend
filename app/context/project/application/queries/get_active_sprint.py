from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.dto.sprint_dto import SprintDTO
from app.context.project.application.queries.get_sprints_by_project import GetSprintsByProjectHandler
from app.context.project.domain.exceptions.sprint_exceptions import SprintNotFoundException
from app.context.project.domain.repositories.sprint_repository import SprintRepository


class GetActiveSprintQuery(BaseQuery):
    """Запрос получения активного спринта проекта."""

    project_id: str


class GetActiveSprintHandler(BaseQueryHandler[GetActiveSprintQuery, SprintDTO]):
    """Обработчик получения активного спринта."""

    def __init__(self, sprint_repo: SprintRepository) -> None:
        super().__init__()
        self._sprint_repo = sprint_repo

    async def handle(self, query: GetActiveSprintQuery) -> SprintDTO:
        sprints = await self._sprint_repo.get_active_by_project(Id.from_string(query.project_id))
        if not sprints:
            raise SprintNotFoundException(f"active sprint for project {query.project_id}")
        return GetSprintsByProjectHandler._to_dto(sprints[0])
