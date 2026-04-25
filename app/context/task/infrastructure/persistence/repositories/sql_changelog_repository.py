from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.task.domain.aggregates.changelog import ChangelogEntry
from app.context.task.domain.repositories.changelog_repository import ChangelogRepository
from app.context.task.infrastructure.persistence.mappers.changelog_mapper import ChangelogMapper
from app.context.task.infrastructure.persistence.orm_models.changelog_orm import ChangelogEntryORM


class SqlChangelogRepository(SqlAlchemyRepository[ChangelogEntry, ChangelogEntryORM], ChangelogRepository):
    """SQLAlchemy-реализация ChangelogRepository."""

    def __init__(self, session: AsyncSession, mapper: ChangelogMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=ChangelogEntryORM)

    # ------------------------------------------------------------------
    # Специфичные методы
    # ------------------------------------------------------------------

    async def get_by_task_id(self, task_id: Id, offset: int = 0, limit: int = 50) -> list[ChangelogEntry]:
        uuid_val = self._mapper._map_uuid(task_id)
        stmt = (
            select(ChangelogEntryORM)
            .where(ChangelogEntryORM.task_id == uuid_val)
            .order_by(ChangelogEntryORM.changed_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_by_task_and_field(self, task_id: Id, field_name: str) -> list[ChangelogEntry]:
        uuid_val = self._mapper._map_uuid(task_id)
        stmt = (
            select(ChangelogEntryORM)
            .where(
                ChangelogEntryORM.task_id == uuid_val,
                ChangelogEntryORM.field_name == field_name,
            )
            .order_by(ChangelogEntryORM.changed_at.desc())
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_recent_changes(self, task_id: Id, limit: int = 10) -> list[ChangelogEntry]:
        uuid_val = self._mapper._map_uuid(task_id)
        stmt = (
            select(ChangelogEntryORM)
            .where(ChangelogEntryORM.task_id == uuid_val)
            .order_by(ChangelogEntryORM.changed_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def count_by_task(self, task_id: Id) -> int:
        uuid_val = self._mapper._map_uuid(task_id)
        stmt = select(func.count()).select_from(ChangelogEntryORM).where(
            ChangelogEntryORM.task_id == uuid_val
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()
