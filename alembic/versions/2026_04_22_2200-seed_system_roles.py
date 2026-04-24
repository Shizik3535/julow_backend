"""seed system roles

Revision ID: a1b2c3d4e5f6
Revises: fd6013d644ae
Create Date: 2026-04-22 22:00:00.000000+00:00

"""
import json
from typing import Sequence, Union
from uuid import UUID

from alembic import op
import sqlalchemy as sa

from app.context.identity.infrastructure.persistence.seed.system_roles import SYSTEM_ROLES


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'fd6013d644ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ROLE_NAMES = [r["name"] for r in SYSTEM_ROLES]


def upgrade() -> None:
    """Insert 4 system roles (idempotent via ON CONFLICT DO NOTHING)."""
    for role in SYSTEM_ROLES:
        op.execute(
            sa.text(
                "INSERT INTO roles (id, name, permissions, is_system, description, created_at, updated_at) "
                "VALUES (CAST(:id AS uuid), :name, CAST(:permissions AS jsonb), :is_system, :description, now(), now()) "
                "ON CONFLICT (name) DO NOTHING"
            ).bindparams(
                id=str(role["id"]),
                name=role["name"],
                permissions=json.dumps(role["permissions"]),
                is_system=role["is_system"],
                description=role["description"],
            )
        )


def downgrade() -> None:
    """Remove system roles by name."""
    op.execute(
        sa.text("DELETE FROM roles WHERE name = ANY(:names)").bindparams(
            names=ROLE_NAMES
        )
    )
