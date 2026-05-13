from __future__ import annotations

from abc import ABC, abstractmethod


class ProjectPort(ABC):
    """Inboard-порт: проверки проектов из Project BC."""

    @abstractmethod
    async def project_exists(self, project_id: str) -> bool:
        """Проверить существование проекта."""

    @abstractmethod
    async def project_workspace_id(self, project_id: str) -> str | None:
        """Получить workspace_id проекта."""
