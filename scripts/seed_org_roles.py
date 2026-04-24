"""
Standalone script to seed system org roles into the database.

Idempotent: uses INSERT ... ON CONFLICT (id) DO NOTHING,
so it's safe to run multiple times.

Usage:
    python -m scripts.seed_org_roles
    python scripts/seed_org_roles.py
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

from app.context.organization.infrastructure.persistence.seed.org_roles import SYSTEM_ORG_ROLES
from app.core.config.database_settings import DatabaseSettings


async def seed_org_roles() -> None:
    settings = DatabaseSettings()
    engine = create_async_engine(settings.url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        inserted = 0
        for role in SYSTEM_ORG_ROLES:
            result = await session.execute(
                text(
                    "INSERT INTO org_roles (id, org_id, name, permissions, is_system, description, scope, created_at, updated_at) "
                    "VALUES (CAST(:id AS uuid), :org_id, :name, CAST(:permissions AS jsonb), :is_system, :description, :scope, now(), now()) "
                    "ON CONFLICT (id) DO NOTHING"
                ),
                {
                    "id": str(role["id"]),
                    "org_id": role["org_id"],
                    "name": role["name"],
                    "permissions": json.dumps(role["permissions"]),
                    "is_system": role["is_system"],
                    "description": role["description"],
                    "scope": role["scope"],
                },
            )
            inserted += result.rowcount
        await session.commit()

        if inserted:
            print(f"✓ Inserted {inserted} system org role(s)")
        else:
            print("✓ All system org roles already exist — nothing to insert")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_org_roles())
