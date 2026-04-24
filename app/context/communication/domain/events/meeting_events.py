from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_domain_event import BaseDomainEvent
from app.context.communication.domain.value_objects.meeting_type import MeetingType
from app.context.communication.domain.value_objects.rsvp_status import RSVPStatus


@dataclass(frozen=True)
class MeetingScheduled(BaseDomainEvent):
    """Совещание запланировано."""

    meeting_id: str = ""
    title: str = ""
    scheduled_at: str = ""
    meeting_type: MeetingType = MeetingType.VIDEO_CALL


@dataclass(frozen=True)
class MeetingUpdated(BaseDomainEvent):
    """Совещание обновлено."""

    meeting_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MeetingCancelled(BaseDomainEvent):
    """Совещание отменено."""

    meeting_id: str = ""


@dataclass(frozen=True)
class MeetingStarted(BaseDomainEvent):
    """Совещание начато."""

    meeting_id: str = ""


@dataclass(frozen=True)
class MeetingCompleted(BaseDomainEvent):
    """Совещание завершено."""

    meeting_id: str = ""


@dataclass(frozen=True)
class MeetingNoteAdded(BaseDomainEvent):
    """Заметка добавлена."""

    meeting_id: str = ""
    note_id: str = ""


@dataclass(frozen=True)
class MeetingActionItemAdded(BaseDomainEvent):
    """Action item добавлен."""

    meeting_id: str = ""
    action_item_id: str = ""


@dataclass(frozen=True)
class MeetingActionItemCompleted(BaseDomainEvent):
    """Action item завершён."""

    meeting_id: str = ""
    action_item_id: str = ""


@dataclass(frozen=True)
class MeetingRSVPUpdated(BaseDomainEvent):
    """RSVP ответ обновлён."""

    meeting_id: str = ""
    user_id: str = ""
    rsvp_status: RSVPStatus = RSVPStatus.PENDING


@dataclass(frozen=True)
class RecurringMeetingCreated(BaseDomainEvent):
    """Повторяющееся совещание создано."""

    source_meeting_id: str = ""
    new_meeting_id: str = ""
