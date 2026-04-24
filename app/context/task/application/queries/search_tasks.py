from __future__ import annotations

from typing import Any

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.context.task.application.dto.task_dto import TaskListDTO
from app.context.task.application.queries.get_task import _map_task_to_dto
from app.context.task.domain.repositories.task_repository import TaskRepository


class SearchTasksQuery(BaseQuery):
    """
    Запрос поиска задач с фильтрацией.

    Атрибуты:
        offset: Смещение.
        limit: Лимит.
        filters: Фильтры поиска.
    """

    offset: int = 0
    limit: int = 100
    filters: dict[str, Any] | None = None


class SearchTasksHandler(BaseQueryHandler[SearchTasksQuery, TaskListDTO]):
    """Обработчик поиска задач."""

    def __init__(self, task_repo: TaskRepository) -> None:
        super().__init__()
        self._task_repo = task_repo

    async def handle(self, query: SearchTasksQuery) -> TaskListDTO:
        tasks = await self._task_repo.search(
            offset=query.offset,
            limit=query.limit,
            filters=query.filters,
        )
        items = [_map_task_to_dto(t) for t in tasks]
        return TaskListDTO(items=items, total=len(items))
