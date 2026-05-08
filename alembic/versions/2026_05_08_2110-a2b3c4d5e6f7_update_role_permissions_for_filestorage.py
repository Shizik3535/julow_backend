"""update role permissions for filestorage

Adds `files.*` / `storage.*` (workspace) and `workspaces.files.*` /
`workspaces.storage.*` (org) permissions to existing system roles.

Revision ID: a2b3c4d5e6f7
Revises: f1a2b3c4d5e6
Create Date: 2026-05-08 21:10:00.000000+00:00
"""
import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.context.organization.infrastructure.persistence.seed.org_roles import SYSTEM_ORG_ROLES
from app.context.workspace.infrastructure.persistence.seed.system_workspace_roles import SYSTEM_WORKSPACE_ROLES


revision: str = "a2b3c4d5e6f7"
down_revision: Union[str, Sequence[str], None] = "f1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Sync system role permissions to include FileStorage permissions."""
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


def downgrade() -> None:
    """Downgrade not supported — file permissions are part of the system contract."""
    raise NotImplementedError("Downgrade not supported for role permission updates")
