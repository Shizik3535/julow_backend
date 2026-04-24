from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.dto.task_dto import TaskListDTO
from app.context.task.application.queries.get_task import _map_task_to_dto
from app.context.task.domain.repositories.task_repository import TaskRepository


class GetTasksByReporterQuery(BaseQuery):
    """
    Запрос задач по автору.

    Атрибуты:
        user_id: ID автора.
    """

    user_id: str


class GetTasksByReporterHandler(BaseQueryHandler[GetTasksByReporterQuery, TaskListDTO]):
    """Обработчик получения задач по автору."""

    def __init__(self, task_repo: TaskRepository) -> None:
        super().__init__()
        self._task_repo = task_repo

    async def handle(self, query: GetTasksByReporterQuery) -> TaskListDTO:
        tasks = await self._task_repo.get_by_reporter(Id.from_string(query.user_id))
        items = [_map_task_to_dto(t) for t in tasks]
        return TaskListDTO(items=items, total=len(items))
