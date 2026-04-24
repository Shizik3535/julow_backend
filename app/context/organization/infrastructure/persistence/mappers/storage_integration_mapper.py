from __future__ import annotations

from app.shared.domain.value_objects.url_vo import Url
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.organization.domain.aggregates.storage_integration import StorageIntegration
from app.context.organization.domain.value_objects.storage_config import StorageConfig
from app.context.organization.domain.value_objects.storage_provider import StorageProvider
from app.context.organization.domain.value_objects.storage_quota import StorageQuota
from app.context.organization.infrastructure.persistence.orm_models.storage_integration_orm import (
    StorageIntegrationORM,
)


class StorageIntegrationMapper(BaseMapper[StorageIntegration, StorageIntegrationORM]):
    """Data Mapper: StorageIntegration ↔ StorageIntegrationORM."""

    def to_domain(self, orm_model: StorageIntegrationORM) -> StorageIntegration:
        config = StorageConfig(
            provider=StorageProvider(orm_model.sc_provider),
            endpoint=Url(orm_model.sc_endpoint) if orm_model.sc_endpoint else None,
            bucket=orm_model.sc_bucket,
            region=orm_model.sc_region,
            access_key=orm_model.sc_access_key,
        )
        quota = StorageQuota(
            max_bytes=orm_model.sq_max_bytes,
            used_bytes=orm_model.sq_used_bytes,
            max_file_size_bytes=orm_model.sq_max_file_size_bytes,
            allowed_extensions=orm_model.sq_allowed_extensions,
        )
        return StorageIntegration(
            id=self._map_id(orm_model.id),
            org_id=self._map_id(orm_model.org_id),
            config=config,
            quota=quota,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: StorageIntegration) -> StorageIntegrationORM:
        cfg = aggregate.config
        q = aggregate.quota
        return StorageIntegrationORM(
            id=self._map_uuid(aggregate.id),
            org_id=self._map_uuid(aggregate.org_id),
            # StorageConfig
            sc_provider=cfg.provider.value,
            sc_endpoint=str(cfg.endpoint) if cfg.endpoint else None,
            sc_bucket=cfg.bucket,
            sc_region=cfg.region,
            sc_access_key=cfg.access_key,
            # StorageQuota
            sq_max_bytes=q.max_bytes,
            sq_used_bytes=q.used_bytes,
            sq_max_file_size_bytes=q.max_file_size_bytes,
            sq_allowed_extensions=q.allowed_extensions,
            # Timestamps
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
