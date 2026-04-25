from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.project.domain.aggregates.sprint import Sprint
from app.context.project.domain.repositories.sprint_repository import SprintRepository
from app.context.project.infrastructure.persistence.mappers.sprint_mapper import SprintMapper
from app.context.project.infrastructure.persistence.orm_models.sprint_orm import SprintORM


class SqlSprintRepository(
    SqlAlchemyRepository[Sprint, SprintORM],
    SprintRepository,
):
    """SQLAlchemy-реализация SprintRepository."""

    def __init__(self, session: AsyncSession, mapper: SprintMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=SprintORM)

    async def get_by_project(self, project_id: Id) -> list[Sprint]:
        uuid_val = self._mapper._map_uuid(project_id)
        stmt = select(SprintORM).where(SprintORM.project_id == uuid_val)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_active_by_project(self, project_id: Id) -> list[Sprint]:
        uuid_val = self._mapper._map_uuid(project_id)
        stmt = select(SprintORM).where(
            SprintORM.project_id == uuid_val,
            SprintORM.status == "active",
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_by_date_range(self, project_id: Id, start_date, end_date) -> list[Sprint]:
        uuid_val = self._mapper._map_uuid(project_id)
        stmt = select(SprintORM).where(
            SprintORM.project_id == uuid_val,
            SprintORM.sprint_start <= end_date,
            SprintORM.sprint_end >= start_date,
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]
