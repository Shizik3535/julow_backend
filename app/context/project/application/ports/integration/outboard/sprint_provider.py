from __future__ import annotations

from abc import ABC, abstractmethod

from app.context.project.application.dto.sprint_dto import SprintDTO


class SprintProvider(ABC):
    """
    Outboard-порт: предоставление данных спринтов другим BC.

    Task BC использует для:
    - Проверки существования спринта (назначение задачи в спринт).
    - Получения активного спринта (default sprint assignment).
    - Получения списка спринтов проекта (backlog management).
    """

    @abstractmethod
    async def sprint_exists(self, sprint_id: str) -> bool:
        """Проверить существование спринта."""

    @abstractmethod
    async def get_sprint(self, sprint_id: str) -> SprintDTO | None:
        """Получить спринт по ID."""

    @abstractmethod
    async def get_active_sprint(self, project_id: str) -> SprintDTO | None:
        """Получить активный спринт проекта."""

    @abstractmethod
    async def get_sprints_by_project(self, project_id: str) -> list[SprintDTO]:
        """Получить все спринты проекта."""
