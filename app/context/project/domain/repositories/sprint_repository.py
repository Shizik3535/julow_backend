from __future__ import annotations

from abc import abstractmethod
from datetime import date

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.aggregates.sprint import Sprint


class SprintRepository(RepositoryPort[Sprint]):
    """Порт репозитория для агрегата Sprint."""

    @abstractmethod
    async def get_by_project(self, project_id: Id) -> list[Sprint]:
        """Найти все спринты проекта."""

    @abstractmethod
    async def get_active_by_project(self, project_id: Id) -> Sprint | None:
        """Найти активный спринт проекта."""

    @abstractmethod
    async def get_by_date_range(self, start: date, end: date) -> list[Sprint]:
        """Найти спринты по диапазону дат."""
