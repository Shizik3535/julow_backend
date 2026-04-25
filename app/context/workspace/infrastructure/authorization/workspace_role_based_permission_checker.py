from __future__ import annotations

from app.context.workspace.application.exceptions.authorization_exceptions import (
    InsufficientWorkspacePermissionsException,
)
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.application.ports.integration.inboard.organization_permission_checker_port import (
    OrganizationPermissionCheckerPort,
)
from app.context.workspace.domain.repositories.workspace_membership_repository import (
    WorkspaceMembershipRepository,
)
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository
from app.context.workspace.domain.repositories.workspace_role_repository import WorkspaceRoleRepository
from app.shared.domain.value_objects.id_vo import Id


class WorkspaceRoleBasedPermissionChecker(WorkspacePermissionCheckerPort):
    """
    Проверка разрешений на основе workspace-роли пользователя
    с каскадированием орг-роли.

    Порядок проверки:
        1. Workspace-роль (прямой участник) — если пользователь есть в
           WorkspaceMembership и его роль даёт нужное разрешение → True.
        2. Орг-роль (каскад) — если workspace принадлежит организации,
           проверяется орг-разрешение вида «workspaces.<ws-permission>».
        3. Иначе → False.

    Поддерживаемые wildcard-шаблоны (workspace-уровень):
        - «ws.*» — полный доступ в workspace
        - «<group>.*» — все разрешения в группе
        - точное совпадение

    Маппинг каскада OrgRole → Workspace:
        workspace-разрешение `P` → орг-разрешение `workspaces.P`.
        Специальный случай: `ws.*` → `workspaces.*`.
    """

    def __init__(
        self,
        membership_repo: WorkspaceMembershipRepository,
        workspace_role_repo: WorkspaceRoleRepository,
        ws_repo: WorkspaceRepository,
        org_permission_checker: OrganizationPermissionCheckerPort,
    ) -> None:
        self._membership_repo = membership_repo
        self._workspace_role_repo = workspace_role_repo
        self._ws_repo = ws_repo
        self._org_permission_checker = org_permission_checker

    async def has_permission(self, user_id: Id, workspace_id: Id, permission: str) -> bool:
        # 1. Проверка через workspace-роль (прямой участник).
        if await self._has_workspace_permission(user_id, workspace_id, permission):
            return True

        # 2. Каскад: проверка через орг-роль, если workspace привязан к организации.
        workspace = await self._ws_repo.get_by_id(workspace_id)
        if workspace is None or workspace.organization_id is None:
            return False

        org_permission = self._map_to_org_permission(permission)
        return await self._org_permission_checker.has_permission(
            user_id=str(user_id),
            org_id=str(workspace.organization_id),
            permission=org_permission,
        )

    async def require_permission(self, user_id: Id, workspace_id: Id, permission: str) -> None:
        if not await self.has_permission(user_id, workspace_id, permission):
            raise InsufficientWorkspacePermissionsException(permission, str(workspace_id))

    # --- Вспомогательные методы ---

    async def _has_workspace_permission(
        self, user_id: Id, workspace_id: Id, permission: str
    ) -> bool:
        member = await self._membership_repo.get_member_by_workspace_and_user(
            workspace_id, user_id
        )
        if member is None or not member.is_active:
            return False

        role = await self._workspace_role_repo.get_by_id(member.role_id)
        if role is None:
            return False

        return self._permission_grants(role.permissions, permission)

    @staticmethod
    def _map_to_org_permission(ws_permission: str) -> str:
        """
        Маппит workspace-разрешение в эквивалент на уровне орг-роли.

        Примеры:
            «ws.*»               → «workspaces.*»
            «members.write»      → «workspaces.members.write»
            «roles.*»            → «workspaces.roles.*»
            «ws.settings.write»  → «workspaces.settings.write»
        """
        if ws_permission == "ws.*":
            return "workspaces.*"
        if ws_permission.startswith("ws."):
            # «ws.settings.write» → «workspaces.settings.write»
            return f"workspaces.{ws_permission[3:]}"
        return f"workspaces.{ws_permission}"

    @staticmethod
    def _permission_grants(permissions: list[str], required: str) -> bool:
        """
        Проверяет, покрывает ли список разрешений требуемое.

        Правила:
            - «group.*» покрывает «group.anything»
            - точное совпадение строки
        """
        for perm in permissions:
            if perm == required:
                return True
            if perm.endswith(".*"):
                prefix = perm[:-1]  # «group.»
                if required.startswith(prefix):
                    return True
        return False
