from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.aggregates.project import Project
from app.context.project.domain.value_objects.methodology import Methodology


class ProjectRepository(RepositoryPort[Project]):
    """Порт репозитория для агрегата Project."""

    @abstractmethod
    async def get_by_workspace(self, workspace_id: Id) -> list[Project]:
        """Найти проекты по ID workspace."""

    @abstractmethod
    async def get_by_member(self, user_id: Id) -> list[Project]:
        """Найти проекты по ID участника."""

    @abstractmethod
    async def get_by_methodology(self, methodology: Methodology) -> list[Project]:
        """Найти проекты по методологии."""

    @abstractmethod
    async def get_archived_by_workspace(self, workspace_id: Id) -> list[Project]:
        """Найти архивированные проекты workspace."""

    @abstractmethod
    async def search(self, offset: int = 0, limit: int = 100, filters: dict[str, Any] | None = None) -> list[Project]:
        """Поиск проектов с фильтрацией."""
