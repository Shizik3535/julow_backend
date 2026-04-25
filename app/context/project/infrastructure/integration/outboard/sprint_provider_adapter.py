from __future__ import annotations

from app.context.project.application.dto.sprint_dto import SprintDTO
from app.context.project.application.ports.integration.outboard.sprint_provider import (
    SprintProvider,
)
from app.context.project.domain.repositories.sprint_repository import SprintRepository
from app.shared.domain.value_objects.id_vo import Id


class SprintProviderAdapter(SprintProvider):
    """
    Реализация outboard-порта SprintProvider.

    Делегирует в SprintRepository для предоставления данных спринтов другим BC.
    """

    def __init__(self, repo: SprintRepository) -> None:
        self._repo = repo

    async def sprint_exists(self, sprint_id: str) -> bool:
        sprint = await self._repo.get_by_id(Id.from_string(sprint_id))
        return sprint is not None

    async def get_sprint(self, sprint_id: str) -> SprintDTO | None:
        sprint = await self._repo.get_by_id(Id.from_string(sprint_id))
        if sprint is None:
            return None
        return self._to_dto(sprint)

    async def get_active_sprint(self, project_id: str) -> SprintDTO | None:
        sprints = await self._repo.get_active_by_project(Id.from_string(project_id))
        if not sprints:
            return None
        return self._to_dto(sprints[0])

    async def get_sprints_by_project(self, project_id: str) -> list[SprintDTO]:
        sprints = await self._repo.get_by_project(Id.from_string(project_id))
        return [self._to_dto(s) for s in sprints]

    @staticmethod
    def _to_dto(sprint) -> SprintDTO:
        date_range = None
        if sprint.date_range is not None:
            date_range = {
                "start": str(sprint.date_range.start),
                "end": str(sprint.date_range.end),
            }

        retro = None
        if sprint.retro is not None:
            retro = {
                "template_name": sprint.retro.template_name,
            }

        return SprintDTO(
            id=str(sprint.id),
            project_id=str(sprint.project_id),
            name=sprint.name,
            goal=sprint.goal.value if sprint.goal else None,
            status=sprint.status.value,
            date_range=date_range,
            retro=retro,
            created_at=sprint.created_at,
            updated_at=sprint.updated_at,
        )
