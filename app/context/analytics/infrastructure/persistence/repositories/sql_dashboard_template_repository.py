from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import (
    SqlAlchemyRepository,
)

from app.context.analytics.domain.aggregates.dashboard_template import DashboardTemplate
from app.context.analytics.domain.repositories.dashboard_template_repository import (
    DashboardTemplateRepository,
)
from app.context.analytics.infrastructure.persistence.mappers.dashboard_template_mapper import (
    DashboardTemplateMapper,
)
from app.context.analytics.infrastructure.persistence.orm_models.dashboard_template_orm import (
    DashboardTemplateORM,
)


class SqlDashboardTemplateRepository(
    SqlAlchemyRepository[DashboardTemplate, DashboardTemplateORM],
    DashboardTemplateRepository,
):
    """SQLAlchemy-реализация ``DashboardTemplateRepository``."""

    def __init__(
        self, session: AsyncSession, mapper: DashboardTemplateMapper
    ) -> None:
        super().__init__(
            session=session, mapper=mapper, orm_model_class=DashboardTemplateORM
        )
        self._mapper: DashboardTemplateMapper = mapper

    async def get_system_templates(self) -> list[DashboardTemplate]:
        stmt = select(DashboardTemplateORM).where(
            DashboardTemplateORM.is_system.is_(True),
            DashboardTemplateORM.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def get_by_workspace(
        self, workspace_id: Id
    ) -> list[DashboardTemplate]:
        # Только пользовательские шаблоны конкретного workspace —
        # системные приходят отдельно через ``get_system_templates``.
        stmt = select(DashboardTemplateORM).where(
            DashboardTemplateORM.is_system.is_(False),
            DashboardTemplateORM.workspace_id == self._mapper._map_uuid(workspace_id),
            DashboardTemplateORM.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def get_by_name(
        self, name: str, workspace_id: Id | None = None
    ) -> DashboardTemplate | None:
        # workspace_id=None -> ищем системный (is_system=True, workspace_id IS NULL).
        # Имя не уникально между workspace'ами: без фильтра по workspace
        # вернули бы произвольный шаблон чужого тенанта.
        if workspace_id is None:
            stmt = select(DashboardTemplateORM).where(
                DashboardTemplateORM.name == name,
                DashboardTemplateORM.is_system.is_(True),
                DashboardTemplateORM.is_deleted.is_(False),
            )
        else:
            stmt = select(DashboardTemplateORM).where(
                DashboardTemplateORM.name == name,
                DashboardTemplateORM.is_system.is_(False),
                DashboardTemplateORM.workspace_id == self._mapper._map_uuid(workspace_id),
                DashboardTemplateORM.is_deleted.is_(False),
            )
        result = await self._session.execute(stmt)
        orm = result.scalars().first()
        return self._mapper.to_domain(orm) if orm else None

    async def search(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[DashboardTemplate]:
        stmt = select(DashboardTemplateORM).where(
            DashboardTemplateORM.is_deleted.is_(False)
        )
        stmt = self._apply_filters(stmt, filters)
        stmt = stmt.offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]
