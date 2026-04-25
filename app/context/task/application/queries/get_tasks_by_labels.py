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


class GetTasksByLabelsQuery(BaseQuery):
    """
    Запрос задач по меткам.

    Атрибуты:
        project_id: ID проекта.
        label_names: Названия меток.
    """

    caller_id: str
    project_id: str
    label_names: list[str]


class GetTasksByLabelsHandler(BaseQueryHandler[GetTasksByLabelsQuery, TaskListDTO]):
    """Обработчик получения задач по меткам."""

    REQUIRED_PERMISSION = "tasks.read"

    def __init__(
        self,
        task_repo: TaskRepository,
        permission_checker: TaskPermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetTasksByLabelsQuery) -> TaskListDTO:
        await self._permission_checker.require_permission(
            user_id=query.caller_id,
            project_id=query.project_id,
            permission=self.REQUIRED_PERMISSION,
        )
        tasks = await self._task_repo.get_by_labels(
            project_id=Id.from_string(query.project_id),
            label_names=query.label_names,
        )
        items = [_map_task_to_dto(t) for t in tasks]
        return TaskListDTO(items=items, total=len(items))
