"""timetracking_initial

Создаёт таблицы TimeTracking BC:
activity_categories, time_entry_tags, time_entries,
time_entry_time_logs, time_entry_tag_links.

Revision ID: b3c4d5e6f7a8
Revises: a2b3c4d5e6f7
Create Date: 2026-05-09 20:30:00.000000+00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op


revision: str = "b3c4d5e6f7a8"
down_revision: str | Sequence[str] | None = "a2b3c4d5e6f7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""

    # --- activity_categories ---
    op.create_table(
        "activity_categories",
        sa.Column("workspace_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("color", sa.String(length=7), nullable=True),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_activity_categories_workspace_id", "activity_categories", ["workspace_id"])

    # --- time_entry_tags ---
    op.create_table(
        "time_entry_tags",
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("color", sa.String(length=7), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_time_entry_tags_workspace_id", "time_entry_tags", ["workspace_id"])

    # --- time_entries ---
    op.create_table(
        "time_entries",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("task_id", sa.Uuid(), nullable=True),
        sa.Column("project_id", sa.Uuid(), nullable=True),
        sa.Column("epic_id", sa.Uuid(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("timer_state", sa.String(length=20), nullable=False, server_default="stopped"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("stopped_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("is_billable", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("hourly_rate_amount", sa.Numeric(18, 6), nullable=True),
        sa.Column("hourly_rate_currency", sa.String(length=3), nullable=True),
        sa.Column("category_id", sa.Uuid(), nullable=True),
        sa.Column("rounding_rule", sa.String(length=30), nullable=True),
        sa.Column("rounding_apply_to", sa.String(length=30), nullable=True),
        sa.Column("rejection_reason_text", sa.Text(), nullable=True),
        sa.Column("rejected_by", sa.Uuid(), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_time_entries_user_id", "time_entries", ["user_id"])
    op.create_index("ix_time_entries_workspace_id", "time_entries", ["workspace_id"])
    op.create_index("ix_time_entries_task_id", "time_entries", ["task_id"])
    op.create_index("ix_time_entries_project_id", "time_entries", ["project_id"])
    op.create_index("ix_time_entries_epic_id", "time_entries", ["epic_id"])
    op.create_index("ix_time_entries_status", "time_entries", ["status"])
    op.create_index("ix_time_entries_entry_date", "time_entries", ["entry_date"])
    op.create_index("ix_time_entries_category_id", "time_entries", ["category_id"])

    # --- time_entry_time_logs ---
    op.create_table(
        "time_entry_time_logs",
        sa.Column("time_entry_id", sa.Uuid(), nullable=False),
        sa.Column("action", sa.String(length=20), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accumulated_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["time_entry_id"], ["time_entries.id"], ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_time_entry_time_logs_time_entry_id", "time_entry_time_logs", ["time_entry_id"],
    )

    # --- time_entry_tag_links (m2m) ---
    op.create_table(
        "time_entry_tag_links",
        sa.Column("time_entry_id", sa.Uuid(), nullable=False),
        sa.Column("tag_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["time_entry_id"], ["time_entries.id"], ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"], ["time_entry_tags.id"], ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("time_entry_id", "tag_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("time_entry_tag_links")
    op.drop_index("ix_time_entry_time_logs_time_entry_id", table_name="time_entry_time_logs")
    op.drop_table("time_entry_time_logs")
    op.drop_index("ix_time_entries_category_id", table_name="time_entries")
    op.drop_index("ix_time_entries_entry_date", table_name="time_entries")
    op.drop_index("ix_time_entries_status", table_name="time_entries")
    op.drop_index("ix_time_entries_epic_id", table_name="time_entries")
    op.drop_index("ix_time_entries_project_id", table_name="time_entries")
    op.drop_index("ix_time_entries_task_id", table_name="time_entries")
    op.drop_index("ix_time_entries_workspace_id", table_name="time_entries")
    op.drop_index("ix_time_entries_user_id", table_name="time_entries")
    op.drop_table("time_entries")
    op.drop_index("ix_time_entry_tags_workspace_id", table_name="time_entry_tags")
    op.drop_table("time_entry_tags")
    op.drop_index("ix_activity_categories_workspace_id", table_name="activity_categories")
    op.drop_table("activity_categories")
