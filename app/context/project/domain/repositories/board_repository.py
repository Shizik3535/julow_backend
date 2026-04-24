from __future__ import annotations

from abc import abstractmethod

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.aggregates.board import Board


class BoardRepository(RepositoryPort[Board]):
    """Порт репозитория для агрегата Board."""

    @abstractmethod
    async def get_by_project_id(self, project_id: Id) -> Board | None:
        """Найти доску по ID проекта."""
