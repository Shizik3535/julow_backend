"""merge analytics and project-invitations heads

Revision ID: 3c2d52a54f9e
Revises: c2d3e4f5a6b7, a1b2c3d4e5f6
Create Date: 2026-05-17 17:51:31.096126+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c2d52a54f9e'
down_revision: Union[str, Sequence[str], None] = ('c2d3e4f5a6b7', 'a1b2c3d4e5f6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
