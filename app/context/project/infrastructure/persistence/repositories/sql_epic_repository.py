from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.project.domain.aggregates.epic import Epic
from app.context.project.domain.repositories.epic_repository import EpicRepository
from app.context.project.infrastructure.persistence.mappers.epic_mapper import EpicMapper
from app.context.project.infrastructure.persistence.orm_models.epic_orm import EpicORM


class SqlEpicRepository(
    SqlAlchemyRepository[Epic, EpicORM],
    EpicRepository,
):
    """SQLAlchemy-реализация EpicRepository."""

    def __init__(self, session: AsyncSession, mapper: EpicMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=EpicORM)

    async def get_by_project(self, project_id: Id) -> list[Epic]:
        uuid_val = self._mapper._map_uuid(project_id)
        stmt = select(EpicORM).where(EpicORM.project_id == uuid_val)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_by_status(self, project_id: Id, status: str) -> list[Epic]:
        uuid_val = self._mapper._map_uuid(project_id)
        stmt = select(EpicORM).where(EpicORM.project_id == uuid_val, EpicORM.status == status)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_by_owner(self, owner_id: Id) -> list[Epic]:
        uuid_val = self._mapper._map_uuid(owner_id)
        stmt = select(EpicORM).where(EpicORM.owner_id == uuid_val)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]
