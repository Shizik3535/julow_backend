from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.dto.task_dto import TaskListDTO
from app.context.task.application.queries.get_task import _map_task_to_dto
from app.context.task.application.ports.authorization.task_permission_checker_port import (
    TaskPermissionCheckerPort,
)
from app.context.task.domain.repositories.task_repository import TaskRepository


class GetSubtasksQuery(BaseQuery):
    """
    Запрос подзадач.

    Атрибуты:
        caller_id: ID пользователя, выполняющего запрос.
        parent_task_id: ID родительской задачи.
    """

    caller_id: str
    parent_task_id: str


class GetSubtasksHandler(BaseQueryHandler[GetSubtasksQuery, TaskListDTO]):
    """Обработчик получения подзадач."""

    REQUIRED_PERMISSION = "tasks.read"

    def __init__(
        self,
        task_repo: TaskRepository,
        permission_checker: TaskPermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetSubtasksQuery) -> TaskListDTO:
        parent_task = await self._task_repo.get_by_id(Id.from_string(query.parent_task_id))
        if parent_task is not None:
            await self._permission_checker.require_permission(
                user_id=query.caller_id,
                project_id=str(parent_task.project_id),
                permission=self.REQUIRED_PERMISSION,
            )

        tasks = await self._task_repo.get_subtasks(Id.from_string(query.parent_task_id))
        items = [_map_task_to_dto(t) for t in tasks]
        return TaskListDTO(items=items, total=len(items))
