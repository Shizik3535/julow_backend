"""
Backfill системных проектных чатов для проектов, у которых ≥2 активных
участника, но чат ещё не был создан.

Назначение
==========
Auto-creation чата запускается обработчиком ``OnProjectMemberJoinedSyncChat``,
который слушает ``ProjectMemberJoined`` события в Kafka. Для проектов, в
которых второй (и далее) участник присоединился ДО внедрения обработчика,
исторические события уже не воспроизводимы — кафка-консьюмер их
давно скоммитил. Поэтому нужен явный backfill.

Идемпотентность
===============
Скрипт пропускает проекты, у которых уже есть чат (``chat.project_id``
matches). Можно запускать многократно без побочных эффектов.

Использование
=============
    python -m scripts.backfill_project_chats              # apply
    python -m scripts.backfill_project_chats --dry-run    # только отчёт
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

# Windows-консоль по умолчанию cp1252; форсируем UTF-8 для stdout, чтобы
# имена проектов с кириллицей корректно печатались. На *nix это no-op.
try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

# Ensure project root is on sys.path so `app` is importable
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.context.communication.domain.aggregates.chat import Chat
from app.context.communication.infrastructure.persistence.mappers.chat_mapper import (
    ChatMapper,
)
from app.context.communication.infrastructure.persistence.repositories.sql_chat_repository import (
    SqlChatRepository,
)
from app.core.config.database_settings import DatabaseSettings
from app.shared.domain.value_objects.id_vo import Id


async def _fetch_eligible_projects(session: AsyncSession) -> list[dict]:
    """
    Найти все active-проекты с ≥1 активным участником.

    Проектный чат теперь создаётся даже у solo-владельца (см.
    ``OnProjectMemberJoinedSyncChat`` с ``_MIN_PROJECT_CHAT_MEMBERS = 1``).

    Возвращает list of dicts с полями:
      - project_id (UUID): идентификатор проекта;
      - name (str): имя проекта для chat.name;
      - workspace_id (UUID | None): workspace для chat.workspace_id;
      - member_ids (list[UUID]): все active user_id в проекте;
      - owner_id (UUID | None): первый owner проекта (для chat OWNER-role).
    """
    # Фильтр `status = 'active'` исключает проекты в pending_deletion —
    # для них чат должен быть архивным; backfill это не его задача.
    # owner_id берём через подзапрос project_owners (project_id, user_id)
    # — это plain join-таблица без timestamp, поэтому просто LIMIT 1.
    rows = await session.execute(
        text(
            """
            WITH active_members AS (
                SELECT
                    pm.project_id,
                    array_agg(DISTINCT m.user_id) AS user_ids
                FROM project_memberships pm
                JOIN project_members m ON m.membership_id = pm.id
                WHERE m.is_active = TRUE
                GROUP BY pm.project_id
                HAVING count(*) >= 1
            )
            SELECT
                p.id AS project_id,
                p.name AS name,
                p.workspace_id AS workspace_id,
                am.user_ids AS user_ids,
                (
                    SELECT po.user_id
                    FROM project_owners po
                    WHERE po.project_id = p.id
                    LIMIT 1
                ) AS owner_id
            FROM active_members am
            JOIN projects p ON p.id = am.project_id
            WHERE p.status = 'active'
            ORDER BY p.created_at ASC
            """
        )
    )
    result: list[dict] = []
    for row in rows.mappings():
        result.append(
            {
                "project_id": row["project_id"],
                "name": row["name"],
                "workspace_id": row["workspace_id"],
                "user_ids": list(row["user_ids"] or []),
                "owner_id": row["owner_id"],
            }
        )
    return result


async def backfill(dry_run: bool = False) -> None:
    settings = DatabaseSettings()
    engine = create_async_engine(settings.url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    created = 0
    skipped = 0

    async with session_factory() as session:
        eligible = await _fetch_eligible_projects(session)
        print(f"-> Found {len(eligible)} project(s) with >=1 active members")

        repo = SqlChatRepository(session=session, mapper=ChatMapper())

        for proj in eligible:
            project_id = Id(value=proj["project_id"])
            existing = await repo.get_by_project_id(project_id)
            if existing is not None:
                skipped += 1
                print(
                    f"  ~ skip   project={proj['project_id']} "
                    f"chat_exists={existing.id} archived={existing.is_archived}"
                )
                continue

            owner_id_raw = proj["owner_id"]
            owner_id = Id(value=owner_id_raw) if owner_id_raw else None
            workspace_id_raw = proj["workspace_id"]
            workspace_id = Id(value=workspace_id_raw) if workspace_id_raw else None
            member_ids = [Id(value=uid) for uid in proj["user_ids"]]

            chat = Chat.create_project_chat(
                name=str(proj["name"] or f"Project {project_id}"),
                project_id=project_id,
                workspace_id=workspace_id,
                member_ids=member_ids,
                owner_id=owner_id,
            )
            # Не публикуем доменные события — это исторический backfill,
            # на ChatCreated не должны срабатывать notifications для уже
            # давно состоящих пользователей.
            chat.clear_domain_events()

            if dry_run:
                print(
                    f"  + DRY    project={proj['project_id']} "
                    f"name={chat.name!r} members={len(member_ids)} "
                    f"workspace={workspace_id_raw}"
                )
            else:
                await repo.add(chat)
                created += 1
                print(
                    f"  + create project={proj['project_id']} "
                    f"chat_id={chat.id} members={len(member_ids)}"
                )

        if not dry_run:
            await session.commit()

    await engine.dispose()

    print()
    print(f"OK Backfill complete: created={created} skipped={skipped} dry_run={dry_run}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill project chats")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Только отчёт без записи в БД",
    )
    args = parser.parse_args()
    asyncio.run(backfill(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
