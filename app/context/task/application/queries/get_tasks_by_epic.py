from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.dto.task_dto import TaskListDTO
from app.context.task.application.queries.get_task import _map_task_to_dto
from app.context.task.domain.repositories.task_repository import TaskRepository


class GetTasksByEpicQuery(BaseQuery):
    """
    Запрос задач эпика.

    Атрибуты:
        epic_id: ID эпика.
    """

    epic_id: str


class GetTasksByEpicHandler(BaseQueryHandler[GetTasksByEpicQuery, TaskListDTO]):
    """Обработчик получения задач эпика."""

    def __init__(self, task_repo: TaskRepository) -> None:
        super().__init__()
        self._task_repo = task_repo

    async def handle(self, query: GetTasksByEpicQuery) -> TaskListDTO:
        tasks = await self._task_repo.get_by_epic(Id.from_string(query.epic_id))
        items = [_map_task_to_dto(t) for t in tasks]
        return TaskListDTO(items=items, total=len(items))
