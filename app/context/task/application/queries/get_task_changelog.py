from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.dto.changelog_entry_dto import ChangelogEntryDTO, ChangelogListDTO
from app.context.task.application.ports.authorization.task_permission_checker_port import (
    TaskPermissionCheckerPort,
)
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.repositories.changelog_repository import ChangelogRepository
from app.context.task.domain.repositories.task_repository import TaskRepository


class GetTaskChangelogQuery(BaseQuery):
    """
    Запрос истории изменений задачи.

    Атрибуты:
        task_id: ID задачи.
        offset: Смещение.
        limit: Лимит.
    """

    caller_id: str
    task_id: str
    offset: int = 0
    limit: int = 50


class GetTaskChangelogHandler(BaseQueryHandler[GetTaskChangelogQuery, ChangelogListDTO]):
    """Обработчик получения истории изменений задачи."""

    REQUIRED_PERMISSION = "tasks.read"

    def __init__(self, changelog_repo: ChangelogRepository, task_repo: TaskRepository, permission_checker: TaskPermissionCheckerPort) -> None:
        super().__init__()
        self._changelog_repo = changelog_repo
        self._task_repo = task_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetTaskChangelogQuery) -> ChangelogListDTO:
        task = await self._task_repo.get_by_id(Id.from_string(query.task_id))
        if task is None:
            raise TaskNotFoundException(id=query.task_id)
        await self._permission_checker.require_permission(
            user_id=query.caller_id,
            project_id=str(task.project_id),
            permission=self.REQUIRED_PERMISSION,
        )

        entries = await self._changelog_repo.get_by_task_id(
            task_id=Id.from_string(query.task_id),
            offset=query.offset,
            limit=query.limit,
        )
        total = await self._changelog_repo.count_by_task(Id.from_string(query.task_id))
        items = [
            ChangelogEntryDTO(
                id=str(e.id),
                task_id=str(e.task_id),
                field_name=e.field_name,
                old_value=e.old_value,
                new_value=e.new_value,
                changed_by=str(e.changed_by),
                changed_at=e.changed_at,
            )
            for e in entries
        ]
        return ChangelogListDTO(items=items, total=total)
