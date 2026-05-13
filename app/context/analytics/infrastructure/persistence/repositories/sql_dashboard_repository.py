from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.exceptions.entity_not_found_exception import EntityNotFoundException
from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import (
    SqlAlchemyRepository,
)

from app.context.analytics.domain.aggregates.dashboard import Dashboard
from app.context.analytics.domain.repositories.dashboard_repository import (
    DashboardRepository,
)
from app.context.analytics.infrastructure.persistence.mappers.dashboard_mapper import (
    DashboardMapper,
)
from app.context.analytics.infrastructure.persistence.orm_models.dashboard_orm import (
    DashboardORM,
    DashboardShareORM,
)


class SqlDashboardRepository(
    SqlAlchemyRepository[Dashboard, DashboardORM],
    DashboardRepository,
):
    """SQLAlchemy-реализация ``DashboardRepository``."""

    def __init__(self, session: AsyncSession, mapper: DashboardMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=DashboardORM)
        self._mapper: DashboardMapper = mapper

    async def update(self, aggregate: Dashboard) -> Dashboard:
        """Перезаписать скалярные поля + дочерние коллекции (widgets, shares)."""
        uuid_value = self._mapper._map_uuid(aggregate.id)
        stmt = select(DashboardORM).where(DashboardORM.id == uuid_value)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        if orm is None:
            raise EntityNotFoundException(entity_type="Dashboard", id=aggregate.id)

        orm.owner_id = self._mapper._map_uuid(aggregate.owner_id)
        orm.workspace_id = (
            self._mapper._map_uuid(aggregate.workspace_id)
            if aggregate.workspace_id
            else None
        )
        orm.name = aggregate.name
        orm.description = aggregate.description
        orm.is_auto_refresh = aggregate.is_auto_refresh
        orm.refresh_interval_seconds = aggregate.refresh_interval_seconds
        orm.is_default = aggregate.is_default
        orm.updated_at = aggregate.updated_at

        orm.widgets = [
            self._mapper._widget_to_orm(w, dashboard_id=aggregate.id)
            for w in aggregate.widgets
        ]
        orm.shares = [
            self._mapper._share_to_orm(s, dashboard_id=aggregate.id)
            for s in aggregate.shares
        ]
        await self._session.flush()
        return aggregate

    # ---- DashboardRepository ----

    async def get_by_owner(self, owner_id: Id) -> list[Dashboard]:
        stmt = select(DashboardORM).where(
            DashboardORM.owner_id == self._mapper._map_uuid(owner_id)
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def get_by_workspace(self, workspace_id: Id) -> list[Dashboard]:
        stmt = select(DashboardORM).where(
            DashboardORM.workspace_id == self._mapper._map_uuid(workspace_id)
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def get_shared_with_user(self, user_id: Id) -> list[Dashboard]:
        stmt = (
            select(DashboardORM)
            .join(DashboardShareORM, DashboardShareORM.dashboard_id == DashboardORM.id)
            .where(DashboardShareORM.user_id == self._mapper._map_uuid(user_id))
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().unique().all()]

    async def get_default_by_workspace(self, workspace_id: Id) -> Dashboard | None:
        stmt = select(DashboardORM).where(
            DashboardORM.workspace_id == self._mapper._map_uuid(workspace_id),
            DashboardORM.is_default.is_(True),
        )
        result = await self._session.execute(stmt)
        orm = result.scalars().first()
        return self._mapper.to_domain(orm) if orm else None

    async def search(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[Dashboard]:
        stmt = select(DashboardORM)
        stmt = self._apply_filters(stmt, filters)
        stmt = stmt.offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]
