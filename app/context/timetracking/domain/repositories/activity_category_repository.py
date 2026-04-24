from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.timetracking.domain.aggregates.activity_category import ActivityCategory


class ActivityCategoryRepository(RepositoryPort[ActivityCategory]):
    """Порт репозитория для агрегата ActivityCategory."""

    @abstractmethod
    async def get_by_name(self, name: str) -> ActivityCategory | None:
        """Найти категорию по имени."""

    @abstractmethod
    async def get_system_categories(self) -> list[ActivityCategory]:
        """Найти все системные категории."""

    @abstractmethod
    async def get_by_workspace(self, workspace_id: Id) -> list[ActivityCategory]:
        """Найти категории workspace."""

    @abstractmethod
    async def search(self, offset: int = 0, limit: int = 100, filters: dict[str, Any] | None = None) -> list[ActivityCategory]:
        """Поиск категорий."""
