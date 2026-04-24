"""
Шаблоны системных ролей workspace (Workspace BC).

Используются для создания 4 системных `WorkspaceRole` при `Workspace.create`.
Включают права на уровне проектов (`projects.*`), чтобы workspace-роли
корректно покрывали каскад Project → Workspace.
"""
from __future__ import annotations

from app.context.workspace.domain.aggregates.workspace_role import WorkspaceRole
from app.shared.domain.value_objects.id_vo import Id


SYSTEM_WORKSPACE_ROLES: list[dict[str, object]] = [
    {
        "name": "owner",
        # «ws.*» уже покрывает «ws.projects.*» + «projects.*» через wildcard.
        "permissions": ["ws.*"],
        "description": "Полный доступ к workspace и всем проектам",
    },
    {
        "name": "admin",
        "permissions": [
            "ws.settings.*",
            "members.*",
            "roles.*",
            "teams.*",
            "projects.*",
            "ws.projects.*",
            "projects.tasks.*",
        ],
        "description": "Управление workspace и проектами",
    },
    {
        "name": "manager",
        "permissions": [
            "members.read",
            "teams.*",
            "projects.read",
            "projects.members.*",
            "projects.content.*",
            "projects.workflow.read",
            "projects.tasks.*",
        ],
        "description": "Управление командами и процессами проектов",
    },
    {
        "name": "member",
        "permissions": [
            "members.read",
            "projects.read",
            "projects.content.*",
            "projects.tasks.read",
            "projects.tasks.create",
            "projects.tasks.update",
            "projects.tasks.assign",
            "projects.tasks.watch",
        ],
        "description": "Базовый доступ к workspace и проектам",
    },
]


def build_system_workspace_roles(workspace_id: Id) -> list[WorkspaceRole]:
    """
    Создаёт 4 системные роли для workspace по шаблону `SYSTEM_WORKSPACE_ROLES`.

    Аргументы:
        workspace_id: ID workspace, к которому привязываются роли.

    Возвращает:
        Список `WorkspaceRole` с `is_system=True`.
    """
    roles: list[WorkspaceRole] = []
    for template in SYSTEM_WORKSPACE_ROLES:
        role = WorkspaceRole(
            workspace_id=workspace_id,
            name=str(template["name"]),
            permissions=list(template["permissions"]),  # type: ignore[arg-type]
            is_system=True,
            description=template["description"],  # type: ignore[arg-type]
        )
        roles.append(role)
    return roles
