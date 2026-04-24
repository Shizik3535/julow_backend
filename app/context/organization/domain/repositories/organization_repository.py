from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.aggregates.organization import Organization


class OrganizationRepository(RepositoryPort[Organization]):
    """
    Порт репозитория для агрегата Organization.

    Расширяет базовый RepositoryPort специфичными запросами
    для Organization BC.
    """

    @abstractmethod
    async def get_by_owner(self, owner_id: Id) -> list[Organization]:
        """Найти организации по ID владельца."""

    @abstractmethod
    async def search(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[Organization]:
        """Поиск организаций с фильтрацией."""
