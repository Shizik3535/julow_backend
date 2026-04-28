from __future__ import annotations

from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.notification.domain.aggregates.device_token import DeviceToken
from app.context.notification.infrastructure.persistence.orm_models.device_token_orm import DeviceTokenORM


class DeviceTokenMapper(BaseMapper[DeviceToken, DeviceTokenORM]):
    """Data Mapper: DeviceToken ↔ DeviceTokenORM."""

    def to_domain(self, orm_model: DeviceTokenORM) -> DeviceToken:
        return DeviceToken(
            id=self._map_id(orm_model.id),
            user_id=self._map_id(orm_model.user_id),
            token=orm_model.token,
            platform=orm_model.platform,
            device_name=orm_model.device_name,
            is_active=orm_model.is_active,
            last_used_at=orm_model.last_used_at,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: DeviceToken) -> DeviceTokenORM:
        return DeviceTokenORM(
            id=self._map_uuid(aggregate.id),
            user_id=self._map_uuid(aggregate.user_id),
            token=aggregate.token,
            platform=aggregate.platform,
            device_name=aggregate.device_name,
            is_active=aggregate.is_active,
            last_used_at=aggregate.last_used_at,
            created_at=aggregate.created_at,
        )
