from __future__ import annotations

from typing import Any

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.context.task.application.dto.task_dto import TaskListDTO
from app.context.task.application.queries.get_task import _map_task_to_dto
from app.context.task.application.ports.authorization.task_permission_checker_port import (
    TaskPermissionCheckerPort,
)
from app.context.task.domain.repositories.task_repository import TaskRepository


class SearchTasksQuery(BaseQuery):
    """
    Запрос поиска задач с фильтрацией.

    Атрибуты:
        offset: Смещение.
        limit: Лимит.
        filters: Фильтры поиска.
        sort_by: Поле сортировки.
        sort_order: Порядок сортировки (asc/desc).
    """

    caller_id: str
    project_id: str | None = None
    offset: int = 0
    limit: int = 100
    filters: dict[str, Any] | None = None
    sort_by: str | None = None
    sort_order: str = "asc"


class SearchTasksHandler(BaseQueryHandler[SearchTasksQuery, TaskListDTO]):
    """Обработчик поиска задач."""

    REQUIRED_PERMISSION = "tasks.read"

    def __init__(self, 
        task_repo: TaskRepository, 
        permission_checker: TaskPermissionCheckerPort
    ) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._permission_checker = permission_checker

    async def handle(self, query: SearchTasksQuery) -> TaskListDTO:
        if query.project_id is not None:
            await self._permission_checker.require_permission(
                user_id=query.caller_id,
                project_id=query.project_id,
                permission=self.REQUIRED_PERMISSION,
            )
            tasks = await self._task_repo.search(
                offset=query.offset,
                limit=query.limit,
                filters=query.filters,
                sort_by=query.sort_by,
                sort_order=query.sort_order,
            )
            tasks = [t for t in tasks if str(t.project_id) == query.project_id]
        else:
            tasks = await self._task_repo.search(
                offset=query.offset,
                limit=query.limit,
                filters=query.filters,
                sort_by=query.sort_by,
                sort_order=query.sort_order,
            )
            caller_uuid = query.caller_id
            tasks = [
                t for t in tasks
                if caller_uuid in [str(a) for a in t.assignee_ids]
                or str(t.reporter_id) == caller_uuid
                or caller_uuid in [str(w.user_id) for w in t.watchers]
            ]

        items = [_map_task_to_dto(t) for t in tasks]
        return TaskListDTO(items=items, total=len(items))
