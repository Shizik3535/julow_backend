"""add project_id column to chats

Добавляет колонку ``project_id`` в таблицу ``chats``: ссылка на проект,
к которому привязан системный групповой чат. Используется обработчиками
Communication BC, синхронизирующими участников чата с участниками проекта.

Колонка nullable — у DM/обычных групп/каналов/anouncement она остаётся NULL.
Внешний ключ намеренно не добавляется: ``project_id`` — opaque ID из другого
BC (Project BC), межконтекстные FK мы не делаем, чтобы сохранить независимое
жизненное удаление проектов и чатов.

Revision ID: c2d3e4f5a6b7
Revises: a1b2c3d4e5f6
Create Date: 2026-05-14 00:30:00.000000+00:00
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "c2d3e4f5a6b7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add nullable project_id column with index."""
    op.add_column(
        "chats",
        sa.Column("project_id", sa.Uuid(), nullable=True),
    )
    op.create_index("ix_chats_project_id", "chats", ["project_id"])


def downgrade() -> None:
    """Drop project_id column."""
    op.drop_index("ix_chats_project_id", table_name="chats")
    op.drop_column("chats", "project_id")
