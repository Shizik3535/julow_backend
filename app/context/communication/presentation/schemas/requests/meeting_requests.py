from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class CreateMeetingRequest(BaseModel):
    """Тело запроса на создание совещания."""

    title: str = Field(..., min_length=1, max_length=255)
    scheduled_at: datetime | None = None
    workspace_id: str
    meeting_type: str = Field(default="video_call", description="in_person/video_call/phone_call/hybrid")
    conference_provider: str = Field(
        default="manual",
        description="manual/internal/zoom/telemost/google_meet/teams",
    )
    manual_url: str | None = Field(
        default=None, description="Ссылка для MANUAL-провайдера"
    )
    agenda: list[str] = Field(default_factory=list)
    duration_minutes: int | None = Field(default=None, ge=1)
    description: str | None = None
    description_format: str = "markdown"
    location: str | None = None
    project_id: str | None = None
    recurrence_pattern: str | None = Field(
        default=None, description="daily/weekly/monthly/..."
    )
    recurrence_interval: int = Field(default=1, ge=1)


class UpdateMeetingRequest(BaseModel):
    """Тело запроса на обновление совещания."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    scheduled_at: datetime | None = None
    duration_minutes: int | None = Field(default=None, ge=1)
    description: str | None = None
    description_format: str = "markdown"
    location: str | None = None
    conference_url: str | None = None
    agenda: list[str] | None = None


class AddMeetingParticipantRequest(BaseModel):
    user_id: str
    is_mandatory: bool = True


class UpdateRSVPRequest(BaseModel):
    rsvp_status: str = Field(..., description="pending/accepted/declined/tentative")


class AddMeetingNoteRequest(BaseModel):
    content: str | None = None
    content_format: str = "markdown"


class AddActionItemRequest(BaseModel):
    text: str = Field(..., min_length=1)
    assignee_id: str | None = None
    due_date: date | None = None
