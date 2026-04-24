from __future__ import annotations

from uuid import UUID


SYSTEM_ROLES: list[dict[str, object]] = [
    {
        "id": UUID("00000000-0000-0000-0000-000000000001"),
        "name": "super_admin",
        "permissions": ["*"],
        "is_system": True,
        "description": "Полный доступ",
    },
    {
        "id": UUID("00000000-0000-0000-0000-000000000002"),
        "name": "admin",
        "permissions": ["users.*", "content.*", "settings.*"],
        "is_system": True,
        "description": "Управление пользователями и контентом",
    },
    {
        "id": UUID("00000000-0000-0000-0000-000000000003"),
        "name": "supporter",
        "permissions": ["users.read", "users.support", "content.read"],
        "is_system": True,
        "description": "Ограниченные права поддержки",
    },
    {
        "id": UUID("00000000-0000-0000-0000-000000000004"),
        "name": "user",
        "permissions": ["self.*"],
        "is_system": True,
        "description": "Базовый доступ к собственным данным",
    },
]
