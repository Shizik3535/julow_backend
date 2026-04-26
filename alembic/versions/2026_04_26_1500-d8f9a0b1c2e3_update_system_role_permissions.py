"""update system role permissions

Remove dead permissions (content.*, content.read, self.*) and add
missing ones (org.read, roles.*, invitations.read, departments.read,
cascade task permissions for moderator, etc.).

Revision ID: d8f9a0b1c2e3
Revises: 467e66bf1128
Create Date: 2026-04-26 15:00:00.000000+00:00

"""
import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.context.organization.infrastructure.persistence.seed.org_roles import SYSTEM_ORG_ROLES
from app.context.workspace.infrastructure.persistence.seed.system_workspace_roles import SYSTEM_WORKSPACE_ROLES
from app.context.project.infrastructure.persistence.seed.system_project_roles import SYSTEM_PROJECT_ROLES


# revision identifiers, used by Alembic.
revision: str = 'd8f9a0b1c2e3'
down_revision: Union[str, Sequence[str], None] = '467e66bf1128'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Update permissions for all system roles across org/workspace/project."""
    for role in SYSTEM_ORG_ROLES:
        op.execute(
            sa.text(
                "UPDATE org_roles SET permissions = CAST(:permissions AS jsonb), "
                "updated_at = now() WHERE id = CAST(:id AS uuid)"
            ).bindparams(
                id=str(role["id"]),
                permissions=json.dumps(role["permissions"]),
            )
        )

    for role in SYSTEM_WORKSPACE_ROLES:
        op.execute(
            sa.text(
                "UPDATE workspace_roles SET permissions = CAST(:permissions AS jsonb), "
                "updated_at = now() WHERE id = CAST(:id AS uuid)"
            ).bindparams(
                id=str(role["id"]),
                permissions=json.dumps(role["permissions"]),
            )
        )

    for role in SYSTEM_PROJECT_ROLES:
        op.execute(
            sa.text(
                "UPDATE project_roles SET permissions = CAST(:permissions AS jsonb), "
                "updated_at = now() WHERE id = CAST(:id AS uuid)"
            ).bindparams(
                id=str(role["id"]),
                permissions=json.dumps(role["permissions"]),
            )
        )


def downgrade() -> None:
    """Downgrade is not supported — old permissions are dead code."""
    raise NotImplementedError("Downgrade not supported for permission updates")
