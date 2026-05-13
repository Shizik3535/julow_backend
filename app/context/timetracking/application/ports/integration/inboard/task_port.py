from __future__ import annotations

from abc import ABC, abstractmethod


class TaskPort(ABC):
    """
    Inboard-порт: получение данных задачи из Task BC.

    TimeTracking BC использует для проверки существования задачи
    при привязке записи времени.
    """

    @abstractmethod
    async def task_exists(self, task_id: str) -> bool:
        """Проверить существование задачи."""

    @abstractmethod
    async def get_task_project_id(self, task_id: str) -> str | None:
        """Получить project_id задачи (для каскадной привязки)."""
