from __future__ import annotations

from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.filestorage.domain.aggregates.storage import Storage
from app.context.filestorage.domain.value_objects.file_type import FileType
from app.context.filestorage.domain.value_objects.storage_config import StorageConfig
from app.context.filestorage.domain.value_objects.storage_owner_type import StorageOwnerType
from app.context.filestorage.domain.value_objects.storage_provider import StorageProvider
from app.context.filestorage.infrastructure.persistence.orm_models.storage_orm import StorageORM


class StorageMapper(BaseMapper[Storage, StorageORM]):
    """Data Mapper: Storage ↔ StorageORM."""

    def to_domain(self, orm_model: StorageORM) -> Storage:
        return Storage(
            id=self._map_id(orm_model.id),
            owner_type=StorageOwnerType(orm_model.owner_type),
            owner_id=self._map_id(orm_model.owner_id),
            provider=StorageProvider(orm_model.provider),
            config=StorageConfig(
                endpoint=orm_model.endpoint,
                bucket=orm_model.bucket,
                region=orm_model.region,
                access_key_ref=orm_model.access_key_ref,
                secret_key_ref=orm_model.secret_key_ref,
                custom_params=orm_model.custom_params,
            ),
            max_bytes=orm_model.max_bytes,
            used_bytes=orm_model.used_bytes,
            allowed_file_types=(
                [FileType(t) for t in orm_model.allowed_file_types]
                if orm_model.allowed_file_types
                else None
            ),
            max_file_size_bytes=orm_model.max_file_size_bytes,
            is_encrypted=orm_model.is_encrypted,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: Storage) -> StorageORM:
        return StorageORM(
            id=self._map_uuid(aggregate.id),
            owner_type=aggregate.owner_type.value,
            owner_id=self._map_uuid(aggregate.owner_id),
            provider=aggregate.provider.value,
            endpoint=aggregate.config.endpoint,
            bucket=aggregate.config.bucket,
            region=aggregate.config.region,
            access_key_ref=aggregate.config.access_key_ref,
            secret_key_ref=aggregate.config.secret_key_ref,
            custom_params=aggregate.config.custom_params,
            max_bytes=aggregate.max_bytes,
            used_bytes=aggregate.used_bytes,
            allowed_file_types=(
                [t.value for t in aggregate.allowed_file_types]
                if aggregate.allowed_file_types is not None
                else None
            ),
            max_file_size_bytes=aggregate.max_file_size_bytes,
            is_encrypted=aggregate.is_encrypted,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
