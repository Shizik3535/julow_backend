from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.aggregates.project_role import ProjectRole


class ProjectRoleRepository(RepositoryPort[ProjectRole]):
    """Порт репозитория для агрегата ProjectRole."""

    @abstractmethod
    async def get_by_name(self, name: str) -> ProjectRole | None:
        """Найти роль по названию."""

    @abstractmethod
    async def get_system_roles(self) -> list[ProjectRole]:
        """Получить все системные роли."""

    @abstractmethod
    async def get_by_project(self, project_id: Id) -> list[ProjectRole]:
        """Получить все роли проекта (системные + кастомные)."""

    @abstractmethod
    async def search(self, offset: int = 0, limit: int = 100, filters: dict[str, Any] | None = None) -> list[ProjectRole]:
        """Поиск ролей с фильтрацией."""
