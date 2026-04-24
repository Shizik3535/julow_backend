from __future__ import annotations

from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.ip_address_vo import IpAddress
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper
from app.context.identity.domain.aggregates.session import Session
from app.context.identity.domain.value_objects.device_info import DeviceInfo
from app.context.identity.domain.value_objects.geolocation import Geolocation
from app.context.identity.domain.value_objects.refresh_token import RefreshToken
from app.context.identity.domain.value_objects.session_status import SessionStatus
from app.context.identity.infrastructure.persistence.orm_models.session_orm import SessionORM


class SessionMapper(BaseMapper[Session, SessionORM]):
    """Data Mapper: Session ↔ SessionORM."""

    def to_domain(self, orm_model: SessionORM) -> Session:
        geolocation = None
        if orm_model.geo_country or orm_model.geo_city:
            geolocation = Geolocation(
                country=orm_model.geo_country,
                city=orm_model.geo_city,
                latitude=orm_model.geo_latitude,
                longitude=orm_model.geo_longitude,
            )

        refresh_token = None
        if orm_model.refresh_token:
            refresh_token = RefreshToken(value=orm_model.refresh_token)

        return Session(
            id=self._map_id(orm_model.id),
            user_id=self._map_id(orm_model.user_id),
            device_info=DeviceInfo(
                user_agent=orm_model.user_agent,
                os=orm_model.os,
                browser=orm_model.browser,
                device_type=orm_model.device_type,
            ),
            ip_address=IpAddress(orm_model.ip_address),
            geolocation=geolocation,
            is_remember_me=orm_model.is_remember_me,
            refresh_token=refresh_token,
            status=SessionStatus(orm_model.status),
            max_concurrent=orm_model.max_concurrent,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
            expires_at=orm_model.expires_at,
            terminated_at=orm_model.terminated_at,
        )

    def to_orm(self, aggregate: Session) -> SessionORM:
        geo = aggregate.geolocation
        return SessionORM(
            id=self._map_uuid(aggregate.id),
            user_id=self._map_uuid(aggregate.user_id),
            user_agent=aggregate.device_info.user_agent,
            os=aggregate.device_info.os,
            browser=aggregate.device_info.browser,
            device_type=aggregate.device_info.device_type,
            ip_address=aggregate.ip_address.value,
            geo_country=geo.country if geo else None,
            geo_city=geo.city if geo else None,
            geo_latitude=geo.latitude if geo else None,
            geo_longitude=geo.longitude if geo else None,
            is_remember_me=aggregate.is_remember_me,
            refresh_token=aggregate.refresh_token.value if aggregate.refresh_token else None,
            status=aggregate.status.value,
            max_concurrent=aggregate.max_concurrent,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
            expires_at=aggregate.expires_at,
            terminated_at=aggregate.terminated_at,
        )
