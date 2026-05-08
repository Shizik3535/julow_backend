"""meeting_initial

Создаёт таблицы Meeting агрегата (Communication BC):
meetings, meeting_participants, meeting_notes, meeting_action_items.

Revision ID: e0f1a2b3c4d5
Revises: d9e0f1a2b3c4
Create Date: 2026-05-08 18:00:00.000000+00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op


revision: str = "e0f1a2b3c4d5"
down_revision: str | Sequence[str] | None = "d9e0f1a2b3c4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "meetings",
        sa.Column("title", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("description_format", sa.String(length=16), nullable=False, server_default="markdown"),
        sa.Column("meeting_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("location", sa.String(length=512), nullable=True),
        sa.Column("conference_provider", sa.String(length=32), nullable=False, server_default="manual"),
        sa.Column("conference_url", sa.String(length=2048), nullable=True),
        sa.Column("conference_room_id", sa.String(length=255), nullable=True),
        sa.Column("project_id", sa.Uuid(), nullable=True),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("organizer_id", sa.Uuid(), nullable=False),
        sa.Column("recurrence_pattern", sa.String(length=32), nullable=True),
        sa.Column("recurrence_interval", sa.Integer(), nullable=True),
        sa.Column("recurrence_end_date", sa.Date(), nullable=True),
        sa.Column("recurrence_max_occurrences", sa.Integer(), nullable=True),
        sa.Column("agenda", sa.JSON(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_meetings_status", "meetings", ["status"])
    op.create_index("ix_meetings_workspace_scheduled", "meetings", ["workspace_id", "scheduled_at"])
    op.create_index("ix_meetings_project", "meetings", ["project_id"])
    op.create_index("ix_meetings_organizer", "meetings", ["organizer_id"])

    op.create_table(
        "meeting_participants",
        sa.Column("meeting_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("is_mandatory", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("rsvp_status", sa.String(length=16), nullable=False, server_default="pending"),
        sa.Column("participant_joined_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["meeting_id"], ["meetings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("meeting_id", "user_id", name="uq_meeting_participants_meeting_user"),
    )
    op.create_index("ix_meeting_participants_meeting_id", "meeting_participants", ["meeting_id"])
    op.create_index("ix_meeting_participants_user_id", "meeting_participants", ["user_id"])

    op.create_table(
        "meeting_notes",
        sa.Column("meeting_id", sa.Uuid(), nullable=False),
        sa.Column("author_id", sa.Uuid(), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("content_format", sa.String(length=16), nullable=False, server_default="markdown"),
        sa.Column("note_created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["meeting_id"], ["meetings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_meeting_notes_meeting_id", "meeting_notes", ["meeting_id"])

    op.create_table(
        "meeting_action_items",
        sa.Column("meeting_id", sa.Uuid(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False, server_default=""),
        sa.Column("assignee_id", sa.Uuid(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["meeting_id"], ["meetings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_meeting_action_items_meeting_id", "meeting_action_items", ["meeting_id"])
    op.create_index("ix_meeting_action_items_is_completed", "meeting_action_items", ["is_completed"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_meeting_action_items_is_completed", table_name="meeting_action_items")
    op.drop_index("ix_meeting_action_items_meeting_id", table_name="meeting_action_items")
    op.drop_table("meeting_action_items")
    op.drop_index("ix_meeting_notes_meeting_id", table_name="meeting_notes")
    op.drop_table("meeting_notes")
    op.drop_index("ix_meeting_participants_user_id", table_name="meeting_participants")
    op.drop_index("ix_meeting_participants_meeting_id", table_name="meeting_participants")
    op.drop_table("meeting_participants")
    op.drop_index("ix_meetings_organizer", table_name="meetings")
    op.drop_index("ix_meetings_project", table_name="meetings")
    op.drop_index("ix_meetings_workspace_scheduled", table_name="meetings")
    op.drop_index("ix_meetings_status", table_name="meetings")
    op.drop_table("meetings")
