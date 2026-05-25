"""Команды жизненного цикла совещания: cancel/start/complete."""

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
from app.context.communication.infrastructure.integration.inboard.conference_provider_registry import (
    ConferenceProviderRegistry,
)


def _require_organizer(meeting, caller_id: str) -> None:
    if str(meeting.organizer_id) != caller_id:
        raise NotMeetingOrganizerException()


class StartMeetingCommand(BaseCommand):
    caller_id: str
    meeting_id: str


class StartMeetingHandler(BaseCommandHandler[StartMeetingCommand, None]):
    def __init__(
        self,
        meeting_repo: MeetingRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = meeting_repo
        self._event_bus = event_bus

    async def handle(self, command: StartMeetingCommand) -> None:
        meeting = await self._repo.get_by_id(Id.from_string(command.meeting_id))
        if meeting is None:
            raise MeetingNotFoundException(command.meeting_id)
        _require_organizer(meeting, command.caller_id)
        meeting.start()
        await self._repo.update(meeting)
        await self._event_bus.publish_all(meeting.clear_domain_events())


class CompleteMeetingCommand(BaseCommand):
    caller_id: str
    meeting_id: str


class CompleteMeetingHandler(BaseCommandHandler[CompleteMeetingCommand, None]):
    def __init__(
        self,
        meeting_repo: MeetingRepository,
        provider_registry: ConferenceProviderRegistry,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = meeting_repo
        self._registry = provider_registry
        self._event_bus = event_bus

    async def handle(self, command: CompleteMeetingCommand) -> None:
        meeting = await self._repo.get_by_id(Id.from_string(command.meeting_id))
        if meeting is None:
            raise MeetingNotFoundException(command.meeting_id)
        _require_organizer(meeting, command.caller_id)
        meeting.complete()
        await self._repo.update(meeting)
        await self._event_bus.publish_all(meeting.clear_domain_events())

        try:
            adapter = self._registry.get(meeting.conference_provider)
            await adapter.delete_room(meeting.conference_room_id)
        except Exception:
            pass


class CancelMeetingCommand(BaseCommand):
    caller_id: str
    meeting_id: str


class CancelMeetingHandler(BaseCommandHandler[CancelMeetingCommand, None]):
    """Отмена совещания. После отмены пытается удалить комнату у провайдера (best-effort)."""

    def __init__(
        self,
        meeting_repo: MeetingRepository,
        provider_registry: ConferenceProviderRegistry,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = meeting_repo
        self._registry = provider_registry
        self._event_bus = event_bus

    async def handle(self, command: CancelMeetingCommand) -> None:
        meeting = await self._repo.get_by_id(Id.from_string(command.meeting_id))
        if meeting is None:
            raise MeetingNotFoundException(command.meeting_id)
        _require_organizer(meeting, command.caller_id)
        meeting.cancel()
        await self._repo.update(meeting)
        await self._event_bus.publish_all(meeting.clear_domain_events())

        # Best-effort удаление комнаты у провайдера.
        try:
            adapter = self._registry.get(meeting.conference_provider)
            await adapter.delete_room(meeting.conference_room_id)
        except Exception:
            pass
