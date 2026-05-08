"""Запрос совещаний в workspace/project."""

from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.communication.application.dto.mappers import meeting_to_dto
from app.context.communication.application.dto.meeting_dto import MeetingListDTO
from app.context.communication.domain.repositories.meeting_repository import (
    MeetingRepository,
)


class GetMeetingsByWorkspaceQuery(BaseQuery):
    workspace_id: str
    caller_id: str


class GetMeetingsByWorkspaceHandler(
    BaseQueryHandler[GetMeetingsByWorkspaceQuery, MeetingListDTO]
):
    """Возвращает все совещания workspace, видимые caller_id (как участнику).

    Для MVP: каждый участник видит только совещания, где он в списке.
    """

    def __init__(self, meeting_repo: MeetingRepository) -> None:
        super().__init__()
        self._repo = meeting_repo

    async def handle(
        self, query: GetMeetingsByWorkspaceQuery
    ) -> MeetingListDTO:
        meetings = await self._repo.get_by_workspace(
            Id.from_string(query.workspace_id)
        )
        meetings = [
            m for m in meetings if m.is_participant(Id.from_string(query.caller_id))
        ]
        items = [meeting_to_dto(m) for m in meetings]
        return MeetingListDTO(items=items, total=len(items))


class GetMeetingsByProjectQuery(BaseQuery):
    project_id: str
    caller_id: str


class GetMeetingsByProjectHandler(
    BaseQueryHandler[GetMeetingsByProjectQuery, MeetingListDTO]
):
    def __init__(self, meeting_repo: MeetingRepository) -> None:
        super().__init__()
        self._repo = meeting_repo

    async def handle(self, query: GetMeetingsByProjectQuery) -> MeetingListDTO:
        meetings = await self._repo.get_by_project(Id.from_string(query.project_id))
        meetings = [
            m for m in meetings if m.is_participant(Id.from_string(query.caller_id))
        ]
        items = [meeting_to_dto(m) for m in meetings]
        return MeetingListDTO(items=items, total=len(items))
