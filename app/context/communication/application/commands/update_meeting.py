"""Команда обновления совещания."""

from __future__ import annotations

from datetime import datetime

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.agenda_item import AgendaItem
from app.shared.domain.value_objects.agenda_vo import Agenda
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.rich_text_format import RichTextFormat
from app.shared.domain.value_objects.rich_text_vo import RichText
from app.shared.domain.value_objects.url_vo import Url

from app.context.communication.application.dto.mappers import meeting_to_dto
from app.context.communication.application.dto.meeting_dto import MeetingDTO
from app.context.communication.application.exceptions.authorization_exceptions import (
    NotMeetingOrganizerException,
)
from app.context.communication.domain.exceptions.meeting_exceptions import (
    MeetingNotFoundException,
)
from app.context.communication.domain.repositories.meeting_repository import (
    MeetingRepository,
)


class UpdateMeetingCommand(BaseCommand):
    """Обновить совещание (только организатор)."""

    caller_id: str
    meeting_id: str
    title: str | None = None
    scheduled_at: datetime | None = None
    duration_minutes: int | None = None
    description: str | None = None
    description_format: str = "markdown"
    location: str | None = None
    conference_url: str | None = None
    agenda: list[str] | None = None


class UpdateMeetingHandler(BaseCommandHandler[UpdateMeetingCommand, MeetingDTO]):
    def __init__(
        self,
        meeting_repo: MeetingRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = meeting_repo
        self._event_bus = event_bus

    async def handle(self, command: UpdateMeetingCommand) -> MeetingDTO:
        meeting = await self._repo.get_by_id(Id.from_string(command.meeting_id))
        if meeting is None:
            raise MeetingNotFoundException(command.meeting_id)
        if str(meeting.organizer_id) != command.caller_id:
            raise NotMeetingOrganizerException()

        description = None
        if command.description is not None:
            description = RichText(
                content=command.description,
                format=RichTextFormat(command.description_format),
            )
        agenda = None
        if command.agenda is not None:
            agenda = Agenda(items=[AgendaItem(text=t) for t in command.agenda])
        conference_url = None
        if command.conference_url is not None:
            conference_url = Url(value=command.conference_url)

        meeting.update(
            title=command.title,
            agenda=agenda,
            scheduled_at=command.scheduled_at,
            duration_minutes=command.duration_minutes,
            description=description,
            location=command.location,
            conference_url=conference_url,
        )
        await self._repo.update(meeting)
        await self._event_bus.publish_all(meeting.clear_domain_events())
        return meeting_to_dto(meeting)
