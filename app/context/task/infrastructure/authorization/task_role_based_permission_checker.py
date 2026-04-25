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
        1. Task-level: если пользователь является участником задач проекта
           (assignee, reporter, watcher), то разрешения из
           _TASK_PARTICIPANT_PERMISSIONS предоставляются без project-роли.
        2. Project membership: если пользователь является участником проекта
           (через ProjectMembershipPort), делегируется в ProjectPermissionProvider.
        3. Cascade: ProjectPermissionProvider инкапсулирует каскад
           ProjectRole → WorkspaceRole → OrgRole.

    Поддерживаемые wildcard-шаблоны (project-уровень):
        - «tasks.*» — полный доступ к задачам проекта
        - «<group>.*» — все разрешения в группе
        - точное совпадение
    """

    _TASK_PARTICIPANT_PERMISSIONS = frozenset({"tasks.read", "tasks.watch"})

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
        # 1. Task-level check: участник задачи получает ограниченный доступ.
        if permission in self._TASK_PARTICIPANT_PERMISSIONS:
            is_participant = await self._task_repo.is_participant_in_project(
                project_id=Id.from_string(project_id),
                user_id=Id.from_string(user_id),
            )
            if is_participant:
                return True

        # 2. Project membership check + cascade в Project BC.
        return await self._project_permission_provider.has_permission(
            user_id=user_id,
            project_id=project_id,
            permission=permission,
        )

    async def require_permission(self, user_id: str, project_id: str, permission: str) -> None:
        if not await self.has_permission(user_id=user_id, project_id=project_id, permission=permission):
            raise InsufficientTaskPermissionsException(
                permission=permission,
                project_id=project_id,
                user_id=user_id,
            )
