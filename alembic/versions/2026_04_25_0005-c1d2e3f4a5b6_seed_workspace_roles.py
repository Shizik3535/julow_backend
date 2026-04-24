"""seed workspace roles

Revision ID: c1d2e3f4a5b6
Revises: b0a97c3a34a4
Create Date: 2026-04-25 00:05:00.000000+00:00

"""
import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.context.workspace.infrastructure.persistence.seed.system_workspace_roles import SYSTEM_WORKSPACE_ROLES


# revision identifiers, used by Alembic.
revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, Sequence[str], None] = 'b0a97c3a34a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

WS_ROLE_IDS = [str(r["id"]) for r in SYSTEM_WORKSPACE_ROLES]


def upgrade() -> None:
    """Insert 4 system workspace roles (idempotent via ON CONFLICT DO NOTHING)."""
    for role in SYSTEM_WORKSPACE_ROLES:
        op.execute(
            sa.text(
                "INSERT INTO workspace_roles "
                "(id, workspace_id, name, permissions, is_system, description, created_at, updated_at) "
                "VALUES (CAST(:id AS uuid), :workspace_id, :name, CAST(:permissions AS jsonb), "
                ":is_system, :description, now(), now()) "
                "ON CONFLICT (id) DO NOTHING"
            ).bindparams(
                id=str(role["id"]),
                workspace_id=role["workspace_id"],
                name=role["name"],
                permissions=json.dumps(role["permissions"]),
                is_system=role["is_system"],
                description=role["description"],
            )
        )


def downgrade() -> None:
    """Remove system workspace roles by id."""
    op.execute(
        sa.text("DELETE FROM workspace_roles WHERE id = ANY(:ids)").bindparams(
            ids=WS_ROLE_IDS
        )
    )
