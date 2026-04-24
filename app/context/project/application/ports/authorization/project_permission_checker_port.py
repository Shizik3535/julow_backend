from __future__ import annotations

from abc import ABC, abstractmethod

from app.shared.domain.value_objects.id_vo import Id


class ProjectPermissionCheckerPort(ABC):
    """
    Порт проверки разрешений пользователя в контексте проекта (Project BC).

    Проверяет, обладает ли пользователь указанным разрешением на основе его
    project-роли, а также каскадно через workspace-роль и орг-роль
    (если workspace привязан к организации).

    Поддерживаемые wildcard-шаблоны:
        - «project.*» — полный доступ в проекте
        - «<group>.*» — все разрешения в группе (members.*, workflow.*, ...)
        - «content.read» — конкретное разрешение

    Каскад ProjectRole → WorkspaceRole → OrgRole:
        Если у пользователя нет прямой project-роли, или она не покрывает
        требуемое разрешение, проверяется workspace-разрешение вида
        «projects.<perm>» (спец-случай: «project.*» → «ws.projects.*»).
        Workspace-чекер каскадирует дальше в орг-роль
        «workspaces.<ws-perm>».
    """

    @abstractmethod
    async def has_permission(self, user_id: Id, project_id: Id, permission: str) -> bool:
        """
        Проверяет, есть ли у пользователя указанное разрешение в проекте.

        Аргументы:
            user_id: Идентификатор пользователя.
            project_id: Идентификатор проекта.
            permission: Требуемое разрешение (например «content.read»).

        Возвращает:
            True, если разрешение есть (через project/workspace/org-роль), иначе False.
        """

    @abstractmethod
    async def require_permission(self, user_id: Id, project_id: Id, permission: str) -> None:
        """
        Проверяет разрешение и выбрасывает исключение при отсутствии.

        Аргументы:
            user_id: Идентификатор пользователя.
            project_id: Идентификатор проекта.
            permission: Требуемое разрешение.

        Raises:
            InsufficientProjectPermissionsException: Если разрешение отсутствует.
        """
