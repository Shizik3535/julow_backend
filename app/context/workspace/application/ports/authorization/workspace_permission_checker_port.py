from __future__ import annotations

from abc import ABC, abstractmethod

from app.shared.domain.value_objects.id_vo import Id


class WorkspacePermissionCheckerPort(ABC):
    """
    Порт проверки разрешений пользователя в контексте workspace (Workspace BC).

    Проверяет, обладает ли пользователь указанным разрешением
    на основе его workspace-роли, а также каскадно через орг-роль
    (если workspace принадлежит организации).

    Поддерживаемые wildcard-шаблоны:
        - «ws.*» — полный доступ в workspace
        - «members.*» / «roles.*» / «teams.*» / «ws.settings.*» — группы
        - «members.write» — конкретное разрешение

    Каскад OrgRole → Workspace:
        Если workspace принадлежит организации, орг-разрешения вида
        «workspaces.<group>.<action>» дают те же права, что и
        соответствующие workspace-разрешения (например, орг-роль
        с «workspaces.members.read» покрывает «members.read» в workspace).
    """

    @abstractmethod
    async def has_permission(self, user_id: Id, workspace_id: Id, permission: str) -> bool:
        """
        Проверяет, есть ли у пользователя указанное разрешение в workspace.

        Аргументы:
            user_id: Идентификатор пользователя.
            workspace_id: Идентификатор workspace.
            permission: Требуемое разрешение (например «members.write»).

        Возвращает:
            True, если разрешение есть (через workspace-роль или орг-роль), иначе False.
        """

    @abstractmethod
    async def require_permission(self, user_id: Id, workspace_id: Id, permission: str) -> None:
        """
        Проверяет разрешение и выбрасывает исключение при отсутствии.

        Аргументы:
            user_id: Идентификатор пользователя.
            workspace_id: Идентификатор workspace.
            permission: Требуемое разрешение.

        Raises:
            InsufficientWorkspacePermissionsException: Если разрешение отсутствует.
        """
