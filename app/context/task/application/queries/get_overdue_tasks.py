from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.context.task.application.dto.task_dto import TaskListDTO
from app.context.task.application.queries.get_task import _map_task_to_dto
from app.context.task.domain.repositories.task_repository import TaskRepository


class GetOverdueTasksQuery(BaseQuery):
    """Запрос просроченных задач."""

    pass


class GetOverdueTasksHandler(BaseQueryHandler[GetOverdueTasksQuery, TaskListDTO]):
    """Обработчик получения просроченных задач."""

    def __init__(self, task_repo: TaskRepository) -> None:
        super().__init__()
        self._task_repo = task_repo

    async def handle(self, query: GetOverdueTasksQuery) -> TaskListDTO:
        tasks = await self._task_repo.get_overdue_tasks()
        items = [_map_task_to_dto(t) for t in tasks]
        return TaskListDTO(items=items, total=len(items))
