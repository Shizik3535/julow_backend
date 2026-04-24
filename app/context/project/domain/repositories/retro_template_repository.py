from __future__ import annotations

from abc import abstractmethod

from app.shared.domain.base_repository import RepositoryPort
from app.context.project.domain.aggregates.retro_template import RetroTemplate


class RetroTemplateRepository(RepositoryPort[RetroTemplate]):
    """Порт репозитория для агрегата RetroTemplate."""

    @abstractmethod
    async def get_system_templates(self) -> list[RetroTemplate]:
        """Получить все системные шаблоны."""

    @abstractmethod
    async def get_by_project(self, project_id: str) -> list[RetroTemplate]:
        """Получить шаблоны проекта."""

    @abstractmethod
    async def get_by_name(self, name: str) -> RetroTemplate | None:
        """Найти шаблон по названию."""
