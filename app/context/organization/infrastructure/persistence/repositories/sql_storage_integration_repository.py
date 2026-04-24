from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.organization.domain.aggregates.storage_integration import StorageIntegration
from app.context.organization.domain.repositories.storage_integration_repository import StorageIntegrationRepository
from app.context.organization.infrastructure.persistence.mappers.storage_integration_mapper import (
    StorageIntegrationMapper,
)
from app.context.organization.infrastructure.persistence.orm_models.storage_integration_orm import (
    StorageIntegrationORM,
)


class SqlStorageIntegrationRepository(
    SqlAlchemyRepository[StorageIntegration, StorageIntegrationORM],
    StorageIntegrationRepository,
):
    """SQLAlchemy-реализация StorageIntegrationRepository."""

    def __init__(self, session: AsyncSession, mapper: StorageIntegrationMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=StorageIntegrationORM)

    async def get_by_org_id(self, org_id: Id) -> StorageIntegration | None:
        uuid_val = self._mapper._map_uuid(org_id)
        stmt = select(StorageIntegrationORM).where(StorageIntegrationORM.org_id == uuid_val)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None
