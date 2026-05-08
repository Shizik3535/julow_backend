"""Запрос совещания по ID."""

from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.communication.application.dto.mappers import meeting_to_dto
from app.context.communication.application.dto.meeting_dto import MeetingDTO
from app.context.communication.application.exceptions.authorization_exceptions import (
    NotMeetingParticipantException,
)
from app.context.communication.domain.exceptions.meeting_exceptions import (
    MeetingNotFoundException,
)
from app.context.communication.domain.repositories.meeting_repository import (
    MeetingRepository,
)


class GetMeetingQuery(BaseQuery):
    """Запрос совещания (только участник)."""

    meeting_id: str
    caller_id: str


class GetMeetingHandler(BaseQueryHandler[GetMeetingQuery, MeetingDTO]):
    def __init__(self, meeting_repo: MeetingRepository) -> None:
        super().__init__()
        self._repo = meeting_repo

    async def handle(self, query: GetMeetingQuery) -> MeetingDTO:
        meeting = await self._repo.get_by_id(Id.from_string(query.meeting_id))
        if meeting is None:
            raise MeetingNotFoundException(query.meeting_id)
        if not meeting.is_participant(Id.from_string(query.caller_id)):
            raise NotMeetingParticipantException()
        return meeting_to_dto(meeting)
