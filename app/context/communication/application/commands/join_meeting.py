"""Команда подключения к совещанию: возвращает join_url + access_token."""

from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.communication.application.dto.meeting_dto import MeetingJoinDTO
from app.context.communication.application.exceptions.authorization_exceptions import (
    NotMeetingParticipantException,
)
from app.context.communication.domain.events.meeting_events import (
    MeetingJoinRequested,
)
from app.context.communication.domain.exceptions.meeting_exceptions import (
    MeetingNotFoundException,
)
from app.context.communication.domain.repositories.meeting_repository import (
    MeetingRepository,
)
from app.context.communication.domain.value_objects.conference_provider import (
    ConferenceProvider,
)
from app.context.communication.infrastructure.integration.inboard.conference_provider_registry import (
    ConferenceProviderRegistry,
)


class JoinMeetingCommand(BaseCommand):
    """Запросить подключение к совещанию.

    Атрибуты:
        caller_id: ID пользователя.
        meeting_id: ID совещания.
    """

    caller_id: str
    meeting_id: str


class JoinMeetingHandler(BaseCommandHandler[JoinMeetingCommand, MeetingJoinDTO]):
    """
    Делегирует генерацию join-токена адаптеру по ``conference_provider``.

    Для MANUAL — возвращает сохранённый URL без токена.
    Для INTERNAL/Zoom/etc — адаптер возвращает join_url + access_token.
    """

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

    async def handle(self, command: JoinMeetingCommand) -> MeetingJoinDTO:
        meeting = await self._repo.get_by_id(Id.from_string(command.meeting_id))
        if meeting is None:
            raise MeetingNotFoundException(command.meeting_id)

        if not meeting.is_participant(Id.from_string(command.caller_id)):
            raise NotMeetingParticipantException()

        adapter = self._registry.get(meeting.conference_provider)
        token = await adapter.generate_join_token(
            external_id=meeting.conference_room_id,
            manual_url=str(meeting.conference_url) if meeting.conference_url else None,
            user_id=command.caller_id,
            is_organizer=str(meeting.organizer_id) == command.caller_id,
        )

        # Регистрируем событие join-запроса (для аналитики, метрик).
        if meeting.conference_provider != ConferenceProvider.MANUAL:
            await self._event_bus.publish_all(
                [
                    MeetingJoinRequested(
                        meeting_id=str(meeting.id),
                        user_id=command.caller_id,
                        provider=meeting.conference_provider.value,
                    )
                ]
            )

        return MeetingJoinDTO(
            join_url=token.join_url,
            access_token=token.access_token,
            provider=meeting.conference_provider.value,
        )
