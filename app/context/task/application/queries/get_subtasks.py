from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.dto.task_dto import TaskListDTO
from app.context.task.application.queries.get_task import _map_task_to_dto
from app.context.task.domain.repositories.task_repository import TaskRepository


class GetSubtasksQuery(BaseQuery):
    """
    Запрос подзадач.

    Атрибуты:
        parent_task_id: ID родительской задачи.
    """

    parent_task_id: str


class GetSubtasksHandler(BaseQueryHandler[GetSubtasksQuery, TaskListDTO]):
    """Обработчик получения подзадач."""

    def __init__(self, task_repo: TaskRepository) -> None:
        super().__init__()
        self._task_repo = task_repo

    async def handle(self, query: GetSubtasksQuery) -> TaskListDTO:
        tasks = await self._task_repo.get_subtasks(Id.from_string(query.parent_task_id))
        items = [_map_task_to_dto(t) for t in tasks]
        return TaskListDTO(items=items, total=len(items))
