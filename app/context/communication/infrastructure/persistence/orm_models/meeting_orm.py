from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


class MeetingORM(BaseORMModel):
    """ORM-модель таблицы meetings."""

    __tablename__ = "meetings"
    __table_args__ = (
        Index("ix_meetings_workspace_scheduled", "workspace_id", "scheduled_at"),
        Index("ix_meetings_project", "project_id"),
        Index("ix_meetings_organizer", "organizer_id"),
        Index("ix_meetings_status", "status"),
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_format: Mapped[str] = mapped_column(
        String(16), nullable=False, default="markdown"
    )
    meeting_type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    location: Mapped[str | None] = mapped_column(String(512), nullable=True)

    conference_provider: Mapped[str] = mapped_column(
        String(32), nullable=False, default="manual"
    )
    conference_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    conference_room_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    project_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    organizer_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)

    # Recurrence (embedded VO, optional)
    recurrence_pattern: Mapped[str | None] = mapped_column(String(32), nullable=True)
    recurrence_interval: Mapped[int | None] = mapped_column(Integer, nullable=True)
    recurrence_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    recurrence_max_occurrences: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    # Agenda (embedded VO, list[AgendaItem]) — храним как JSON для простоты
    agenda: Mapped[list | None] = mapped_column(JSON, nullable=True)

    participants: Mapped[list["MeetingParticipantORM"]] = relationship(
        "MeetingParticipantORM",
        cascade="all, delete-orphan",
        lazy="selectin",
        back_populates="meeting",
    )
    notes: Mapped[list["MeetingNoteORM"]] = relationship(
        "MeetingNoteORM",
        cascade="all, delete-orphan",
        lazy="selectin",
        back_populates="meeting",
    )
    action_items: Mapped[list["MeetingActionItemORM"]] = relationship(
        "MeetingActionItemORM",
        cascade="all, delete-orphan",
        lazy="selectin",
        back_populates="meeting",
    )


class MeetingParticipantORM(BaseORMModel):
    """ORM-модель таблицы meeting_participants."""

    __tablename__ = "meeting_participants"
    __table_args__ = (
        UniqueConstraint(
            "meeting_id",
            "user_id",
            name="uq_meeting_participants_meeting_user",
        ),
    )

    meeting_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    rsvp_status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="pending"
    )
    participant_joined_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    meeting: Mapped["MeetingORM"] = relationship(
        "MeetingORM", back_populates="participants"
    )


class MeetingNoteORM(BaseORMModel):
    """ORM-модель таблицы meeting_notes."""

    __tablename__ = "meeting_notes"

    meeting_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_format: Mapped[str] = mapped_column(
        String(16), nullable=False, default="markdown"
    )
    note_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    meeting: Mapped["MeetingORM"] = relationship(
        "MeetingORM", back_populates="notes"
    )


class MeetingActionItemORM(BaseORMModel):
    """ORM-модель таблицы meeting_action_items."""

    __tablename__ = "meeting_action_items"

    meeting_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_completed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, index=True
    )

    meeting: Mapped["MeetingORM"] = relationship(
        "MeetingORM", back_populates="action_items"
    )
