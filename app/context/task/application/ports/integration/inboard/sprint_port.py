from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class SprintPort(ABC):
    """
    Inboard-порт: получение данных спринтов из Project BC (Sprint AR).

    Используется для проверки существования и статуса спринта
    при назначении задачи.
    """

    @abstractmethod
    async def sprint_exists(self, sprint_id: str) -> bool:
        """Проверить существование спринта."""

    @abstractmethod
    async def get_sprint(self, sprint_id: str) -> dict[str, Any] | None:
        """Получить данные спринта."""

    @abstractmethod
    async def get_active_sprint(self, project_id: str) -> dict[str, Any] | None:
        """Получить активный спринт проекта."""
