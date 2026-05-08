from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.url_vo import Url
from app.shared.domain.value_objects.rich_text_vo import RichText
from app.shared.domain.value_objects.agenda_vo import Agenda
from app.context.communication.domain.value_objects.conference_provider import ConferenceProvider
from app.context.communication.domain.value_objects.meeting_status import MeetingStatus
from app.context.communication.domain.value_objects.meeting_type import MeetingType
from app.context.communication.domain.value_objects.rsvp_status import RSVPStatus
from app.context.communication.domain.value_objects.recurrence_config import RecurrenceConfig
from app.context.communication.domain.entities.meeting_participant import MeetingParticipant
from app.context.communication.domain.entities.meeting_note import MeetingNote
from app.context.communication.domain.entities.meeting_action_item import MeetingActionItem
from app.context.communication.domain.events.meeting_events import (
    MeetingScheduled,
    MeetingUpdated,
    MeetingCancelled,
    MeetingStarted,
    MeetingCompleted,
    MeetingNoteAdded,
    MeetingActionItemAdded,
    MeetingActionItemCompleted,
    MeetingParticipantAdded,
    MeetingParticipantRemoved,
    MeetingRSVPUpdated,
)
from app.context.communication.domain.exceptions.meeting_exceptions import (
    CannotAddMeetingNoteException,
    MeetingAlreadyStartedException,
    MeetingAlreadyCompletedException,
    InvalidRSVPStatusTransitionException,
    MeetingActionItemNotFoundException,
)

_VALID_RSVP_TRANSITIONS: dict[RSVPStatus, set[RSVPStatus]] = {
    RSVPStatus.PENDING: {RSVPStatus.ACCEPTED, RSVPStatus.DECLINED, RSVPStatus.TENTATIVE},
    RSVPStatus.TENTATIVE: {RSVPStatus.ACCEPTED, RSVPStatus.DECLINED},
    RSVPStatus.DECLINED: {RSVPStatus.TENTATIVE},
    RSVPStatus.ACCEPTED: set(),
}


@dataclass
class Meeting(AggregateRoot):
    """
    Корень агрегата совещания (Communication BC).

    Атрибуты:
        title: Название.
        description: Описание.
        meeting_type: Формат совещания.
        agenda: Повестка (из shared kernel).
        status: Статус.
        scheduled_at: Время начала.
        duration_minutes: Длительность в минутах.
        location: Место проведения (для IN_PERSON).
        conference_url: URL видеозвонка (из shared kernel).
        project_id: Opaque ID проекта.
        workspace_id: Opaque ID workspace.
        organizer_id: ID организатора.
        participants: Список участников.
        notes: Список заметок.
        action_items: Список action items.
        recurrence: Конфигурация повторения.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    title: str = ""
    description: RichText | None = None
    meeting_type: MeetingType = MeetingType.VIDEO_CALL
    agenda: Agenda | None = None
    status: MeetingStatus = MeetingStatus.SCHEDULED
    scheduled_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    duration_minutes: int | None = None
    location: str | None = None
    conference_provider: ConferenceProvider = ConferenceProvider.MANUAL
    conference_url: Url | None = None
    conference_room_id: str | None = None
    project_id: Id | None = None
    workspace_id: Id = field(default_factory=Id.generate)
    organizer_id: Id = field(default_factory=Id.generate)
    participants: list[MeetingParticipant] = field(default_factory=list)
    notes: list[MeetingNote] = field(default_factory=list)
    action_items: list[MeetingActionItem] = field(default_factory=list)
    recurrence: RecurrenceConfig | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @classmethod
    def create(
        cls,
        title: str,
        scheduled_at: datetime,
        workspace_id: Id,
        organizer_id: Id,
        meeting_type: MeetingType,
        agenda: Agenda | None = None,
        duration_minutes: int | None = None,
        project_id: Id | None = None,
        recurrence: RecurrenceConfig | None = None,
        conference_provider: ConferenceProvider = ConferenceProvider.MANUAL,
        conference_url: Url | None = None,
        conference_room_id: str | None = None,
        description: RichText | None = None,
        location: str | None = None,
    ) -> Meeting:
        """Создаёт совещание. Организатор автоматически добавляется как participant."""
        meeting = cls(
            title=title,
            scheduled_at=scheduled_at,
            workspace_id=workspace_id,
            organizer_id=organizer_id,
            meeting_type=meeting_type,
            agenda=agenda,
            duration_minutes=duration_minutes,
            project_id=project_id,
            recurrence=recurrence,
            conference_provider=conference_provider,
            conference_url=conference_url,
            conference_room_id=conference_room_id,
            description=description,
            location=location,
        )
        meeting.participants = [
            MeetingParticipant(user_id=organizer_id, is_mandatory=True, rsvp_status=RSVPStatus.ACCEPTED),
        ]
        meeting._register_event(
            MeetingScheduled(
                meeting_id=str(meeting.id),
                title=title,
                scheduled_at=str(scheduled_at),
                meeting_type=meeting_type,
            )
        )
        return meeting

    def update(
        self,
        title: str | None = None,
        agenda: Agenda | None = None,
        scheduled_at: datetime | None = None,
        duration_minutes: int | None = None,
        description: RichText | None = None,
        location: str | None = None,
        conference_url: Url | None = None,
    ) -> None:
        if self.status in (MeetingStatus.COMPLETED, MeetingStatus.CANCELLED):
            raise ValueError("Нельзя обновить завершённое/отменённое совещание")
        changed: list[str] = []
        if title is not None and self.title != title:
            self.title = title
            changed.append("title")
        if agenda is not None and self.agenda != agenda:
            self.agenda = agenda
            changed.append("agenda")
        if scheduled_at is not None and self.scheduled_at != scheduled_at:
            self.scheduled_at = scheduled_at
            changed.append("scheduled_at")
        if duration_minutes is not None and self.duration_minutes != duration_minutes:
            self.duration_minutes = duration_minutes
            changed.append("duration_minutes")
        if description is not None and self.description != description:
            self.description = description
            changed.append("description")
        if location is not None and self.location != location:
            self.location = location
            changed.append("location")
        if conference_url is not None and self.conference_url != conference_url:
            self.conference_url = conference_url
            changed.append("conference_url")
        if changed:
            self.updated_at = datetime.now(tz=timezone.utc)
            self._register_event(
                MeetingUpdated(meeting_id=str(self.id), changed_fields=changed)
            )

    # --- Участники ---

    def add_participant(self, user_id: Id, is_mandatory: bool = True) -> None:
        if self.status == MeetingStatus.CANCELLED:
            raise ValueError("Нельзя добавить участника в отменённое совещание")
        if any(p.user_id == user_id for p in self.participants):
            return
        participant = MeetingParticipant(user_id=user_id, is_mandatory=is_mandatory)
        self.participants.append(participant)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            MeetingParticipantAdded(meeting_id=str(self.id), user_id=str(user_id))
        )

    def remove_participant(self, user_id: Id) -> None:
        if user_id == self.organizer_id:
            raise ValueError("Нельзя удалить организатора")
        before = len(self.participants)
        self.participants = [p for p in self.participants if p.user_id != user_id]
        if len(self.participants) == before:
            return
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            MeetingParticipantRemoved(meeting_id=str(self.id), user_id=str(user_id))
        )

    def is_participant(self, user_id: Id) -> bool:
        return any(p.user_id == user_id for p in self.participants)

    def _set_conference(
        self,
        provider: ConferenceProvider,
        url: Url | None,
        room_id: str | None,
    ) -> None:
        """Зафиксировать данные конференции.

        Метод намеренно сделан приватным: он является частью протокола
        создания Meeting (URL/room_id известны только после обращения
        к внешнему провайдеру и потому не могут быть переданы в
        :meth:`create`). Для модификаций после создания используйте
        команды, которые должны эмитить соответствующие доменные события.
        """
        self.conference_provider = provider
        self.conference_url = url
        self.conference_room_id = room_id
        self.updated_at = datetime.now(tz=timezone.utc)

    def update_rsvp(self, user_id: Id, rsvp_status: RSVPStatus) -> None:
        participant = next((p for p in self.participants if p.user_id == user_id), None)
        if participant is None:
            raise ValueError(f"Участник не найден: {user_id}")
        allowed = _VALID_RSVP_TRANSITIONS.get(participant.rsvp_status, set())
        if rsvp_status not in allowed:
            raise InvalidRSVPStatusTransitionException(
                from_status=participant.rsvp_status.value,
                to_status=rsvp_status.value,
            )
        participant.rsvp_status = rsvp_status
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            MeetingRSVPUpdated(
                meeting_id=str(self.id),
                user_id=str(user_id),
                rsvp_status=rsvp_status,
            )
        )

    # --- Жизненный цикл ---

    def start(self) -> None:
        if self.status == MeetingStatus.IN_PROGRESS:
            raise MeetingAlreadyStartedException()
        if self.status in (MeetingStatus.COMPLETED, MeetingStatus.CANCELLED):
            raise MeetingAlreadyCompletedException()
        self.status = MeetingStatus.IN_PROGRESS
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(MeetingStarted(meeting_id=str(self.id)))

    def complete(self) -> None:
        if self.status == MeetingStatus.COMPLETED:
            raise MeetingAlreadyCompletedException()
        if self.status == MeetingStatus.CANCELLED:
            raise MeetingAlreadyCompletedException()
        self.status = MeetingStatus.COMPLETED
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(MeetingCompleted(meeting_id=str(self.id)))

    def cancel(self) -> None:
        if self.status in (MeetingStatus.COMPLETED, MeetingStatus.CANCELLED):
            raise MeetingAlreadyCompletedException()
        self.status = MeetingStatus.CANCELLED
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(MeetingCancelled(meeting_id=str(self.id)))

    # --- Заметки ---

    def add_note(self, content: RichText | None, author_id: Id) -> None:
        if self.status not in (MeetingStatus.IN_PROGRESS, MeetingStatus.COMPLETED):
            raise CannotAddMeetingNoteException()
        note = MeetingNote(content=content, author_id=author_id)
        self.notes.append(note)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            MeetingNoteAdded(meeting_id=str(self.id), note_id=str(note.id))
        )

    # --- Action Items ---

    def add_action_item(self, text: str, assignee_id: Id | None = None, due_date: datetime | None = None) -> None:
        item = MeetingActionItem(text=text, assignee_id=assignee_id)
        self.action_items.append(item)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            MeetingActionItemAdded(meeting_id=str(self.id), action_item_id=str(item.id))
        )

    def complete_action_item(self, action_item_id: Id) -> None:
        item = next((ai for ai in self.action_items if ai.id == action_item_id), None)
        if item is None:
            raise MeetingActionItemNotFoundException(id=action_item_id)
        item.is_completed = True
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            MeetingActionItemCompleted(meeting_id=str(self.id), action_item_id=str(action_item_id))
        )

    def remove_action_item(self, action_item_id: Id) -> None:
        self.action_items = [ai for ai in self.action_items if ai.id != action_item_id]
        self.updated_at = datetime.now(tz=timezone.utc)
