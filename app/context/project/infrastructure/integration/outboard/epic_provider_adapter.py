from __future__ import annotations

from app.context.project.application.dto.epic_dto import EpicDTO
from app.context.project.application.ports.integration.outboard.epic_provider import (
    EpicProvider,
)
from app.context.project.domain.repositories.epic_repository import EpicRepository
from app.shared.domain.value_objects.id_vo import Id


class EpicProviderAdapter(EpicProvider):
    """
    Реализация outboard-порта EpicProvider.

    Делегирует в EpicRepository для предоставления данных эпиков другим BC.
    """

    def __init__(self, repo: EpicRepository) -> None:
        self._repo = repo

    async def epic_exists(self, epic_id: str) -> bool:
        epic = await self._repo.get_by_id(Id.from_string(epic_id))
        return epic is not None

    async def get_epic(self, epic_id: str) -> EpicDTO | None:
        epic = await self._repo.get_by_id(Id.from_string(epic_id))
        if epic is None:
            return None
        return self._to_dto(epic)

    async def get_epics_by_project(self, project_id: str) -> list[EpicDTO]:
        epics = await self._repo.get_by_project(Id.from_string(project_id))
        return [self._to_dto(e) for e in epics]

    @staticmethod
    def _to_dto(epic) -> EpicDTO:
        description = None
        if epic.description is not None:
            description = {
                "content": epic.description.content,
                "format": epic.description.format.value,
            }

        return EpicDTO(
            id=str(epic.id),
            project_id=str(epic.project_id),
            name=epic.name,
            description=description,
            status=epic.status.value,
            start_date=str(epic.start_date) if epic.start_date else None,
            due_date=str(epic.due_date) if epic.due_date else None,
            owner_id=str(epic.owner_id) if epic.owner_id else None,
            color=str(epic.color) if epic.color else None,
            created_at=epic.created_at,
            updated_at=epic.updated_at,
        )
