from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.context.task.application.dto.task_dto import TaskListDTO
from app.context.task.application.queries.get_task import _map_task_to_dto
from app.context.task.application.ports.authorization.task_permission_checker_port import (
    TaskPermissionCheckerPort,
)
from app.context.task.domain.repositories.task_repository import TaskRepository


class GetOverdueTasksQuery(BaseQuery):
    """Запрос просроченных задач.

    Атрибуты:
        caller_id: ID пользователя, выполняющего запрос.
        project_id: ID проекта (опционально).
    """

    caller_id: str
    project_id: str | None = None


class GetOverdueTasksHandler(BaseQueryHandler[GetOverdueTasksQuery, TaskListDTO]):
    """Обработчик получения просроченных задач."""

    REQUIRED_PERMISSION = "tasks.read"

    def __init__(
        self,
        task_repo: TaskRepository,
        permission_checker: TaskPermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetOverdueTasksQuery) -> TaskListDTO:
        if query.project_id is not None:
            await self._permission_checker.require_permission(
                user_id=query.caller_id,
                project_id=query.project_id,
                permission=self.REQUIRED_PERMISSION,
            )
            tasks = await self._task_repo.get_overdue_tasks()
            tasks = [t for t in tasks if str(t.project_id) == query.project_id]
        else:
            tasks = await self._task_repo.get_overdue_tasks()
            caller_uuid = query.caller_id
            tasks = [
                t for t in tasks
                if caller_uuid in [str(a) for a in t.assignee_ids]
                or str(t.reporter_id) == caller_uuid
                or caller_uuid in [str(w.user_id) for w in t.watchers]
            ]

        items = [_map_task_to_dto(t) for t in tasks]
        return TaskListDTO(items=items, total=len(items))
