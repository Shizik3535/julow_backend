from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.dto.task_dto import TaskListDTO
from app.context.task.application.queries.get_task import _map_task_to_dto
from app.context.task.domain.repositories.task_repository import TaskRepository


class GetTasksByStatusQuery(BaseQuery):
    """
    Запрос задач по workflow-статусу.

    Атрибуты:
        project_id: ID проекта.
        status_id: ID workflow-статуса.
    """

    project_id: str
    status_id: str


class GetTasksByStatusHandler(BaseQueryHandler[GetTasksByStatusQuery, TaskListDTO]):
    """Обработчик получения задач по workflow-статусу."""

    def __init__(self, task_repo: TaskRepository) -> None:
        super().__init__()
        self._task_repo = task_repo

    async def handle(self, query: GetTasksByStatusQuery) -> TaskListDTO:
        tasks = await self._task_repo.get_by_status(
            project_id=Id.from_string(query.project_id),
            status_id=Id.from_string(query.status_id),
        )
        items = [_map_task_to_dto(t) for t in tasks]
        return TaskListDTO(items=items, total=len(items))
