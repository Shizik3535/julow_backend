from __future__ import annotations

from app.shared.application.base_dto import BaseDTO
from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.repositories.task_repository import TaskRepository


class TaskCountDTO(BaseDTO):
    """DTO счётчика задач."""

    count: int


class CountTasksByProjectQuery(BaseQuery):
    """
    Запрос счётчика задач проекта.

    Атрибуты:
        project_id: ID проекта.
    """

    project_id: str


class CountTasksByProjectHandler(BaseQueryHandler[CountTasksByProjectQuery, TaskCountDTO]):
    """Обработчик подсчёта задач проекта."""

    def __init__(self, task_repo: TaskRepository) -> None:
        super().__init__()
        self._task_repo = task_repo

    async def handle(self, query: CountTasksByProjectQuery) -> TaskCountDTO:
        count = await self._task_repo.count_by_project(Id.from_string(query.project_id))
        return TaskCountDTO(count=count)
