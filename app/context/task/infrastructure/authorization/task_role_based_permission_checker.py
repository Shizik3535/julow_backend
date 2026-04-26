from __future__ import annotations

from app.context.project.application.ports.integration.outboard.project_permission_provider import (
    ProjectPermissionProvider,
)
from app.context.task.application.exceptions.authorization_exceptions import (
    InsufficientTaskPermissionsException,
)
from app.context.task.application.ports.authorization.task_permission_checker_port import (
    TaskPermissionCheckerPort,
)
from app.context.task.application.ports.integration.inboard.project_membership_port import (
    ProjectMembershipPort,
)
from app.context.task.domain.repositories.task_repository import TaskRepository
from app.shared.domain.value_objects.id_vo import Id


class TaskRoleBasedPermissionChecker(TaskPermissionCheckerPort):
    """
    Проверка разрешений на основе участия в задачах проекта
    с каскадированием в Project BC.

    Порядок проверки:
        1. Task-level (participant): если пользователь является участником задач проекта
           (assignee, reporter, watcher), то разрешения из
           _TASK_PARTICIPANT_PERMISSIONS предоставляются без project-роли.
        2. Task-level (assignee-only): если пользователь является исполнителем
           задач проекта, то разрешения из _TASK_ASSIGNEE_PERMISSIONS
           предоставляются без project-роли.
        3. Project membership: если пользователь является участником проекта
           (через ProjectMembershipPort), делегируется в ProjectPermissionProvider.
        4. Cascade: ProjectPermissionProvider инкапсулирует каскад
           ProjectRole → WorkspaceRole → OrgRole.

    Поддерживаемые wildcard-шаблоны (project-уровень):
        - «tasks.*» — полный доступ к задачам проекта
        - «<group>.*» — все разрешения в группе
        - точное совпадение
    """

    _TASK_PARTICIPANT_PERMISSIONS = frozenset({"tasks.read", "tasks.watch"})
    _TASK_ASSIGNEE_PERMISSIONS = frozenset({"tasks.update_own", "tasks.update_status"})

    # Покрытие разрешений: tasks.update покрывает tasks.update_own и tasks.update_status.
    # Это гарантирует, что проектная роль с tasks.update по-прежнему даёт доступ
    # к гранулярным операциям assignee.
    _PERMISSION_COVERAGE: dict[str, tuple[str, ...]] = {
        "tasks.update_own": ("tasks.update",),
        "tasks.update_status": ("tasks.update",),
    }

    def __init__(
        self,
        task_repo: TaskRepository,
        project_membership_port: ProjectMembershipPort,
        project_permission_provider: ProjectPermissionProvider,
    ) -> None:
        self._task_repo = task_repo
        self._project_membership_port = project_membership_port
        self._project_permission_provider = project_permission_provider

    async def has_permission(self, user_id: str, project_id: str, permission: str) -> bool:
        # 1. Task-level check: любой участник (assignee, reporter, watcher).
        if permission in self._TASK_PARTICIPANT_PERMISSIONS:
            is_participant = await self._task_repo.is_participant_in_project(
                project_id=Id.from_string(project_id),
                user_id=Id.from_string(user_id),
            )
            if is_participant:
                return True

        # 2. Task-level check: только assignee.
        if permission in self._TASK_ASSIGNEE_PERMISSIONS:
            is_assignee = await self._task_repo.is_assignee_in_project(
                project_id=Id.from_string(project_id),
                user_id=Id.from_string(user_id),
            )
            if is_assignee:
                return True

        # 3. Project membership check + cascade в Project BC.
        if await self._project_permission_provider.has_permission(
            user_id=user_id,
            project_id=project_id,
            permission=permission,
        ):
            return True

        # 4. Покрытие: проверяем, покрывается ли разрешение более широким
        #    (например, tasks.update покрывает tasks.update_own).
        for cover_perm in self._PERMISSION_COVERAGE.get(permission, ()):
            if await self._project_permission_provider.has_permission(
                user_id=user_id,
                project_id=project_id,
                permission=cover_perm,
            ):
                return True

        return False

    async def require_permission(self, user_id: str, project_id: str, permission: str) -> None:
        if not await self.has_permission(user_id=user_id, project_id=project_id, permission=permission):
            raise InsufficientTaskPermissionsException(
                permission=permission,
                project_id=project_id,
                user_id=user_id,
            )
