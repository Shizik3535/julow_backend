from __future__ import annotations

from abc import abstractmethod

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.filestorage.domain.aggregates.storage import Storage
from app.context.filestorage.domain.value_objects.storage_owner_type import StorageOwnerType


class StorageRepository(RepositoryPort[Storage]):
    """Порт репозитория для агрегата Storage."""

    @abstractmethod
    async def get_by_owner(self, owner_type: StorageOwnerType, owner_id: Id) -> Storage | None:
        """Найти хранилище по владельцу."""

    @abstractmethod
    async def get_by_owner_type(self, owner_type: StorageOwnerType) -> list[Storage]:
        """Найти все хранилища по типу владельца."""
