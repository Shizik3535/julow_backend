from __future__ import annotations

from abc import abstractmethod

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.aggregates.storage_integration import StorageIntegration


class StorageIntegrationRepository(RepositoryPort[StorageIntegration]):
    """
    Порт репозитория для агрегата StorageIntegration.

    Расширяет базовый RepositoryPort специфичными запросами
    для управления хранилищами организаций.
    """

    @abstractmethod
    async def get_by_org_id(self, org_id: Id) -> StorageIntegration | None:
        """Найти хранилище по ID организации."""
