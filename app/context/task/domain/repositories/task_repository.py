from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.aggregates.task import Task


class TaskRepository(RepositoryPort[Task]):
    """Порт репозитория для агрегата Task."""

    @abstractmethod
    async def get_by_project(self, project_id: Id) -> list[Task]:
        """Найти задачи по ID проекта."""

    @abstractmethod
    async def get_by_assignee(self, user_id: Id) -> list[Task]:
        """Найти задачи по ID исполнителя."""

    @abstractmethod
    async def get_by_reporter(self, user_id: Id) -> list[Task]:
        """Найти задачи по ID автора."""

    @abstractmethod
    async def get_subtasks(self, parent_task_id: Id) -> list[Task]:
        """Найти подзадачи."""

    @abstractmethod
    async def get_by_sprint(self, sprint_id: Id) -> list[Task]:
        """Найти задачи по ID спринта."""

    @abstractmethod
    async def get_by_epic(self, epic_id: Id) -> list[Task]:
        """Найти задачи по ID эпика."""

    @abstractmethod
    async def get_overdue_tasks(self) -> list[Task]:
        """Найти просроченные задачи."""

    @abstractmethod
    async def get_by_status(self, project_id: Id, status_id: Id) -> list[Task]:
        """Найти задачи по workflow-статусу в рамках проекта."""

    @abstractmethod
    async def get_by_parent(self, parent_task_id: Id) -> list[Task]:
        """Найти дочерние задачи."""

    @abstractmethod
    async def get_by_labels(self, project_id: Id, label_names: list[str]) -> list[Task]:
        """Найти задачи по меткам."""

    @abstractmethod
    async def search(self, offset: int = 0, limit: int = 100, filters: dict[str, Any] | None = None) -> list[Task]:
        """Поиск задач с фильтрацией."""

    @abstractmethod
    async def count_by_project(self, project_id: Id) -> int:
        """Подсчитать количество задач в проекте."""

    @abstractmethod
    async def count_by_status(self, project_id: Id, status_id: Id) -> int:
        """Подсчитать количество задач по workflow-статусу."""

    @abstractmethod
    async def is_participant_in_project(self, project_id: Id, user_id: Id) -> bool:
        """Проверить, является ли пользователь участником задач проекта (assignee, reporter, watcher)."""

    @abstractmethod
    async def is_assignee_in_project(self, project_id: Id, user_id: Id) -> bool:
        """Проверить, является ли пользователь исполнителем хотя бы одной задачи проекта."""
