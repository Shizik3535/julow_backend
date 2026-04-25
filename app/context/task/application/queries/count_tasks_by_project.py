from __future__ import annotations

from app.shared.application.base_dto import BaseDTO
from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.ports.authorization.task_permission_checker_port import (
    TaskPermissionCheckerPort,
)
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

    caller_id: str
    project_id: str


class CountTasksByProjectHandler(BaseQueryHandler[CountTasksByProjectQuery, TaskCountDTO]):
    """Обработчик подсчёта задач проекта."""

    REQUIRED_PERMISSION = "tasks.read"

    def __init__(self, task_repo: TaskRepository, permission_checker: TaskPermissionCheckerPort) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._permission_checker = permission_checker

    async def handle(self, query: CountTasksByProjectQuery) -> TaskCountDTO:
        await self._permission_checker.require_permission(
            user_id=query.caller_id,
            project_id=query.project_id,
            permission=self.REQUIRED_PERMISSION,
        )
        count = await self._task_repo.count_by_project(Id.from_string(query.project_id))
        return TaskCountDTO(count=count)
