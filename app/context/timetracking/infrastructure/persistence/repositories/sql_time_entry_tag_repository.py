from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository

from app.context.timetracking.domain.aggregates.time_entry_tag import TimeEntryTag
from app.context.timetracking.domain.repositories.time_entry_tag_repository import (
    TimeEntryTagRepository,
)
from app.context.timetracking.infrastructure.persistence.mappers.time_entry_tag_mapper import (
    TimeEntryTagMapper,
)
from app.context.timetracking.infrastructure.persistence.orm_models.time_entry_tag_orm import (
    TimeEntryTagORM,
)


class SqlTimeEntryTagRepository(
    SqlAlchemyRepository[TimeEntryTag, TimeEntryTagORM],
    TimeEntryTagRepository,
):
    """SQLAlchemy-реализация TimeEntryTagRepository."""

    def __init__(self, session: AsyncSession, mapper: TimeEntryTagMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=TimeEntryTagORM)

    async def get_by_name(self, name: str, workspace_id: Id) -> TimeEntryTag | None:
        ws_uuid = self._mapper._map_uuid(workspace_id)
        stmt = select(TimeEntryTagORM).where(
            TimeEntryTagORM.name == name,
            TimeEntryTagORM.workspace_id == ws_uuid,
            TimeEntryTagORM.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None

    async def get_by_workspace(self, workspace_id: Id) -> list[TimeEntryTag]:
        ws_uuid = self._mapper._map_uuid(workspace_id)
        stmt = select(TimeEntryTagORM).where(
            TimeEntryTagORM.workspace_id == ws_uuid,
            TimeEntryTagORM.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]
