"""
Standalone script to seed system project roles into the database.

Idempotent: uses INSERT ... ON CONFLICT (id) DO NOTHING,
so it's safe to run multiple times.

Usage:
    python -m scripts.seed_project_roles
    python scripts/seed_project_roles.py
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

# Ensure project root is on sys.path so `app` is importable
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.context.project.infrastructure.persistence.seed.system_project_roles import SYSTEM_PROJECT_ROLES
from app.core.config.database_settings import DatabaseSettings


async def seed_project_roles() -> None:
    settings = DatabaseSettings()
    engine = create_async_engine(settings.url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        inserted = 0
        for role in SYSTEM_PROJECT_ROLES:
            result = await session.execute(
                text(
                    "INSERT INTO project_roles "
                    "(id, project_id, name, permissions, is_system, description, created_at, updated_at) "
                    "VALUES (CAST(:id AS uuid), :project_id, :name, CAST(:permissions AS jsonb), "
                    ":is_system, :description, now(), now()) "
                    "ON CONFLICT (id) DO NOTHING"
                ),
                {
                    "id": str(role["id"]),
                    "project_id": role["project_id"],
                    "name": role["name"],
                    "permissions": json.dumps(role["permissions"]),
                    "is_system": role["is_system"],
                    "description": role["description"],
                },
            )
            inserted += result.rowcount
        await session.commit()

        if inserted:
            print(f"✓ Inserted {inserted} system project role(s)")
        else:
            print("✓ All system project roles already exist — nothing to insert")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_project_roles())
