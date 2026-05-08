from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import (
    SqlAlchemyRepository,
)

from app.context.filestorage.domain.aggregates.storage import Storage
from app.context.filestorage.domain.repositories.storage_repository import StorageRepository
from app.context.filestorage.domain.value_objects.storage_owner_type import StorageOwnerType
from app.context.filestorage.infrastructure.persistence.mappers.storage_mapper import StorageMapper
from app.context.filestorage.infrastructure.persistence.orm_models.storage_orm import StorageORM


class SqlStorageRepository(
    SqlAlchemyRepository[Storage, StorageORM],
    StorageRepository,
):
    """SQLAlchemy-реализация StorageRepository."""

    def __init__(self, session: AsyncSession, mapper: StorageMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=StorageORM)
        self._mapper: StorageMapper = mapper

    async def get_by_owner(
        self, owner_type: StorageOwnerType, owner_id: Id
    ) -> Storage | None:
        stmt = select(StorageORM).where(
            StorageORM.owner_type == owner_type.value,
            StorageORM.owner_id == self._mapper._map_uuid(owner_id),
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None

    async def get_by_owner_type(self, owner_type: StorageOwnerType) -> list[Storage]:
        stmt = select(StorageORM).where(StorageORM.owner_type == owner_type.value)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]
