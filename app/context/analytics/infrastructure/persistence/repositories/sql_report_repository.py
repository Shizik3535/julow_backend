from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.exceptions.entity_not_found_exception import EntityNotFoundException
from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import (
    SqlAlchemyRepository,
)

from app.context.analytics.domain.aggregates.report import Report
from app.context.analytics.domain.repositories.report_repository import ReportRepository
from app.context.analytics.domain.value_objects.bounded_context_ref import (
    BoundedContextRef,
)
from app.context.analytics.domain.value_objects.data_source import DataSource
from app.context.analytics.domain.value_objects.report_type import ReportType
from app.context.analytics.infrastructure.persistence.mappers._query_serialization import (
    analytics_query_to_json,
)
from app.context.analytics.infrastructure.persistence.mappers.report_mapper import (
    ReportMapper,
)
from app.context.analytics.infrastructure.persistence.orm_models.report_orm import (
    ReportORM,
    ReportShareORM,
)


class SqlReportRepository(
    SqlAlchemyRepository[Report, ReportORM],
    ReportRepository,
):
    """SQLAlchemy-реализация ``ReportRepository``.

    Использует денормализованные колонки ``query_data_source``/
    ``query_bounded_context`` для эффективной фильтрации по источнику
    данных (см. ``ReportMapper`` и ``ReportRepository`` docstring).
    """

    def __init__(self, session: AsyncSession, mapper: ReportMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=ReportORM)
        self._mapper: ReportMapper = mapper

    async def update(self, aggregate: Report) -> Report:
        """Перезаписать скалярные поля + дочернюю коллекцию shares."""
        uuid_value = self._mapper._map_uuid(aggregate.id)
        stmt = select(ReportORM).where(ReportORM.id == uuid_value)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        if orm is None:
            raise EntityNotFoundException(entity_type="Report", id=aggregate.id)

        orm.owner_id = self._mapper._map_uuid(aggregate.owner_id)
        orm.workspace_id = (
            self._mapper._map_uuid(aggregate.workspace_id)
            if aggregate.workspace_id
            else None
        )
        orm.name = aggregate.name
        orm.description = aggregate.description
        orm.report_type = aggregate.report_type.value

        # Сериализованный VO + денормализованные индексы
        orm.query = analytics_query_to_json(aggregate.query)
        orm.query_data_source = aggregate.query.data_source.value
        orm.query_bounded_context = aggregate.query.bounded_context.value

        if aggregate.schedule is not None:
            orm.schedule_frequency = aggregate.schedule.frequency.value
            orm.schedule_recipients = [str(r) for r in aggregate.schedule.recipients]
            orm.schedule_is_active = aggregate.schedule.is_active
            orm.schedule_next_run_at = aggregate.schedule.next_run_at
            orm.schedule_last_run_at = aggregate.schedule.last_run_at
        else:
            orm.schedule_frequency = None
            orm.schedule_recipients = None
            orm.schedule_is_active = False
            orm.schedule_next_run_at = None
            orm.schedule_last_run_at = None

        orm.last_generated_at = aggregate.last_generated_at
        orm.last_export_format = (
            aggregate.last_export_format.value
            if aggregate.last_export_format
            else None
        )
        orm.updated_at = aggregate.updated_at

        orm.shares = [
            self._mapper._share_to_orm(s, report_id=aggregate.id)
            for s in aggregate.shares
        ]
        await self._session.flush()
        return aggregate

    # ---- ReportRepository ----

    async def get_by_owner(self, owner_id: Id) -> list[Report]:
        stmt = select(ReportORM).where(
            ReportORM.owner_id == self._mapper._map_uuid(owner_id)
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def get_by_workspace(self, workspace_id: Id) -> list[Report]:
        stmt = select(ReportORM).where(
            ReportORM.workspace_id == self._mapper._map_uuid(workspace_id)
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def get_shared_with_user(self, user_id: Id) -> list[Report]:
        stmt = (
            select(ReportORM)
            .join(ReportShareORM, ReportShareORM.report_id == ReportORM.id)
            .where(ReportShareORM.user_id == self._mapper._map_uuid(user_id))
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().unique().all()]

    async def get_scheduled_reports(self) -> list[Report]:
        stmt = select(ReportORM).where(
            ReportORM.schedule_frequency.is_not(None),
            ReportORM.schedule_is_active.is_(True),
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def get_by_type(
        self, report_type: ReportType, workspace_id: Id
    ) -> list[Report]:
        stmt = select(ReportORM).where(
            ReportORM.workspace_id == self._mapper._map_uuid(workspace_id),
            ReportORM.report_type == report_type.value,
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def get_by_data_source(
        self, data_source: DataSource, workspace_id: Id
    ) -> list[Report]:
        stmt = select(ReportORM).where(
            ReportORM.workspace_id == self._mapper._map_uuid(workspace_id),
            ReportORM.query_data_source == data_source.value,
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def get_by_bounded_context(
        self, bounded_context: BoundedContextRef, workspace_id: Id
    ) -> list[Report]:
        stmt = select(ReportORM).where(
            ReportORM.workspace_id == self._mapper._map_uuid(workspace_id),
            ReportORM.query_bounded_context == bounded_context.value,
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def search(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[Report]:
        stmt = select(ReportORM)
        stmt = self._apply_filters(stmt, filters)
        stmt = stmt.offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]
