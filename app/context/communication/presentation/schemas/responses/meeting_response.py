from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class MeetingParticipantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    is_mandatory: bool = True
    rsvp_status: str = "pending"
    joined_at: datetime | None = None


class MeetingNoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    author_id: str
    content: str | None = None
    content_format: str = "markdown"
    created_at: datetime | None = None


class MeetingActionItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    text: str
    assignee_id: str | None = None
    due_date: date | None = None
    is_completed: bool = False


class RecurrenceConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pattern: str = "weekly"
    interval: int = 1
    end_date: date | None = None
    max_occurrences: int | None = None


class MeetingResponse(BaseModel):
    """Ответ с данными совещания."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str | None = None
    description_format: str = "markdown"
    meeting_type: str
    status: str
    scheduled_at: datetime | None = None
    duration_minutes: int | None = None
    location: str | None = None
    conference_provider: str = "manual"
    conference_url: str | None = None
    conference_room_id: str | None = None
    project_id: str | None = None
    workspace_id: str
    organizer_id: str
    participants: list[MeetingParticipantResponse] = Field(default_factory=list)
    notes: list[MeetingNoteResponse] = Field(default_factory=list)
    action_items: list[MeetingActionItemResponse] = Field(default_factory=list)
    recurrence: RecurrenceConfigResponse | None = None
    agenda: list[str] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class MeetingListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[MeetingResponse] = Field(default_factory=list)
    total: int = 0


class MeetingJoinResponse(BaseModel):
    """Ответ на запрос подключения."""

    model_config = ConfigDict(from_attributes=True)

    join_url: str
    access_token: str | None = None
    provider: str
