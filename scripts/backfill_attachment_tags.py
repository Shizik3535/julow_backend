"""
Backfill системных тегов (`source:*`, `project:<id>`) для уже существующих
файлов, прикреплённых к сообщениям чата и к комментариям.

Назначение
==========
Команды ``AddMessageAttachmentHandler`` и ``AddCommentAttachmentHandler``
проставляют файлам теги `source:chat` / `source:comment` и (где
применимо) `project:<id>` уже в момент загрузки. Для вложений,
залитых ДО этого изменения, теги отсутствуют — поэтому UI-фильтр
"Чат" и проектная навигация в documents-странице их не показывают.

Этот скрипт решает разовую задачу backfill'а: пробегает по всем
``chat_message_attachments`` и ``comment_attachments`` и добивает
недостающие теги в ``fs_file_tags``.

Идемпотентность
===============
Уникальный ключ ``uq_fs_file_tags_file_name`` (file_id, name) даёт
естественную защиту от дубликатов: для существующих тегов делается
``ON CONFLICT DO NOTHING``. Скрипт можно запускать многократно.

Использование
=============
    python -m scripts.backfill_attachment_tags              # apply
    python -m scripts.backfill_attachment_tags --dry-run    # только отчёт
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

import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config.database_settings import DatabaseSettings


async def _backfill_chat_attachment_tags(session: AsyncSession, dry_run: bool) -> tuple[int, int]:
    """
    Для каждой пары (file_id, chat.project_id) проставить теги
    `source:chat` и (если у чата есть project_id) `project:<id>`.

    Возвращает (planned_inserts, applied_inserts). Для dry-run второе = 0.
    """
    # Получаем все уникальные (file_id, project_id) для сообщений из
    # активных чатов. DISTINCT — потому что один файл может быть прикреплён
    # ко множеству сообщений теоретически, хотя в текущем коде создание
    # уникальное (file_id = attachment_id = result.file_id).
    rows = await session.execute(
        text(
            """
            SELECT DISTINCT a.file_id, c.project_id
            FROM chat_message_attachments a
            JOIN chat_messages m ON m.id = a.message_id
            JOIN chats c ON c.id = m.chat_id
            """
        )
    )
    pairs = list(rows.mappings())
    print(f"-> Found {len(pairs)} chat-attachment file(s)")

    planned = 0
    applied = 0
    for row in pairs:
        file_id = row["file_id"]
        project_id = row["project_id"]
        wanted = ["source:chat"]
        if project_id is not None:
            wanted.append(f"project:{project_id}")

        for name in wanted:
            planned += 1
            if dry_run:
                print(f"  + DRY    chat file={file_id} tag={name!r}")
                continue
            res = await session.execute(
                text(
                    """
                    INSERT INTO fs_file_tags (id, file_id, name, color)
                    VALUES (:id, :file_id, :name, NULL)
                    ON CONFLICT ON CONSTRAINT uq_fs_file_tags_file_name DO NOTHING
                    """
                ),
                {"id": uuid.uuid4(), "file_id": file_id, "name": name},
            )
            if res.rowcount:
                applied += 1
                print(f"  + tag    chat file={file_id} tag={name!r}")
            else:
                print(f"  = exist  chat file={file_id} tag={name!r}")

    return planned, applied


async def _backfill_task_attachment_tags(session: AsyncSession, dry_run: bool) -> tuple[int, int]:
    """
    Для каждого ``task_attachments.file_id`` проставить теги:
      * ``source:task`` — фильтр «Источник = Задача» в UI документов.
      * ``project:<tasks.project_id>`` — чтобы файл попадал в проектный
        фильтр сайдбара документов.

    Возвращает (planned_inserts, applied_inserts).
    """
    rows = await session.execute(
        text(
            """
            SELECT DISTINCT a.file_id, t.project_id
            FROM task_attachments a
            JOIN tasks t ON t.id = a.task_id
            """
        )
    )
    pairs = list(rows.mappings())
    print(f"-> Found {len(pairs)} task-attachment file(s)")

    planned = 0
    applied = 0
    for row in pairs:
        file_id = row["file_id"]
        project_id = row["project_id"]
        wanted = ["source:task"]
        if project_id is not None:
            wanted.append(f"project:{project_id}")

        for name in wanted:
            planned += 1
            if dry_run:
                print(f"  + DRY    task file={file_id} tag={name!r}")
                continue
            res = await session.execute(
                text(
                    """
                    INSERT INTO fs_file_tags (id, file_id, name, color)
                    VALUES (:id, :file_id, :name, NULL)
                    ON CONFLICT ON CONSTRAINT uq_fs_file_tags_file_name DO NOTHING
                    """
                ),
                {"id": uuid.uuid4(), "file_id": file_id, "name": name},
            )
            if res.rowcount:
                applied += 1
                print(f"  + tag    task file={file_id} tag={name!r}")
            else:
                print(f"  = exist  task file={file_id} tag={name!r}")

    return planned, applied


async def _backfill_comment_attachment_tags(session: AsyncSession, dry_run: bool) -> tuple[int, int]:
    """
    Для каждого ``comment_attachments.file_id`` проставить теги:
      * ``source:comment`` — фильтр «Источник = Комментарий» в UI.
      * ``project:<id>`` — резолвится по ``comments.target_type``/``target_id``:
        - TASK    → tasks.project_id
        - EPIC    → epics.project_id
        - SPRINT  → sprints.project_id
        - PROJECT → target_id и есть project_id

    Резолв через SQL JOIN'ы — без поднятия доменной логики; в случае
    неподдерживаемых target_type (MILESTONE/MEETING/...) проставится
    только ``source:comment``.
    """
    rows = await session.execute(
        text(
            """
            SELECT DISTINCT
                ca.file_id        AS file_id,
                c.target_type     AS target_type,
                CASE c.target_type
                    WHEN 'TASK'    THEN (SELECT project_id FROM tasks   WHERE id = c.target_id)
                    WHEN 'EPIC'    THEN (SELECT project_id FROM epics   WHERE id = c.target_id)
                    WHEN 'SPRINT'  THEN (SELECT project_id FROM sprints WHERE id = c.target_id)
                    WHEN 'PROJECT' THEN c.target_id
                    ELSE NULL
                END               AS project_id
            FROM comment_attachments ca
            JOIN comments c ON c.id = ca.comment_id
            """
        )
    )
    pairs = list(rows.mappings())
    print(f"-> Found {len(pairs)} comment-attachment file(s)")

    planned = 0
    applied = 0
    for row in pairs:
        file_id = row["file_id"]
        project_id = row["project_id"]
        wanted = ["source:comment"]
        if project_id is not None:
            wanted.append(f"project:{project_id}")

        for name in wanted:
            planned += 1
            if dry_run:
                print(f"  + DRY    comment file={file_id} tag={name!r}")
                continue
            res = await session.execute(
                text(
                    """
                    INSERT INTO fs_file_tags (id, file_id, name, color)
                    VALUES (:id, :file_id, :name, NULL)
                    ON CONFLICT ON CONSTRAINT uq_fs_file_tags_file_name DO NOTHING
                    """
                ),
                {"id": uuid.uuid4(), "file_id": file_id, "name": name},
            )
            if res.rowcount:
                applied += 1
                print(f"  + tag    comment file={file_id} tag={name!r}")
            else:
                print(f"  = exist  comment file={file_id} tag={name!r}")

    return planned, applied


async def backfill(dry_run: bool = False) -> None:
    settings = DatabaseSettings()
    engine = create_async_engine(settings.url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        chat_planned, chat_applied = await _backfill_chat_attachment_tags(session, dry_run)
        task_planned, task_applied = await _backfill_task_attachment_tags(session, dry_run)
        comment_planned, comment_applied = await _backfill_comment_attachment_tags(session, dry_run)

        if not dry_run:
            await session.commit()

    await engine.dispose()

    print()
    print(
        "OK Backfill complete: "
        f"chat_planned={chat_planned} chat_applied={chat_applied} "
        f"task_planned={task_planned} task_applied={task_applied} "
        f"comment_planned={comment_planned} comment_applied={comment_applied} "
        f"dry_run={dry_run}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill attachment tags (source:*, project:<id>)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Только отчёт без записи в БД",
    )
    args = parser.parse_args()
    asyncio.run(backfill(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
