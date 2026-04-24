"""seed org roles

Revision ID: b2c3d4e5f6a7
Revises: 736039843518
Create Date: 2026-04-24 17:00:00.000000+00:00

"""
import json
from typing import Sequence, Union
from uuid import UUID

import sqlalchemy as sa
from alembic import op

from app.context.organization.infrastructure.persistence.seed.org_roles import SYSTEM_ORG_ROLES


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = '736039843518'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ORG_ROLE_IDS = [str(r["id"]) for r in SYSTEM_ORG_ROLES]


def upgrade() -> None:
    """Insert 4 system org roles (idempotent via ON CONFLICT DO NOTHING)."""
    for role in SYSTEM_ORG_ROLES:
        op.execute(
            sa.text(
                "INSERT INTO org_roles (id, org_id, name, permissions, is_system, description, scope, created_at, updated_at) "
                "VALUES (CAST(:id AS uuid), :org_id, :name, CAST(:permissions AS jsonb), :is_system, :description, :scope, now(), now()) "
                "ON CONFLICT (id) DO NOTHING"
            ).bindparams(
                id=str(role["id"]),
                org_id=role["org_id"],
                name=role["name"],
                permissions=json.dumps(role["permissions"]),
                is_system=role["is_system"],
                description=role["description"],
                scope=role["scope"],
            )
        )


def downgrade() -> None:
    """Remove system org roles by id."""
    op.execute(
        sa.text("DELETE FROM org_roles WHERE id = ANY(:ids)").bindparams(
            ids=ORG_ROLE_IDS
        )
    )
