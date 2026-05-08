"""Команды управления участниками совещания: add/remove + RSVP."""

from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.communication.application.exceptions.authorization_exceptions import (
    NotMeetingOrganizerException,
)
from app.context.communication.domain.exceptions.meeting_exceptions import (
    MeetingNotFoundException,
)
from app.context.communication.domain.repositories.meeting_repository import (
    MeetingRepository,
)
from app.context.communication.domain.value_objects.rsvp_status import RSVPStatus


def _require_organizer(meeting, caller_id: str) -> None:
    if str(meeting.organizer_id) != caller_id:
        raise NotMeetingOrganizerException()


class AddMeetingParticipantCommand(BaseCommand):
    caller_id: str
    meeting_id: str
    user_id: str
    is_mandatory: bool = True


class AddMeetingParticipantHandler(
    BaseCommandHandler[AddMeetingParticipantCommand, None]
):
    def __init__(
        self,
        meeting_repo: MeetingRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = meeting_repo
        self._event_bus = event_bus

    async def handle(self, command: AddMeetingParticipantCommand) -> None:
        meeting = await self._repo.get_by_id(Id.from_string(command.meeting_id))
        if meeting is None:
            raise MeetingNotFoundException(command.meeting_id)
        _require_organizer(meeting, command.caller_id)
        meeting.add_participant(
            user_id=Id.from_string(command.user_id),
            is_mandatory=command.is_mandatory,
        )
        await self._repo.update(meeting)
        await self._event_bus.publish_all(meeting.clear_domain_events())


class RemoveMeetingParticipantCommand(BaseCommand):
    caller_id: str
    meeting_id: str
    user_id: str


class RemoveMeetingParticipantHandler(
    BaseCommandHandler[RemoveMeetingParticipantCommand, None]
):
    def __init__(
        self,
        meeting_repo: MeetingRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = meeting_repo
        self._event_bus = event_bus

    async def handle(self, command: RemoveMeetingParticipantCommand) -> None:
        meeting = await self._repo.get_by_id(Id.from_string(command.meeting_id))
        if meeting is None:
            raise MeetingNotFoundException(command.meeting_id)
        _require_organizer(meeting, command.caller_id)
        meeting.remove_participant(Id.from_string(command.user_id))
        await self._repo.update(meeting)
        await self._event_bus.publish_all(meeting.clear_domain_events())


class UpdateRSVPCommand(BaseCommand):
    """Обновить свой RSVP-статус (только сам участник)."""

    caller_id: str
    meeting_id: str
    rsvp_status: str


class UpdateRSVPHandler(BaseCommandHandler[UpdateRSVPCommand, None]):
    def __init__(
        self,
        meeting_repo: MeetingRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = meeting_repo
        self._event_bus = event_bus

    async def handle(self, command: UpdateRSVPCommand) -> None:
        meeting = await self._repo.get_by_id(Id.from_string(command.meeting_id))
        if meeting is None:
            raise MeetingNotFoundException(command.meeting_id)
        meeting.update_rsvp(
            user_id=Id.from_string(command.caller_id),
            rsvp_status=RSVPStatus(command.rsvp_status),
        )
        await self._repo.update(meeting)
        await self._event_bus.publish_all(meeting.clear_domain_events())
