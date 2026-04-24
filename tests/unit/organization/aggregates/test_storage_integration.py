"""Unit-тесты для агрегата StorageIntegration (Organization BC)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.aggregates.storage_integration import StorageIntegration
from app.context.organization.domain.value_objects.storage_config import StorageConfig
from app.context.organization.domain.value_objects.storage_provider import StorageProvider
from app.context.organization.domain.value_objects.storage_quota import StorageQuota
from app.context.organization.domain.events.storage_integration_events import (
    OrgStorageAdded,
    OrgStorageUpdated,
    OrgStorageQuotaExceeded,
)
from app.context.organization.domain.exceptions.organization_exceptions import (
    StorageQuotaExceededException,
)


# ═══════════════════════════════════════════════════════════════════════════
# Создание
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestStorageIntegrationCreation:
    def test_create(self, new_storage: StorageIntegration) -> None:
        assert new_storage.config.provider == StorageProvider.LOCAL
        assert new_storage.quota.max_bytes == 1_000_000

    def test_create_emits_org_storage_added(self, new_storage: StorageIntegration) -> None:
        events = new_storage.clear_domain_events()
        assert any(isinstance(e, OrgStorageAdded) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Обновление
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestStorageIntegrationUpdate:
    def test_update_config(self, storage: StorageIntegration) -> None:
        new_config = StorageConfig(provider=StorageProvider.LOCAL)
        storage.update_config(config=new_config)
        assert storage.config == new_config

    def test_update_config_emits_event(self, storage: StorageIntegration) -> None:
        new_config = StorageConfig(provider=StorageProvider.LOCAL)
        storage.update_config(config=new_config)
        events = storage.clear_domain_events()
        assert any(isinstance(e, OrgStorageUpdated) for e in events)

    def test_update_quota(self, storage: StorageIntegration) -> None:
        new_quota = StorageQuota(max_bytes=2_000_000, used_bytes=0)
        storage.update_quota(quota=new_quota)
        assert storage.quota.max_bytes == 2_000_000

    def test_update_quota_emits_event(self, storage: StorageIntegration) -> None:
        new_quota = StorageQuota(max_bytes=2_000_000, used_bytes=0)
        storage.update_quota(quota=new_quota)
        events = storage.clear_domain_events()
        assert any(isinstance(e, OrgStorageUpdated) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Квота
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestStorageIntegrationQuota:
    def test_check_quota_within_limit(self, storage: StorageIntegration) -> None:
        storage.check_quota(500_000)

    def test_check_quota_exceeded_raises(self, storage: StorageIntegration) -> None:
        with pytest.raises(StorageQuotaExceededException):
            storage.check_quota(1_500_000)

    def test_check_quota_exceeded_emits_event(self, storage: StorageIntegration) -> None:
        with pytest.raises(StorageQuotaExceededException):
            storage.check_quota(1_500_000)
        events = storage.clear_domain_events()
        assert any(isinstance(e, OrgStorageQuotaExceeded) for e in events)

    def test_check_quota_unlimited(self, any_org_id: Id) -> None:
        config = StorageConfig(provider=StorageProvider.LOCAL)
        quota = StorageQuota(max_bytes=0, used_bytes=0)
        storage = StorageIntegration.create(org_id=any_org_id, config=config, quota=quota)
        storage.clear_domain_events()
        storage.check_quota(1_000_000)
        events = storage.clear_domain_events()
        assert not any(isinstance(e, OrgStorageQuotaExceeded) for e in events)
