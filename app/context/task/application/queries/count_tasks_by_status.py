from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.queries.count_tasks_by_project import TaskCountDTO
from app.context.task.domain.repositories.task_repository import TaskRepository


class CountTasksByStatusQuery(BaseQuery):
    """
    Запрос счётчика задач по workflow-статусу.

    Атрибуты:
        project_id: ID проекта.
        status_id: ID workflow-статуса.
    """

    project_id: str
    status_id: str


class CountTasksByStatusHandler(BaseQueryHandler[CountTasksByStatusQuery, TaskCountDTO]):
    """Обработчик подсчёта задач по workflow-статусу."""

    def __init__(self, task_repo: TaskRepository) -> None:
        super().__init__()
        self._task_repo = task_repo

    async def handle(self, query: CountTasksByStatusQuery) -> TaskCountDTO:
        count = await self._task_repo.count_by_status(
            project_id=Id.from_string(query.project_id),
            status_id=Id.from_string(query.status_id),
        )
        return TaskCountDTO(count=count)
