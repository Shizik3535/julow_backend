from __future__ import annotations

from abc import abstractmethod

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.timetracking.domain.aggregates.time_entry_tag import TimeEntryTag


class TimeEntryTagRepository(RepositoryPort[TimeEntryTag]):
    """Порт репозитория для агрегата TimeEntryTag."""

    @abstractmethod
    async def get_by_name(self, name: str, workspace_id: Id) -> TimeEntryTag | None:
        """Найти тег по имени в пределах workspace."""

    @abstractmethod
    async def get_by_workspace(self, workspace_id: Id) -> list[TimeEntryTag]:
        """Найти теги workspace."""
