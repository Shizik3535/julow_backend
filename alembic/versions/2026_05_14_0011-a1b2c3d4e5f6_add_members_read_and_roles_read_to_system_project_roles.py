"""add members.read and roles.read to manager/member/guest project roles

После принятия приглашения пользователь получал membership в проекте
с ролью `member` или `guest`, но эти системные роли НЕ имели разрешений
`members.read` и `roles.read`. В результате:
  - `GetProjectMembersHandler` (REQUIRED = `members.read`) и
  - `GetProjectRolesHandler` (REQUIRED = `roles.read`)
кидали 403, и в UI диалог «Участники проекта» показывал баннер
«Недостаточно прав … требуется разрешение «roles.read»». Пользователь
не видел даже список тиммейтов и их ролей.

Эта миграция:
  - добавляет `members.read` и `roles.read` ко ВСЕМ системным
    project-ролям с именами `manager`, `member`, `guest` (включая
    глобальные шаблоны с `project_id IS NULL` и per-project копии,
    создаваемые `CreateProjectCommand`);
  - роль `admin` уже покрыта через `members.*` / `roles.*` (wildcard);
  - роль `owner` уже покрыта через `project.*` (wildcard).

Идемпотентно: использует `@>` для проверки наличия каждого permission
по отдельности и добавляет только отсутствующие.

Revision ID: a1b2c3d4e5f7
Revises: f7a8b9c0d1e2
Create Date: 2026-05-14 00:11:00.000000+00:00
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f7"
down_revision: Union[str, Sequence[str], None] = "f7a8b9c0d1e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Имена ролей, которым нужно добавить read-доступ к members/roles.
# admin покрыт wildcards `members.*`/`roles.*`, owner — `project.*`.
TARGET_ROLE_NAMES = ("manager", "member", "guest")

# Список permission'ов, которые нужно гарантировать. Добавляются по одному,
# чтобы идемпотентность работала независимо для каждого permission'а:
# если одна уже есть, а другой нет — добавится только отсутствующий.
PERMISSIONS_TO_ADD = ("members.read", "roles.read")


def _add_permission_sql(permission: str) -> sa.TextClause:
    """
    Добавляет один permission в массив permissions, если его там ещё нет.

    Колонка `permissions` имеет тип JSON (не JSONB), поэтому JSONB-операторы
    `@>` и `||` напрямую недоступны. Кастуем в JSONB → выполняем операцию →
    кастуем обратно в JSON (тип колонки). Имя ролей передаём через
    PostgreSQL array literal (`{a,b,c}`) и `ANY(... :: TEXT[])`.
    """
    return sa.text(
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
        perm_array=f'["{permission}"]',
    )


def _remove_permission_sql(permission: str) -> sa.TextClause:
    """Удалить один permission из массива у тех же ролей. Используется в downgrade."""
    return sa.text(
        """
        UPDATE project_roles
        SET permissions = CAST(
                (CAST(permissions AS JSONB) - :perm_value)
                AS JSON
            ),
            updated_at = now()
        WHERE is_system = true
          AND name = ANY(CAST(:names AS TEXT[]))
        """
    ).bindparams(
        names="{" + ",".join(TARGET_ROLE_NAMES) + "}",
        perm_value=permission,
    )


def upgrade() -> None:
    for perm in PERMISSIONS_TO_ADD:
        op.execute(_add_permission_sql(perm))


def downgrade() -> None:
    for perm in PERMISSIONS_TO_ADD:
        op.execute(_remove_permission_sql(perm))
