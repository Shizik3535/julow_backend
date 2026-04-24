from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.exceptions import EntityNotFoundException
from app.context.organization.application.dto.storage_integration_dto import StorageIntegrationDTO
from app.context.organization.domain.repositories.storage_integration_repository import StorageIntegrationRepository


class GetOrgStorageQuery(BaseQuery):
    """
    Запрос хранилища организации.

    Атрибуты:
        org_id: ID организации.
    """

    org_id: str


class GetOrgStorageHandler(BaseQueryHandler[GetOrgStorageQuery, StorageIntegrationDTO]):
    """Обработчик запроса хранилища организации."""

    def __init__(self, storage_repo: StorageIntegrationRepository) -> None:
        super().__init__()
        self._storage_repo = storage_repo

    async def handle(self, query: GetOrgStorageQuery) -> StorageIntegrationDTO:
        storage = await self._storage_repo.get_by_org_id(Id.from_string(query.org_id))
        if storage is None:
            raise EntityNotFoundException(entity_type="StorageIntegration", id=query.org_id)

        return StorageIntegrationDTO(
            id=str(storage.id),
            org_id=str(storage.org_id),
            provider=storage.config.provider.value,
            endpoint=str(storage.config.endpoint) if storage.config.endpoint else None,
            bucket=storage.config.bucket,
            region=storage.config.region,
            max_bytes=storage.quota.max_bytes,
            used_bytes=storage.quota.used_bytes,
            max_file_size_bytes=storage.quota.max_file_size_bytes,
            allowed_extensions=storage.quota.allowed_extensions,
            created_at=storage.created_at,
            updated_at=storage.updated_at,
        )
