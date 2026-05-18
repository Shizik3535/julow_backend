"""Адаптер CommentTargetAccessPort.

Разрешает проверку доступа к произвольному ``target_type`` через
делегирование в соответствующий BC-провайдер:

* ``TASK``    → TaskProvider → project_id → ProjectPermissionProvider
* ``PROJECT`` → ProjectPermissionProvider напрямую (target_id = project_id)
* ``EPIC``    → EpicProvider → project_id → ProjectPermissionProvider
* ``SPRINT``  → SprintProvider → project_id → ProjectPermissionProvider
* ``MILESTONE`` / ``MEETING`` / ``DOCUMENT`` — пока не поддержаны,
  доступ запрещён (deny-by-default).

Используемое разрешение — ``tasks.read``: любой, кто может читать задачи
проекта, может читать/добавлять комментарии в его контексте. Это совпадает
с трактовкой permissions из ``docs/rbac/project-permissions.md`` и
``docs/rbac/task-permissions.md`` до тех пор, пока в RBAC-доках не
появится отдельный набор ``comments.*`` разрешений.
"""

from __future__ import annotations

from app.context.project.application.ports.integration.outboard.epic_provider import (
    EpicProvider,
)
from app.context.project.application.ports.integration.outboard.project_permission_provider import (
    ProjectPermissionProvider,
)
from app.context.project.application.ports.integration.outboard.project_provider import (
    ProjectProvider,
)
from app.context.project.application.ports.integration.outboard.sprint_provider import (
    SprintProvider,
)
from app.context.task.application.ports.integration.outboard.task_provider import (
    TaskProvider,
)

from app.context.communication.application.exceptions.authorization_exceptions import (
    CommentTargetForbiddenException,
)
from app.context.communication.application.ports.integration.inboard.comment_target_access_port import (
    CommentTargetAccessPort,
)
from app.context.communication.domain.value_objects.comment_target_type import (
    CommentTargetType,
)


# Разрешение, которым гейтятся комментарии. Любой, кто может читать задачи
# проекта (project-, workspace- или org-уровень через каскад), может
# читать и оставлять комментарии в его контексте.
_COMMENT_ACCESS_PERMISSION = "tasks.read"


class CommentTargetAccessAdapter(CommentTargetAccessPort):
    """Реализация ``CommentTargetAccessPort`` через провайдеры Project/Task BC."""

    def __init__(
        self,
        task_provider: TaskProvider,
        epic_provider: EpicProvider,
        sprint_provider: SprintProvider,
        project_permission_provider: ProjectPermissionProvider,
        project_provider: ProjectProvider | None = None,
    ) -> None:
        self._task_provider = task_provider
        self._epic_provider = epic_provider
        self._sprint_provider = sprint_provider
        self._project_permissions = project_permission_provider
        self._project_provider = project_provider

    async def require_access(
        self,
        user_id: str,
        target_type: CommentTargetType,
        target_id: str,
    ) -> None:
        project_id = await self._resolve_project_id(target_type, target_id)
        if project_id is None:
            # Цель существует в неподдержанной BC или не найдена — deny.
            raise CommentTargetForbiddenException(
                target_type=target_type.value,
                target_id=target_id,
                user_id=user_id,
                reason="тип цели не поддержан или сущность не найдена",
            )

        allowed = await self._project_permissions.has_permission(
            user_id=user_id,
            project_id=project_id,
            permission=_COMMENT_ACCESS_PERMISSION,
        )
        if not allowed:
            raise CommentTargetForbiddenException(
                target_type=target_type.value,
                target_id=target_id,
                user_id=user_id,
                reason=f"требуется разрешение «{_COMMENT_ACCESS_PERMISSION}»",
            )

    # ------------------------------------------------------------------

    async def _resolve_project_id(
        self,
        target_type: CommentTargetType,
        target_id: str,
    ) -> str | None:
        """Найти ``project_id``, к которому привязана комментируемая сущность."""
        if target_type == CommentTargetType.PROJECT:
            return target_id
        if target_type == CommentTargetType.TASK:
            task = await self._task_provider.get_task(target_id)
            return task.project_id if task else None
        if target_type == CommentTargetType.EPIC:
            epic = await self._epic_provider.get_epic(target_id)
            return epic.project_id if epic else None
        if target_type == CommentTargetType.SPRINT:
            sprint = await self._sprint_provider.get_sprint(target_id)
            return sprint.project_id if sprint else None
        # MILESTONE / MEETING / DOCUMENT — пока не интегрированы.
        return None

    async def resolve_workspace_id(
        self,
        target_type: CommentTargetType,
        target_id: str,
    ) -> str | None:
        """Резолвинг ``workspace_id`` через цепочку target → project → workspace."""
        project_id = await self._resolve_project_id(target_type, target_id)
        if project_id is None or self._project_provider is None:
            return None
        project = await self._project_provider.get_project(project_id)
        if project is None:
            return None
        workspace_id = getattr(project, "workspace_id", None)
        return str(workspace_id) if workspace_id else None

    async def resolve_project_id(
        self,
        target_type: CommentTargetType,
        target_id: str,
    ) -> str | None:
        """Публичный фасад над ``_resolve_project_id`` для внешних потребителей.

        Нужен, например, для маркировки вложений комментариев тегом
        ``project:<id>`` — UI документов использует этот тег для фильтра
        по проекту.
        """
        return await self._resolve_project_id(target_type, target_id)
