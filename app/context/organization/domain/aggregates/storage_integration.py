from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.value_objects.storage_config import StorageConfig
from app.context.organization.domain.value_objects.storage_quota import StorageQuota
from app.context.organization.domain.events.storage_integration_events import (
    OrgStorageAdded,
    OrgStorageUpdated,
    OrgStorageQuotaExceeded,
)
from app.context.organization.domain.exceptions.organization_exceptions import (
    StorageQuotaExceededException,
)


@dataclass
class StorageIntegration(AggregateRoot):
    """
    Корень агрегата хранилища организации (Organization BC).

    Связан с организацией через org_id. Одна StorageIntegration на организацию.

    Атрибуты:
        org_id: Opaque ID организации.
        config: Конфигурация хранилища.
        quota: Квота хранилища.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    org_id: Id = field(default_factory=Id.generate)
    config: StorageConfig = field(default_factory=StorageConfig)
    quota: StorageQuota = field(default_factory=StorageQuota)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    # --- Фабричный метод ---

    @classmethod
    def create(
        cls,
        org_id: Id,
        config: StorageConfig,
        quota: StorageQuota,
    ) -> StorageIntegration:
        """Создаёт хранилище организации."""
        storage = cls(org_id=org_id, config=config, quota=quota)
        storage._register_event(
            OrgStorageAdded(org_id=str(org_id), storage_id=str(storage.id))
        )
        return storage

    # --- Бизнес-методы ---

    def update_config(self, config: StorageConfig | None = None) -> None:
        """Обновляет конфигурацию хранилища."""
        if config is not None:
            self.config = config
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            OrgStorageUpdated(org_id=str(self.org_id), changed_fields=["config"])
        )

    def update_quota(self, quota: StorageQuota | None = None) -> None:
        """Обновляет квоту хранилища."""
        if quota is not None:
            self.quota = quota
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            OrgStorageUpdated(org_id=str(self.org_id), changed_fields=["quota"])
        )

    def check_quota(self, additional_bytes: int) -> None:
        """Проверяет, не превысит ли дополнительный объём квоту."""
        if self.quota.max_bytes > 0 and self.quota.used_bytes + additional_bytes > self.quota.max_bytes:
            self._register_event(
                OrgStorageQuotaExceeded(org_id=str(self.org_id))
            )
            raise StorageQuotaExceededException()
