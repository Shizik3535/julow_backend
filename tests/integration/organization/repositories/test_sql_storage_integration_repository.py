"""Интеграционные тесты SqlStorageIntegrationRepository (реальная PostgreSQL)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.url_vo import Url
from app.context.organization.domain.aggregates.storage_integration import StorageIntegration
from app.context.organization.domain.value_objects.storage_config import StorageConfig
from app.context.organization.domain.value_objects.storage_provider import StorageProvider
from app.context.organization.domain.value_objects.storage_quota import StorageQuota
from app.context.organization.infrastructure.persistence.repositories.sql_storage_integration_repository import (
    SqlStorageIntegrationRepository,
)


@pytest.mark.integration
class TestSqlStorageIntegrationRepositoryAdd:
    """Тесты добавления."""

    async def test_add_and_get_by_id(
        self, storage_repo: SqlStorageIntegrationRepository, make_storage_integration
    ) -> None:
        storage = await make_storage_integration()
        found = await storage_repo.get_by_id(storage.id)
        assert found is not None
        assert found.id == storage.id


@pytest.mark.integration
class TestSqlStorageIntegrationRepositorySearch:
    """Тесты поиска."""

    async def test_get_by_org_id_found(
        self, storage_repo: SqlStorageIntegrationRepository, make_storage_integration, make_org
    ) -> None:
        org = await make_org()
        storage = await make_storage_integration(org_id=org.id)
        found = await storage_repo.get_by_org_id(org.id)
        assert found is not None
        assert found.id == storage.id

    async def test_get_by_org_id_not_found(self, storage_repo: SqlStorageIntegrationRepository) -> None:
        found = await storage_repo.get_by_org_id(Id.generate())
        assert found is None


@pytest.mark.integration
class TestSqlStorageIntegrationRepositoryUpdate:
    """Тесты обновления."""

    async def test_update_config(
        self, storage_repo: SqlStorageIntegrationRepository, make_storage_integration
    ) -> None:
        storage = await make_storage_integration()
        new_config = StorageConfig(
            provider=StorageProvider.AWS_S3,
            endpoint=Url("https://minio.example.com"),
            bucket="test-bucket",
            region="us-east-1",
            access_key="access-key-123",
        )
        storage.update_config(config=new_config)
        storage.clear_domain_events()
        await storage_repo.update(storage)

        found = await storage_repo.get_by_id(storage.id)
        assert found is not None
        assert found.config.provider == StorageProvider.AWS_S3
        assert found.config.bucket == "test-bucket"

    async def test_update_quota(
        self, storage_repo: SqlStorageIntegrationRepository, make_storage_integration
    ) -> None:
        storage = await make_storage_integration()
        new_quota = StorageQuota(max_bytes=2147483647, used_bytes=0)
        storage.update_quota(quota=new_quota)
        storage.clear_domain_events()
        await storage_repo.update(storage)

        found = await storage_repo.get_by_id(storage.id)
        assert found is not None
        assert found.quota.max_bytes == 2147483647


@pytest.mark.integration
class TestSqlStorageIntegrationRepositoryDelete:
    """Тесты удаления."""

    async def test_delete(
        self, storage_repo: SqlStorageIntegrationRepository, make_storage_integration
    ) -> None:
        storage = await make_storage_integration()
        await storage_repo.delete(storage.id)
        found = await storage_repo.get_by_id(storage.id)
        assert found is None
