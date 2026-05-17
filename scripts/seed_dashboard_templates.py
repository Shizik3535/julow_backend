"""
Standalone script to seed system dashboard templates into the database.

Idempotent: uses INSERT ... ON CONFLICT (id) DO NOTHING на стабильных UUID,
поэтому повторный запуск безопасен.

Usage:
    python -m scripts.seed_dashboard_templates
    python scripts/seed_dashboard_templates.py
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

from app.context.analytics.infrastructure.persistence.seed.system_dashboard_templates import (
    SYSTEM_DASHBOARD_TEMPLATES,
)
from app.core.config.database_settings import DatabaseSettings


async def seed_dashboard_templates() -> None:
    settings = DatabaseSettings()
    engine = create_async_engine(settings.url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        inserted = 0
        for template in SYSTEM_DASHBOARD_TEMPLATES:
            result = await session.execute(
                text(
                    "INSERT INTO analytics_dashboard_templates ("
                    "  id, workspace_id, name, description, widget_configs,"
                    "  is_system, is_deleted, created_at, updated_at"
                    ") VALUES ("
                    "  CAST(:id AS uuid), NULL, :name, :description,"
                    "  CAST(:widget_configs AS jsonb),"
                    "  :is_system, :is_deleted, now(), now()"
                    ") ON CONFLICT (id) DO NOTHING"
                ),
                {
                    "id": str(template["id"]),
                    "name": template["name"],
                    "description": template["description"],
                    "widget_configs": json.dumps(template["widget_configs"]),
                    "is_system": template["is_system"],
                    "is_deleted": template["is_deleted"],
                },
            )
            inserted += result.rowcount
        await session.commit()

        if inserted:
            print(f"✓ Inserted {inserted} system dashboard template(s)")
        else:
            print("✓ All system dashboard templates already exist — nothing to insert")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_dashboard_templates())
