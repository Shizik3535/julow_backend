"""Запрос предстоящих совещаний пользователя."""

from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.communication.application.dto.mappers import meeting_to_dto
from app.context.communication.application.dto.meeting_dto import MeetingListDTO
from app.context.communication.domain.repositories.meeting_repository import (
    MeetingRepository,
)


class GetMyMeetingsQuery(BaseQuery):
    """Запрос моих предстоящих совещаний."""

    caller_id: str


class GetMyMeetingsHandler(BaseQueryHandler[GetMyMeetingsQuery, MeetingListDTO]):
    def __init__(self, meeting_repo: MeetingRepository) -> None:
        super().__init__()
        self._repo = meeting_repo

    async def handle(self, query: GetMyMeetingsQuery) -> MeetingListDTO:
        meetings = await self._repo.get_upcoming_by_participant(
            Id.from_string(query.caller_id)
        )
        items = [meeting_to_dto(m) for m in meetings]
        return MeetingListDTO(items=items, total=len(items))
