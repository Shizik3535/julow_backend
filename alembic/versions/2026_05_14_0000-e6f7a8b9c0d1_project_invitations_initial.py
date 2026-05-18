"""project invitations initial

Creates project_invitations table mirroring workspace_invitations pattern.

Revision ID: e6f7a8b9c0d1
Revises: d5e6f7a8b9c0
Create Date: 2026-05-14 00:00:00.000000+00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "e6f7a8b9c0d1"
down_revision: str | Sequence[str] | None = "d5e6f7a8b9c0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "project_invitations",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("token_value", sa.String(length=255), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("token_max_uses", sa.Integer(), nullable=True),
        sa.Column("token_used_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("role_id", sa.Uuid(), nullable=False),
        sa.Column("invited_by", sa.Uuid(), nullable=False),
        sa.Column("invited_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="pending"),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_project_invitations_project_id"),
        "project_invitations",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_invitations_workspace_id"),
        "project_invitations",
        ["workspace_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_invitations_token_value"),
        "project_invitations",
        ["token_value"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_invitations_role_id"),
        "project_invitations",
        ["role_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_invitations_user_id"),
        "project_invitations",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_project_invitations_user_id"), table_name="project_invitations")
    op.drop_index(op.f("ix_project_invitations_role_id"), table_name="project_invitations")
    op.drop_index(op.f("ix_project_invitations_token_value"), table_name="project_invitations")
    op.drop_index(op.f("ix_project_invitations_workspace_id"), table_name="project_invitations")
    op.drop_index(op.f("ix_project_invitations_project_id"), table_name="project_invitations")
    op.drop_table("project_invitations")
