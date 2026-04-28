from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.notification.domain.aggregates.device_token import DeviceToken
from app.context.notification.domain.repositories.device_token_repository import DeviceTokenRepository
from app.context.notification.infrastructure.persistence.mappers.device_token_mapper import DeviceTokenMapper
from app.context.notification.infrastructure.persistence.orm_models.device_token_orm import DeviceTokenORM


class SqlDeviceTokenRepository(
    SqlAlchemyRepository[DeviceToken, DeviceTokenORM],
    DeviceTokenRepository,
):
    """SQLAlchemy-реализация DeviceTokenRepository."""

    def __init__(self, session: AsyncSession, mapper: DeviceTokenMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=DeviceTokenORM)

    async def get_by_user_id(self, user_id: Id) -> list[DeviceToken]:
        uuid_val = self._mapper._map_uuid(user_id)
        stmt = select(DeviceTokenORM).where(DeviceTokenORM.user_id == uuid_val)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_active_by_user_id(self, user_id: Id) -> list[DeviceToken]:
        uuid_val = self._mapper._map_uuid(user_id)
        stmt = select(DeviceTokenORM).where(
            DeviceTokenORM.user_id == uuid_val,
            DeviceTokenORM.is_active == True,
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_by_token(self, token: str) -> DeviceToken | None:
        stmt = select(DeviceTokenORM).where(DeviceTokenORM.token == token)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None
