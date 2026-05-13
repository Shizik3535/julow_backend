"""timetracking unique constraints and indexes

Adds:
- UNIQUE (workspace_id, name) on activity_categories and time_entry_tags
- index on time_entry_tag_links.tag_id (m2m secondary lookup)
- indexes on name columns of activity_categories and time_entry_tags

Revision ID: d5e6f7a8b9c0
Revises: c4d5e6f7a8b9
Create Date: 2026-05-09 20:50:00.000000+00:00
"""
from collections.abc import Sequence

from alembic import op


revision: str = "d5e6f7a8b9c0"
down_revision: str | Sequence[str] | None = "c4d5e6f7a8b9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Unique (workspace_id, name) constraints
    op.create_unique_constraint(
        "uq_time_entry_tags_workspace_name",
        "time_entry_tags",
        ["workspace_id", "name"],
    )
    op.create_unique_constraint(
        "uq_activity_categories_workspace_name",
        "activity_categories",
        ["workspace_id", "name"],
    )

    # Index for reverse m2m lookup
    op.create_index(
        "ix_time_entry_tag_links_tag_id",
        "time_entry_tag_links",
        ["tag_id"],
    )

    # Indexes on name columns (search/lookups by name)
    op.create_index("ix_time_entry_tags_name", "time_entry_tags", ["name"])
    op.create_index("ix_activity_categories_name", "activity_categories", ["name"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_activity_categories_name", table_name="activity_categories")
    op.drop_index("ix_time_entry_tags_name", table_name="time_entry_tags")
    op.drop_index("ix_time_entry_tag_links_tag_id", table_name="time_entry_tag_links")
    op.drop_constraint(
        "uq_activity_categories_workspace_name",
        "activity_categories",
        type_="unique",
    )
    op.drop_constraint(
        "uq_time_entry_tags_workspace_name",
        "time_entry_tags",
        type_="unique",
    )
