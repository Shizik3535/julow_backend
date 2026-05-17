"""seed system dashboard templates

Inserts global system dashboard templates (is_system=True, workspace_id NULL)
from app.context.analytics.infrastructure.persistence.seed.system_dashboard_templates.

Идемпотентность — через ON CONFLICT (id) DO NOTHING на стабильных UUID
(в analytics_dashboard_templates нет уникального индекса по name).

Revision ID: a1b2c3d4e5f6
Revises: f8a9b0c1d2e3
Create Date: 2026-05-17 20:30:00.000000+00:00
"""
import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.context.analytics.infrastructure.persistence.seed.system_dashboard_templates import (
    SYSTEM_DASHBOARD_TEMPLATES,
)


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "f8a9b0c1d2e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TEMPLATE_IDS = [str(t["id"]) for t in SYSTEM_DASHBOARD_TEMPLATES]


def upgrade() -> None:
    """Вставить системные шаблоны (idempotent via ON CONFLICT DO NOTHING)."""
    for template in SYSTEM_DASHBOARD_TEMPLATES:
        op.execute(
            sa.text(
                "INSERT INTO analytics_dashboard_templates ("
                "  id, workspace_id, name, description, widget_configs,"
                "  is_system, is_deleted, created_at, updated_at"
                ") VALUES ("
                "  CAST(:id AS uuid), NULL, :name, :description,"
                "  CAST(:widget_configs AS jsonb),"
                "  :is_system, :is_deleted, now(), now()"
                ") ON CONFLICT (id) DO NOTHING"
            ).bindparams(
                id=str(template["id"]),
                name=template["name"],
                description=template["description"],
                widget_configs=json.dumps(template["widget_configs"]),
                is_system=template["is_system"],
                is_deleted=template["is_deleted"],
            )
        )


def downgrade() -> None:
    """Удалить системные шаблоны по их UUID."""
    for tid in TEMPLATE_IDS:
        op.execute(
            sa.text(
                "DELETE FROM analytics_dashboard_templates WHERE id = CAST(:id AS uuid)"
            ).bindparams(id=tid)
        )
