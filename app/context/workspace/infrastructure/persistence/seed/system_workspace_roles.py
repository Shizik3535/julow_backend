"""
Seed-данные для системных ролей workspace (Workspace BC).

Глобальные системные роли (workspace_id IS NULL) — доступны
во всех workspace как шаблоны. Включают права на уровне проектов
(`projects.*`), чтобы workspace-роли корректно покрывали
каскад Project → Workspace.

Используется в:
    - scripts/seed_workspace_roles.py
    - tests/integration/conftest.py
    - tests/e2e/conftest.py
"""
from __future__ import annotations

from uuid import UUID


SYSTEM_WORKSPACE_ROLES: list[dict[str, object]] = [
    {
        "id": UUID("00000000-0000-0000-0002-000000000001"),
        "workspace_id": None,
        "name": "owner",
        "permissions": ["ws.*"],
        "is_system": True,
        "description": "Полный доступ к workspace и всем проектам",
    },
    {
        "id": UUID("00000000-0000-0000-0002-000000000002"),
        "workspace_id": None,
        "name": "admin",
        "permissions": [
            "ws.read",
            "ws.settings.*",
            "members.*",
            "roles.*",
            "teams.*",
            "projects.*",
            "ws.projects.*",
            "projects.tasks.*",
            "files.*",
            "storage.*",
            "time.*",
        ],
        "is_system": True,
        "description": "Управление workspace, проектами и файлами",
    },
    {
        "id": UUID("00000000-0000-0000-0002-000000000003"),
        "workspace_id": None,
        "name": "manager",
        "permissions": [
            "ws.read",
            "members.read",
            "teams.*",
            "projects.read",
            "projects.members.*",
            "projects.workflow.read",
            "projects.tasks.*",
            "files.read",
            "files.write",
            "files.share",
            "storage.read",
            "time.read",
            "time.write",
            "time.submit",
            "time.approve",
            "time.admin",
        ],
        "is_system": True,
        "description": "Управление командами и процессами проектов",
    },
    {
        "id": UUID("00000000-0000-0000-0002-000000000004"),
        "workspace_id": None,
        "name": "member",
        "permissions": [
            "ws.read",
            "members.read",
            "projects.read",
            "projects.tasks.read",
            "projects.tasks.create",
            "projects.tasks.update",
            "projects.tasks.assign",
            "projects.tasks.watch",
            "files.read",
            "files.write",
            "storage.read",
            "time.read",
            "time.write",
            "time.delete",
            "time.submit",
        ],
        "is_system": True,
        "description": "Базовый доступ к workspace и проектам",
    },
]
