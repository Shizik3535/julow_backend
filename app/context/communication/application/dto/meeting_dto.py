from __future__ import annotations

from datetime import date, datetime

from app.shared.application.base_dto import BaseDTO


class MeetingParticipantDTO(BaseDTO):
    """DTO участника совещания."""

    user_id: str
    is_mandatory: bool = True
    rsvp_status: str = "pending"
    joined_at: datetime | None = None


class MeetingNoteDTO(BaseDTO):
    """DTO заметки совещания."""

    id: str
    author_id: str
    content: str | None = None
    content_format: str = "markdown"
    created_at: datetime | None = None


class MeetingActionItemDTO(BaseDTO):
    """DTO action item."""

    id: str
    text: str
    assignee_id: str | None = None
    due_date: date | None = None
    is_completed: bool = False


class RecurrenceConfigDTO(BaseDTO):
    """DTO конфигурации повторения."""

    pattern: str = "weekly"
    interval: int = 1
    end_date: date | None = None
    max_occurrences: int | None = None


class MeetingDTO(BaseDTO):
    """
    DTO совещания (Communication BC).
    """

    id: str
    title: str
    description: str | None = None
    description_format: str = "markdown"
    meeting_type: str = "video_call"
    status: str = "scheduled"
    scheduled_at: datetime | None = None
    duration_minutes: int | None = None
    location: str | None = None
    conference_provider: str = "manual"
    conference_url: str | None = None
    conference_room_id: str | None = None
    project_id: str | None = None
    workspace_id: str
    organizer_id: str
    participants: list[MeetingParticipantDTO] = []
    notes: list[MeetingNoteDTO] = []
    action_items: list[MeetingActionItemDTO] = []
    recurrence: RecurrenceConfigDTO | None = None
    agenda: list[str] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None


class MeetingListDTO(BaseDTO):
    """Список совещаний."""

    items: list[MeetingDTO] = []
    total: int = 0


class MeetingJoinDTO(BaseDTO):
    """Результат запроса подключения к совещанию."""

    join_url: str
    access_token: str | None = None
    provider: str
