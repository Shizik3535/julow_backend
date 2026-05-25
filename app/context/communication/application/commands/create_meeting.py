"""Команда создания совещания."""

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
from app.context.communication.domain.aggregates.meeting import Meeting
from app.context.communication.domain.repositories.meeting_repository import (
    MeetingRepository,
)
from app.context.communication.domain.value_objects.conference_provider import (
    ConferenceProvider,
)
from app.context.communication.domain.value_objects.meeting_type import MeetingType
from app.context.communication.domain.value_objects.recurrence_config import (
    RecurrenceConfig,
)
from app.context.communication.domain.value_objects.recurrence_pattern import (
    RecurrencePattern,
)
from app.context.communication.infrastructure.integration.inboard.conference_provider_registry import (
    ConferenceProviderRegistry,
)


class CreateMeetingCommand(BaseCommand):
    """
    Команда создания совещания.

    Атрибуты:
        caller_id: ID организатора (он же создатель).
        workspace_id: UUID workspace.
        title: Название.
        scheduled_at: Время начала.
        meeting_type: in_person/video_call/phone_call/hybrid.
        conference_provider: manual/internal/zoom/telemost/google_meet/teams.
        manual_url: Ссылка для MANUAL-провайдера.
        agenda: Пункты повестки (тексты).
        duration_minutes: Длительность.
        description: Описание (markdown/wysiwyg).
        description_format: Формат описания.
        location: Место (для IN_PERSON).
        project_id: UUID проекта (опционально).
        recurrence_pattern: weekly/daily/monthly (опционально).
        recurrence_interval: Интервал.
    """

    caller_id: str
    workspace_id: str
    title: str
    scheduled_at: datetime | None = None
    meeting_type: str = "video_call"
    conference_provider: str = "manual"
    manual_url: str | None = None
    agenda: list[str] = []
    duration_minutes: int | None = None
    description: str | None = None
    description_format: str = "markdown"
    location: str | None = None
    project_id: str | None = None
    participant_ids: list[str] = []
    recurrence_pattern: str | None = None
    recurrence_interval: int = 1


class CreateMeetingHandler(BaseCommandHandler[CreateMeetingCommand, MeetingDTO]):
    """
    Создаёт совещание и регистрирует комнату через ``ConferenceProviderPort``.

    Для MANUAL — просто сохраняет переданный ``manual_url``.
    Для остальных провайдеров делегирует адаптеру.
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

    async def handle(self, command: CreateMeetingCommand) -> MeetingDTO:
        provider = ConferenceProvider(command.conference_provider)
        adapter = self._registry.get(provider)

        # Создаём агрегат сразу — нам нужен meeting_id для имени комнаты
        description: RichText | None = None
        if command.description is not None:
            description = RichText(
                content=command.description,
                format=RichTextFormat(command.description_format),
            )
        agenda: Agenda | None = None
        if command.agenda:
            agenda = Agenda(items=[AgendaItem(text=t) for t in command.agenda])

        recurrence: RecurrenceConfig | None = None
        if command.recurrence_pattern is not None:
            recurrence = RecurrenceConfig(
                pattern=RecurrencePattern(command.recurrence_pattern),
                interval=command.recurrence_interval,
            )

        meeting = Meeting.create(
            title=command.title,
            scheduled_at=command.scheduled_at,
            workspace_id=Id.from_string(command.workspace_id),
            organizer_id=Id.from_string(command.caller_id),
            meeting_type=MeetingType(command.meeting_type),
            agenda=agenda,
            duration_minutes=command.duration_minutes,
            project_id=(
                Id.from_string(command.project_id) if command.project_id else None
            ),
            recurrence=recurrence,
            conference_provider=provider,
            description=description,
            location=command.location,
        )

        room = await adapter.create_room(
            meeting_id=str(meeting.id),
            organizer_id=command.caller_id,
            manual_url=command.manual_url,
        )
        meeting._set_conference(
            provider=provider,
            url=Url(value=room.join_url) if room.join_url else None,
            room_id=room.external_id,
        )

        # Регистрируем дополнительных участников. Делаем это ДО `repo.add`,
        # чтобы маппер сразу записал их в `meeting_participants`. Дубликаты
        # и сам организатор фильтруются — `add_participant` бросает ValueError
        # на дубль, поэтому ловим аккуратно.
        for pid in command.participant_ids:
            if not pid or pid == command.caller_id:
                continue
            try:
                meeting.add_participant(Id.from_string(pid))
            except ValueError:
                # Игнорируем дубликаты / некорректные id — приглашение
                # участника не должно валить создание встречи.
                continue

        await self._repo.add(meeting)
        await self._event_bus.publish_all(meeting.clear_domain_events())
        return meeting_to_dto(meeting)
