from __future__ import annotations

from abc import ABC, abstractmethod

from app.context.project.application.dto.project_dto import ProjectDTO


class ProjectProvider(ABC):
    """
    Outboard-порт: предоставление данных проекта другим BC.

    Реализуется в infrastructure слое Project BC.
    Другие BC инжектируют соответствующий inboard-порт,
    адаптер которого делегирует в этот provider.
    """

    @abstractmethod
    async def get_project(self, project_id: str) -> ProjectDTO | None:
        """Получить проект по ID."""

    @abstractmethod
    async def project_exists(self, project_id: str) -> bool:
        """Проверить существование проекта."""

    @abstractmethod
    async def get_projects_by_workspace(self, workspace_id: str) -> list[ProjectDTO]:
        """Получить все проекты workspace."""
