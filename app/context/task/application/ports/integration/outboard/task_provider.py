from __future__ import annotations

from abc import ABC, abstractmethod

from app.context.task.application.dto.task_dto import TaskDTO


class TaskProvider(ABC):
    """
    Outboard-порт: предоставление данных задач другим BC.

    Communication BC и другие используют для проверки
    существования задачи и получения данных.
    """

    @abstractmethod
    async def task_exists(self, task_id: str) -> bool:
        """Проверить существование задачи."""

    @abstractmethod
    async def get_task(self, task_id: str) -> TaskDTO | None:
        """Получить задачу по ID."""

    @abstractmethod
    async def get_tasks_by_project(self, project_id: str) -> list[TaskDTO]:
        """Получить все задачи проекта."""

    @abstractmethod
    async def count_by_project(self, project_id: str) -> int:
        """Подсчитать количество задач в проекте."""
