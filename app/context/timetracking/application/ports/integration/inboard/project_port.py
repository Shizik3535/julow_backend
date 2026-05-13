from __future__ import annotations

from abc import ABC, abstractmethod


class ProjectPort(ABC):
    """
    Inboard-порт: получение данных проекта из Project BC.

    TimeTracking BC использует для проверки существования и активности
    проекта при привязке записи времени.
    """

    @abstractmethod
    async def project_exists(self, project_id: str) -> bool:
        """Проверить существование проекта."""

    @abstractmethod
    async def is_project_active(self, project_id: str) -> bool:
        """Проверить, что проект в активном статусе (не ARCHIVED/SUSPENDED)."""

    @abstractmethod
    async def get_project_workspace_id(self, project_id: str) -> str | None:
        """Получить workspace_id проекта (для согласованности)."""
