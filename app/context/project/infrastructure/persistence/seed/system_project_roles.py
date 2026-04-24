"""
Шаблоны системных ролей проекта (Project BC).

Используются для:
- Создания 5 системных `ProjectRole` при `Project.create` (в CreateProjectHandler).
- Тестовых фикстур.

Соответствуют спецификации §5.7 (docs/domain-spec/05-project.md).
"""
from __future__ import annotations

from app.context.project.domain.aggregates.project_role import ProjectRole
from app.shared.domain.value_objects.id_vo import Id


SYSTEM_PROJECT_ROLES: list[dict[str, object]] = [
    {
        "name": "owner",
        "permissions": ["project.*"],
        "description": "Полный доступ, управление владельцами",
    },
    {
        "name": "admin",
        "permissions": [
            "project.settings.*",
            "members.*",
            "roles.*",
            "workflow.*",
            "views.*",
            "automations.*",
            "custom_fields.*",
            "content.*",
            "tasks.*",
        ],
        "description": "Управление проектом",
    },
    {
        "name": "manager",
        "permissions": [
            "members.read",
            "workflow.*",
            "sprints.*",
            "epics.*",
            "milestones.*",
            "content.*",
            "views.read",
            "tasks.*",
        ],
        "description": "Управление процессами",
    },
    {
        "name": "member",
        "permissions": [
            "content.*",
            "sprints.read",
            "views.read",
            "tasks.create",
            "tasks.read",
            "tasks.update",
            "tasks.assign",
            "tasks.watch",
        ],
        "description": "Работа с задачами",
    },
    {
        "name": "guest",
        "permissions": [
            "content.read",
            "views.read",
            "tasks.read",
        ],
        "description": "Только просмотр",
    },
]


def build_system_project_roles(project_id: Id) -> list[ProjectRole]:
    """
    Создаёт 5 системных ролей для проекта по шаблону `SYSTEM_PROJECT_ROLES`.

    Аргументы:
        project_id: ID проекта, к которому привязываются роли.

    Возвращает:
        Список `ProjectRole` с `is_system=True` и `project_id=<project_id>`.
    """
    roles: list[ProjectRole] = []
    for template in SYSTEM_PROJECT_ROLES:
        role = ProjectRole(
            project_id=project_id,
            name=str(template["name"]),
            permissions=list(template["permissions"]),  # type: ignore[arg-type]
            is_system=True,
            description=template["description"],  # type: ignore[arg-type]
        )
        roles.append(role)
    return roles
