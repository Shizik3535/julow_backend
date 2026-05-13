"""add_sso_enforce_and_integration_fields

Revision ID: 5cad42b1f3a7
Revises: b5a09105c9ac
Create Date: 2026-05-04 23:40:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5cad42b1f3a7'
down_revision: Union[str, Sequence[str], None] = 'b5a09105c9ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add enforce_sso to organizations, email_domains/auto_provision/default_role_id to sso_integrations."""
    # --- organizations: enforce_sso ---
    op.add_column(
        'organizations',
        sa.Column('sp_enforce_sso', sa.Boolean(), nullable=False, server_default=sa.text('false')),
    )

    # --- sso_integrations: email_domains, auto_provision, default_role_id ---
    op.add_column(
        'sso_integrations',
        sa.Column('email_domains', sa.JSON(), nullable=True),
    )
    op.add_column(
        'sso_integrations',
        sa.Column('auto_provision', sa.Boolean(), nullable=False, server_default=sa.text('false')),
    )
    op.add_column(
        'sso_integrations',
        sa.Column('default_role_id', sa.Uuid(), nullable=True),
    )


def downgrade() -> None:
    """Remove enforce_sso from organizations, email_domains/auto_provision/default_role_id from sso_integrations."""
    op.drop_column('sso_integrations', 'default_role_id')
    op.drop_column('sso_integrations', 'auto_provision')
    op.drop_column('sso_integrations', 'email_domains')
    op.drop_column('organizations', 'sp_enforce_sso')
