from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.dto.epic_dto import EpicDTO, EpicListDTO
from app.context.project.domain.aggregates.epic import Epic
from app.context.project.domain.repositories.epic_repository import EpicRepository


class GetEpicsByProjectQuery(BaseQuery):
    """Запрос получения эпиков проекта."""

    project_id: str


class GetEpicsByProjectHandler(BaseQueryHandler[GetEpicsByProjectQuery, EpicListDTO]):
    """Обработчик получения эпиков проекта."""

    def __init__(self, epic_repo: EpicRepository) -> None:
        super().__init__()
        self._epic_repo = epic_repo

    async def handle(self, query: GetEpicsByProjectQuery) -> EpicListDTO:
        epics = await self._epic_repo.get_by_project(Id.from_string(query.project_id))
        items = [self._to_dto(e) for e in epics]
        return EpicListDTO(items=items, total=len(items))

    @staticmethod
    def _to_dto(e: Epic) -> EpicDTO:
        return EpicDTO(
            id=str(e.id),
            project_id=str(e.project_id),
            name=e.name,
            description={"content": e.description.content, "format": e.description.format.value} if e.description else None,
            status=e.status.value,
            start_date=str(e.start_date) if e.start_date else None,
            due_date=str(e.due_date) if e.due_date else None,
            owner_id=str(e.owner_id) if e.owner_id else None,
            color=str(e.color) if e.color else None,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )
