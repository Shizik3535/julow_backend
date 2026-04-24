from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class EpicPort(ABC):
    """
    Inboard-порт: получение данных эпиков из Project BC (Epic AR).

    Используется для проверки существования и статуса эпика
    при привязке задачи.
    """

    @abstractmethod
    async def epic_exists(self, epic_id: str) -> bool:
        """Проверить существование эпика."""

    @abstractmethod
    async def get_epic(self, epic_id: str) -> dict[str, Any] | None:
        """Получить данные эпика."""
