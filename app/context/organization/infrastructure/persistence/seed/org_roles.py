"""
Seed-данные для системных орг-ролей (Organization BC).

Используется в:
    - scripts/seed_org_roles.py
    - tests/integration/conftest.py
    - tests/e2e/conftest.py
    - alembic data migration
"""
from __future__ import annotations

from uuid import UUID


SYSTEM_ORG_ROLES: list[dict[str, object]] = [
    {
        "id": UUID("00000000-0000-0000-0000-000000000011"),
        "org_id": None,
        "name": "owner",
        # «org.*» покрывает всё (включая workspaces.*) на уровне Organization BC
        # при wildcard-матчинге; дублируем workspaces.* явно для ясности.
        "permissions": ["org.*", "workspaces.*"],
        "is_system": True,
        "description": "Полный доступ, управление владельцами",
        "scope": "org",
    },
    {
        "id": UUID("00000000-0000-0000-0000-000000000012"),
        "org_id": None,
        "name": "admin",
        "permissions": [
            "org.settings.*",
            "members.*",
            "teams.*",
            "departments.*",
            "content.*",
            "workspaces.*",
            "workspaces.projects.*",
            "workspaces.projects.tasks.*",
        ],
        "is_system": True,
        "description": "Управление организацией",
        "scope": "org",
    },
    {
        "id": UUID("00000000-0000-0000-0000-000000000013"),
        "org_id": None,
        "name": "moderator",
        "permissions": [
            "members.read",
            "members.invite",
            "content.*",
            "teams.*",
            "workspaces.read",
            "workspaces.members.read",
            "workspaces.members.invite",
            "workspaces.projects.read",
            "workspaces.projects.tasks.read",
        ],
        "is_system": True,
        "description": "Ограниченное управление",
        "scope": "org",
    },
    {
        "id": UUID("00000000-0000-0000-0000-000000000014"),
        "org_id": None,
        "name": "member",
        "permissions": [
            "self.*",
            "content.read",
            "teams.read",
            "workspaces.read",
            "workspaces.projects.read",
            "workspaces.projects.tasks.read",
        ],
        "is_system": True,
        "description": "Базовый доступ",
        "scope": "org",
    },
]
