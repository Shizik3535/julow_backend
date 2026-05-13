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
            "org.read",
            "org.settings.*",
            "members.*",
            "roles.*",
            "teams.*",
            "departments.*",
            "invitations.read",
            "workspaces.*",
            "workspaces.projects.*",
            "workspaces.projects.tasks.*",
            "workspaces.files.*",
            "workspaces.storage.*",
            "workspaces.time.*",
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
            "org.read",
            "members.read",
            "members.invite",
            "invitations.read",
            "teams.*",
            "departments.read",
            "workspaces.read",
            "workspaces.members.read",
            "workspaces.members.invite",
            "workspaces.projects.read",
            "workspaces.projects.tasks.read",
            "workspaces.projects.tasks.create",
            "workspaces.projects.tasks.update",
            "workspaces.projects.tasks.assign",
            "workspaces.projects.tasks.watch",
            "workspaces.files.read",
            "workspaces.files.write",
            "workspaces.files.share",
            "workspaces.storage.read",
            "workspaces.time.read",
            "workspaces.time.write",
            "workspaces.time.delete",
            "workspaces.time.submit",
            "workspaces.time.approve",
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
            "org.read",
            "members.read",
            "teams.read",
            "workspaces.read",
            "workspaces.projects.read",
            "workspaces.projects.tasks.read",
            "workspaces.files.read",
            "workspaces.time.read",
        ],
        "is_system": True,
        "description": "Базовый доступ",
        "scope": "org",
    },
]
