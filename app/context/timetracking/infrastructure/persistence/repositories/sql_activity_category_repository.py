from __future__ import annotations

from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository

from app.context.timetracking.domain.aggregates.activity_category import ActivityCategory
from app.context.timetracking.domain.repositories.activity_category_repository import (
    ActivityCategoryRepository,
)
from app.context.timetracking.infrastructure.persistence.mappers.activity_category_mapper import (
    ActivityCategoryMapper,
)
from app.context.timetracking.infrastructure.persistence.orm_models.activity_category_orm import (
    ActivityCategoryORM,
)


class SqlActivityCategoryRepository(
    SqlAlchemyRepository[ActivityCategory, ActivityCategoryORM],
    ActivityCategoryRepository,
):
    """SQLAlchemy-реализация ActivityCategoryRepository."""

    def __init__(self, session: AsyncSession, mapper: ActivityCategoryMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=ActivityCategoryORM)

    async def get_by_name(self, name: str, workspace_id: Id | None = None) -> ActivityCategory | None:
        if workspace_id is not None:
            ws_uuid = self._mapper._map_uuid(workspace_id)
            stmt = select(ActivityCategoryORM).where(
                ActivityCategoryORM.name == name,
                ActivityCategoryORM.workspace_id == ws_uuid,
                ActivityCategoryORM.is_deleted.is_(False),
            )
        else:
            stmt = (
                select(ActivityCategoryORM)
                .where(
                    ActivityCategoryORM.name == name,
                    ActivityCategoryORM.is_system.is_(True),
                    ActivityCategoryORM.is_deleted.is_(False),
                )
                .limit(1)
            )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None

    async def get_system_categories(self) -> list[ActivityCategory]:
        stmt = select(ActivityCategoryORM).where(
            ActivityCategoryORM.is_system.is_(True),
            ActivityCategoryORM.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def get_by_workspace(self, workspace_id: Id) -> list[ActivityCategory]:
        ws_uuid = self._mapper._map_uuid(workspace_id)
        stmt = select(ActivityCategoryORM).where(
            or_(
                ActivityCategoryORM.workspace_id == ws_uuid,
                ActivityCategoryORM.is_system.is_(True),
            ),
            ActivityCategoryORM.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def search(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[ActivityCategory]:
        stmt = select(ActivityCategoryORM).where(ActivityCategoryORM.is_deleted.is_(False))
        if filters:
            name = filters.get("name")
            if name:
                safe = name.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
                stmt = stmt.where(ActivityCategoryORM.name.ilike(f"%{safe}%", escape="\\"))
            workspace_id = filters.get("workspace_id")
            if workspace_id:
                ws_uuid = self._mapper._map_uuid(Id.from_string(workspace_id) if isinstance(workspace_id, str) else workspace_id)
                stmt = stmt.where(ActivityCategoryORM.workspace_id == ws_uuid)
        stmt = stmt.offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]
