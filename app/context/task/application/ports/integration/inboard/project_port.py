from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ProjectPort(ABC):
    """
    Inboard-порт: получение данных проекта из Project BC.

    Используется для проверки существования, статуса проекта,
    валидации кастомных полей (CustomFieldDefinition).
    """

    @abstractmethod
    async def project_exists(self, project_id: str) -> bool:
        """Проверить существование проекта."""

    @abstractmethod
    async def get_project(self, project_id: str) -> dict[str, Any] | None:
        """Получить данные проекта."""

    @abstractmethod
    async def is_project_active(self, project_id: str) -> bool:
        """Проверить, что проект в активном статусе (не ARCHIVED/SUSPENDED)."""
