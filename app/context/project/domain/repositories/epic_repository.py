from __future__ import annotations

from abc import abstractmethod

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.aggregates.epic import Epic
from app.context.project.domain.value_objects.epic_status import EpicStatus


class EpicRepository(RepositoryPort[Epic]):
    """Порт репозитория для агрегата Epic."""

    @abstractmethod
    async def get_by_project(self, project_id: Id) -> list[Epic]:
        """Найти все эпики проекта."""

    @abstractmethod
    async def get_by_status(self, project_id: Id, status: EpicStatus) -> list[Epic]:
        """Найти эпики по статусу."""

    @abstractmethod
    async def get_by_owner(self, owner_id: Id) -> list[Epic]:
        """Найти эпики по владельцу."""
