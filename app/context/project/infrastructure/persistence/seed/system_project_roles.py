"""
Seed-данные для системных ролей проекта (Project BC).

Глобальные системные роли (project_id IS NULL) — доступны
во всех проектах как шаблоны.

Используется в:
    - scripts/seed_project_roles.py
    - app/context/project/application/commands/create_project.py
    - tests/integration/conftest.py
    - tests/e2e/conftest.py

Соответствуют спецификации §5.7 (docs/domain-spec/05-project.md).
"""
from __future__ import annotations

from uuid import UUID


SYSTEM_PROJECT_ROLES: list[dict[str, object]] = [
    {
        "id": UUID("00000000-0000-0000-0003-000000000001"),
        "project_id": None,
        "name": "owner",
        "permissions": ["project.*"],
        "is_system": True,
        "description": "Полный доступ, управление владельцами",
    },
    {
        "id": UUID("00000000-0000-0000-0003-000000000002"),
        "project_id": None,
        "name": "admin",
        "permissions": [
            "project.read",
            "project.settings.*",
            "members.*",
            "roles.*",
            "workflow.*",
            "views.*",
            "automations.*",
            "custom_fields.*",
            "tasks.*",
        ],
        "is_system": True,
        "description": "Управление проектом",
    },
    {
        "id": UUID("00000000-0000-0000-0003-000000000003"),
        "project_id": None,
        "name": "manager",
        "permissions": [
            "project.read",
            "members.read",
            "roles.read",
            "workflow.*",
            "sprints.*",
            "epics.*",
            "milestones.*",
            "views.read",
            "tasks.*",
        ],
        "is_system": True,
        "description": "Управление процессами",
    },
    {
        "id": UUID("00000000-0000-0000-0003-000000000004"),
        "project_id": None,
        "name": "member",
        "permissions": [
            "project.read",
            "members.read",
            "roles.read",
            "sprints.read",
            "views.read",
            "tasks.create",
            "tasks.read",
            "tasks.update",
            "tasks.assign",
            "tasks.watch",
        ],
        "is_system": True,
        "description": "Работа с задачами",
    },
    {
        "id": UUID("00000000-0000-0000-0003-000000000005"),
        "project_id": None,
        "name": "guest",
        "permissions": [
            "project.read",
            "members.read",
            "roles.read",
            "views.read",
            "tasks.read",
            "tasks.update_own",
            "tasks.update_status",
        ],
        "is_system": True,
        "description": "Просмотр + обновление своих задач",
    },
]
