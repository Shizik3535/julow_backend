"""add project.read to system project roles

Системные project-роли (`admin`, `manager`, `member`, `guest`) не имели
разрешения `project.read`. Из-за этого все запросы с
`REQUIRED_PERMISSION = "project.read"` (GetProjectsByMemberHandler,
GetProjectHandler, GetBoardHandler, GetProjectTasksHandler) отказывали
приглашённым пользователям в доступе — проект «исчезал» из списка и
страница доски бесконечно крутила лоадер.

Миграция:
  - обновляет ВСЕ `project_roles` с `is_system=true` (как глобальные
    шаблоны с project_id IS NULL, так и per-project копии, создаваемые
    `CreateProjectCommand`) — добавляет `project.read` в начало массива
    `permissions`, если его там ещё нет. Идемпотентно.
  - роль `owner` уже имеет `project.*` (wildcard), его не трогаем.

Revision ID: f7a8b9c0d1e2
Revises: e6f7a8b9c0d1
Create Date: 2026-05-14 00:10:00.000000+00:00
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "f7a8b9c0d1e2"
down_revision: Union[str, Sequence[str], None] = "e6f7a8b9c0d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Имена ролей, которым нужно добавить project.read.
# owner уже покрыт через project.* (wildcard) — пропускаем.
TARGET_ROLE_NAMES = ("admin", "manager", "member", "guest")


def upgrade() -> None:
    """
    Идемпотентно добавляет `"project.read"` в массив permissions
    у всех системных project-ролей с указанными именами.

    Использует SQL JSONB-выражение, чтобы не дёргать данные в Python:
        permissions = (
            CASE
                WHEN permissions @> '["project.read"]'::jsonb THEN permissions
                ELSE permissions || '["project.read"]'::jsonb
            END
        )
    """
    # Колонка `permissions` имеет тип JSON (не JSONB), поэтому операторы
    # `@>` и `||` не определены напрямую. Кастуем обе стороны в jsonb,
    # потом результат обратно в json (тип колонки). Также SQLAlchemy не
    # парсит `::jsonb` как cast (путает с bindparam), поэтому используем
    # `CAST(... AS JSONB)`.
    op.execute(
        sa.text(
            """
            UPDATE project_roles
            SET permissions = CASE
                    WHEN CAST(permissions AS JSONB) @> CAST(:perm_array AS JSONB)
                        THEN permissions
                    ELSE CAST(
                        CAST(permissions AS JSONB) || CAST(:perm_array AS JSONB)
                        AS JSON
                    )
                END,
                updated_at = now()
            WHERE is_system = true
              AND name = ANY(CAST(:names AS TEXT[]))
            """
        ).bindparams(
            names="{" + ",".join(TARGET_ROLE_NAMES) + "}",
            perm_array='["project.read"]',
        )
    )


def downgrade() -> None:
    """
    Откат: убрать `project.read` из тех же ролей. Используем jsonb_path_query
    с фильтрацией. Реализуется как `permissions - 'project.read'` (binary
    operator JSONB minus text — удаляет элемент из массива).
    """
    op.execute(
        sa.text(
            """
            UPDATE project_roles
            SET permissions = CAST(
                    (CAST(permissions AS JSONB) - 'project.read')
                    AS JSON
                ),
                updated_at = now()
            WHERE is_system = true
              AND name = ANY(CAST(:names AS TEXT[]))
            """
        ).bindparams(names="{" + ",".join(TARGET_ROLE_NAMES) + "}")
    )
