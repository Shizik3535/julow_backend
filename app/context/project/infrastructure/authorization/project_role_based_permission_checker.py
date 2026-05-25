from __future__ import annotations

from app.context.project.application.exceptions.authorization_exceptions import (
    InsufficientProjectPermissionsException,
)
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)
from app.context.project.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.project.domain.repositories.project_membership_repository import (
    ProjectMembershipRepository,
)
from app.context.project.domain.repositories.project_repository import ProjectRepository
from app.context.project.domain.repositories.project_role_repository import ProjectRoleRepository
from app.shared.domain.value_objects.id_vo import Id


class ProjectRoleBasedPermissionChecker(ProjectPermissionCheckerPort):
    """
    Проверка разрешений на основе project-роли пользователя
    с каскадированием в workspace-роль и орг-роль.

    Порядок проверки:
        1. Project-роль (прямой участник) — если пользователь активен в
           ProjectMembership и его роль даёт нужное разрешение → True.
        2. Workspace-роль (каскад) — если у проекта есть workspace_id,
           проверяется workspace-разрешение вида «projects.<project-permission>»
           (спец-случай: «project.*» → «ws.projects.*»).
        3. Workspace-чекер сам каскадирует в орг-роль
           («workspaces.<ws-permission>»), доп. логики не требуется.

    Поддерживаемые wildcard-шаблоны (project-уровень):
        - «project.*» — полный доступ в проекте
        - «<group>.*» — все разрешения в группе
        - точное совпадение

    Маппинг каскада Project → Workspace:
        project-разрешение `P` → workspace-разрешение `projects.P`.
        Специальный случай: `project.*` → `ws.projects.*`.
    """

    def __init__(
        self,
        membership_repo: ProjectMembershipRepository,
        project_role_repo: ProjectRoleRepository,
        project_repo: ProjectRepository,
        workspace_permission_checker: WorkspacePermissionCheckerPort,
    ) -> None:
        self._membership_repo = membership_repo
        self._project_role_repo = project_role_repo
        self._project_repo = project_repo
        self._workspace_permission_checker = workspace_permission_checker

    async def has_permission(self, user_id: Id, project_id: Id, permission: str) -> bool:
        # 1. Проверка через project-роль (прямой участник).
        if await self._has_project_permission(user_id, project_id, permission):
            return True

        # 2. Каскад: проверка через workspace-роль
        # (workspace-чекер каскадирует дальше в орг-роль).
        project = await self._project_repo.get_by_id(project_id)
        if project is None or project.workspace_id is None:
            return False

        ws_permission = self._map_to_ws_permission(permission)
        return await self._workspace_permission_checker.has_permission(
            user_id=str(user_id),
            workspace_id=str(project.workspace_id),
            permission=ws_permission,
        )

    async def require_permission(self, user_id: Id, project_id: Id, permission: str) -> None:
        if not await self.has_permission(user_id, project_id, permission):
            raise InsufficientProjectPermissionsException(permission, str(project_id))

    # --- Вспомогательные методы ---

    async def _has_project_permission(
        self, user_id: Id, project_id: Id, permission: str
    ) -> bool:
        project = await self._project_repo.get_by_id(project_id)
        if project is not None and any(owner_id == user_id for owner_id in project.owner_ids):
            return True

        member = await self._membership_repo.get_member_by_project_and_user(
            project_id, user_id
        )
        if member is None or not member.is_active:
            return False

        role = await self._project_role_repo.get_by_id(member.role_id)
        if role is None:
            return False

        return self._permission_grants(role.permissions, permission)

    @staticmethod
    def _map_to_ws_permission(project_permission: str) -> str:
        """
        Маппит project-разрешение в эквивалент на уровне workspace-роли.

        Примеры:
            «project.*»        → «ws.projects.*»
            «tasks.read»       → «projects.tasks.read»
            «members.write»    → «projects.members.write»
            «workflow.*»       → «projects.workflow.*»
        """
        if project_permission == "project.*":
            return "ws.projects.*"
        if project_permission.startswith("project."):
            # «project.settings.write» → «projects.settings.write»
            return f"projects.{project_permission[len('project.'):]}"
        return f"projects.{project_permission}"

    @staticmethod
    def _permission_grants(permissions: list[str], required: str) -> bool:
        """
        Проверяет, покрывает ли список разрешений требуемое.

        Правила:
            - «project.*» покрывает всё
            - «group.*» покрывает «group.anything»
            - точное совпадение строки
        """
        for perm in permissions:
            if perm == "project.*":
                return True
            if perm == required:
                return True
            if perm.endswith(".*"):
                prefix = perm[:-1]  # «group.»
                if required.startswith(prefix):
                    return True
        return False
