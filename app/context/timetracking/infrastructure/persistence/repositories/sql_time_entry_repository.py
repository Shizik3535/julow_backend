from __future__ import annotations

from datetime import date as date_type
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.exceptions.entity_not_found_exception import EntityNotFoundException
from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository

from app.context.timetracking.domain.aggregates.time_entry import TimeEntry
from app.context.timetracking.domain.repositories.time_entry_repository import (
    TimeEntryRepository,
)
from app.context.timetracking.domain.value_objects.time_entry_status import TimeEntryStatus
from app.context.timetracking.domain.value_objects.timer_state import TimerState
from app.context.timetracking.infrastructure.persistence.mappers.time_entry_mapper import (
    TimeEntryMapper,
)
from app.context.timetracking.infrastructure.persistence.orm_models.time_entry_orm import (
    TimeEntryORM,
    TimeEntryTimeLogORM,
    time_entry_tags_table,
)


class SqlTimeEntryRepository(
    SqlAlchemyRepository[TimeEntry, TimeEntryORM],
    TimeEntryRepository,
):
    """SQLAlchemy-реализация TimeEntryRepository."""

    def __init__(self, session: AsyncSession, mapper: TimeEntryMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=TimeEntryORM)

    # ------------------------------------------------------------------
    # Tag links — m2m через ассоциативную таблицу
    # ------------------------------------------------------------------

    async def _load_tag_ids(self, orm_model: TimeEntryORM) -> list[Id]:
        stmt = select(time_entry_tags_table.c.tag_id).where(
            time_entry_tags_table.c.time_entry_id == orm_model.id
        )
        result = await self._session.execute(stmt)
        ids = [self._mapper._map_id(row[0]) for row in result.fetchall()]
        orm_model._loaded_tag_ids = ids  # type: ignore[attr-defined]
        return ids

    async def _to_domain_with_tags(self, orm_model: TimeEntryORM) -> TimeEntry:
        await self._load_tag_ids(orm_model)
        return self._mapper.to_domain(orm_model)

    async def _to_domain_list_with_tags(self, orms: list[TimeEntryORM]) -> list[TimeEntry]:
        result = []
        for o in orms:
            await self._load_tag_ids(o)
            result.append(self._mapper.to_domain(o))
        return result

    async def _sync_tag_links(self, entry_id_uuid, tag_ids: list[Id]) -> None:
        """Удалить старые tag-связи и вставить новые."""
        await self._session.execute(
            time_entry_tags_table.delete().where(
                time_entry_tags_table.c.time_entry_id == entry_id_uuid
            )
        )
        for tag_id in tag_ids:
            await self._session.execute(
                time_entry_tags_table.insert().values(
                    time_entry_id=entry_id_uuid,
                    tag_id=self._mapper._map_uuid(tag_id),
                )
            )

    # ------------------------------------------------------------------
    # Override add/update/get_by_id
    # ------------------------------------------------------------------

    async def add(self, aggregate: TimeEntry) -> TimeEntry:
        orm = self._mapper.to_orm(aggregate)
        self._session.add(orm)
        await self._session.flush()
        await self._sync_tag_links(orm.id, aggregate.tag_ids)
        await self._session.flush()
        return aggregate

    async def update(self, aggregate: TimeEntry) -> TimeEntry:
        uuid_val = self._mapper._map_uuid(aggregate.id)
        stmt = select(TimeEntryORM).where(TimeEntryORM.id == uuid_val)
        result = await self._session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        if orm_model is None:
            raise EntityNotFoundException(entity_type="TimeEntry", id=aggregate.id)

        updated_orm = self._mapper.to_orm(aggregate)
        for column in TimeEntryORM.__table__.columns:
            col_name = column.name
            if col_name in ("id", "created_at"):
                continue
            setattr(orm_model, col_name, getattr(updated_orm, col_name, None))

        # Синхронизация time_logs: delete + insert
        await self._session.execute(
            TimeEntryTimeLogORM.__table__.delete().where(
                TimeEntryTimeLogORM.time_entry_id == uuid_val
            )
        )
        for log in list(orm_model.time_logs):
            self._session.expunge(log)
        for log_orm in updated_orm.time_logs:
            self._session.add(log_orm)

        # Синхронизация tag links
        await self._sync_tag_links(uuid_val, aggregate.tag_ids)

        await self._session.flush()
        return aggregate

    async def get_by_id(self, id: Id) -> TimeEntry | None:
        uuid_val = self._mapper._map_uuid(id)
        stmt = select(TimeEntryORM).where(TimeEntryORM.id == uuid_val)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        if orm is None:
            return None
        return await self._to_domain_with_tags(orm)

    # ------------------------------------------------------------------
    # Специфичные методы
    # ------------------------------------------------------------------

    async def get_by_user(self, user_id: Id) -> list[TimeEntry]:
        uuid_val = self._mapper._map_uuid(user_id)
        stmt = select(TimeEntryORM).where(TimeEntryORM.user_id == uuid_val)
        result = await self._session.execute(stmt)
        return await self._to_domain_list_with_tags(list(result.scalars().all()))

    async def get_by_user_and_date(self, user_id: Id, entry_date: date_type) -> list[TimeEntry]:
        uuid_val = self._mapper._map_uuid(user_id)
        stmt = select(TimeEntryORM).where(
            and_(
                TimeEntryORM.user_id == uuid_val,
                TimeEntryORM.entry_date == entry_date,
            )
        )
        result = await self._session.execute(stmt)
        return await self._to_domain_list_with_tags(list(result.scalars().all()))

    async def get_by_task(self, task_id: Id) -> list[TimeEntry]:
        uuid_val = self._mapper._map_uuid(task_id)
        stmt = select(TimeEntryORM).where(TimeEntryORM.task_id == uuid_val)
        result = await self._session.execute(stmt)
        return await self._to_domain_list_with_tags(list(result.scalars().all()))

    async def get_by_project(self, project_id: Id) -> list[TimeEntry]:
        uuid_val = self._mapper._map_uuid(project_id)
        stmt = select(TimeEntryORM).where(TimeEntryORM.project_id == uuid_val)
        result = await self._session.execute(stmt)
        return await self._to_domain_list_with_tags(list(result.scalars().all()))

    async def get_by_epic(self, epic_id: Id) -> list[TimeEntry]:
        uuid_val = self._mapper._map_uuid(epic_id)
        stmt = select(TimeEntryORM).where(TimeEntryORM.epic_id == uuid_val)
        result = await self._session.execute(stmt)
        return await self._to_domain_list_with_tags(list(result.scalars().all()))

    async def get_by_workspace(self, workspace_id: Id) -> list[TimeEntry]:
        uuid_val = self._mapper._map_uuid(workspace_id)
        stmt = select(TimeEntryORM).where(TimeEntryORM.workspace_id == uuid_val)
        result = await self._session.execute(stmt)
        return await self._to_domain_list_with_tags(list(result.scalars().all()))

    async def get_running_timer(self, user_id: Id) -> TimeEntry | None:
        uuid_val = self._mapper._map_uuid(user_id)
        stmt = select(TimeEntryORM).where(
            and_(
                TimeEntryORM.user_id == uuid_val,
                TimeEntryORM.timer_state.in_([TimerState.RUNNING.value, TimerState.PAUSED.value]),
            )
        )
        result = await self._session.execute(stmt)
        orm = result.scalars().first()
        if orm is None:
            return None
        return await self._to_domain_with_tags(orm)

    async def get_by_status(self, workspace_id: Id, status: TimeEntryStatus) -> list[TimeEntry]:
        uuid_val = self._mapper._map_uuid(workspace_id)
        stmt = select(TimeEntryORM).where(
            and_(
                TimeEntryORM.workspace_id == uuid_val,
                TimeEntryORM.status == status.value,
            )
        )
        result = await self._session.execute(stmt)
        return await self._to_domain_list_with_tags(list(result.scalars().all()))

    async def get_submitted_for_approval(self, workspace_id: Id) -> list[TimeEntry]:
        return await self.get_by_status(workspace_id, TimeEntryStatus.SUBMITTED)

    async def get_by_category(self, category_id: Id) -> list[TimeEntry]:
        uuid_val = self._mapper._map_uuid(category_id)
        stmt = select(TimeEntryORM).where(TimeEntryORM.category_id == uuid_val)
        result = await self._session.execute(stmt)
        return await self._to_domain_list_with_tags(list(result.scalars().all()))

    async def sum_duration_by_user(self, user_id: Id, start: date_type, end: date_type) -> int:
        uuid_val = self._mapper._map_uuid(user_id)
        stmt = select(func.coalesce(func.sum(TimeEntryORM.duration_seconds), 0)).where(
            and_(
                TimeEntryORM.user_id == uuid_val,
                TimeEntryORM.entry_date >= start,
                TimeEntryORM.entry_date <= end,
            )
        )
        result = await self._session.execute(stmt)
        return int(result.scalar_one())

    async def sum_duration_by_project(
        self, project_id: Id, start: date_type, end: date_type
    ) -> int:
        uuid_val = self._mapper._map_uuid(project_id)
        stmt = select(func.coalesce(func.sum(TimeEntryORM.duration_seconds), 0)).where(
            and_(
                TimeEntryORM.project_id == uuid_val,
                TimeEntryORM.entry_date >= start,
                TimeEntryORM.entry_date <= end,
            )
        )
        result = await self._session.execute(stmt)
        return int(result.scalar_one())

    async def search(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[TimeEntry]:
        stmt = select(TimeEntryORM)
        if filters:
            workspace_id = filters.get("workspace_id")
            if workspace_id:
                ws_uuid = self._mapper._map_uuid(Id.from_string(workspace_id) if isinstance(workspace_id, str) else workspace_id)
                stmt = stmt.where(TimeEntryORM.workspace_id == ws_uuid)
            user_id = filters.get("user_id")
            if user_id:
                u_uuid = self._mapper._map_uuid(Id.from_string(user_id) if isinstance(user_id, str) else user_id)
                stmt = stmt.where(TimeEntryORM.user_id == u_uuid)
            project_id = filters.get("project_id")
            if project_id:
                p_uuid = self._mapper._map_uuid(Id.from_string(project_id) if isinstance(project_id, str) else project_id)
                stmt = stmt.where(TimeEntryORM.project_id == p_uuid)
            task_id = filters.get("task_id")
            if task_id:
                t_uuid = self._mapper._map_uuid(Id.from_string(task_id) if isinstance(task_id, str) else task_id)
                stmt = stmt.where(TimeEntryORM.task_id == t_uuid)
            status = filters.get("status")
            if status:
                stmt = stmt.where(TimeEntryORM.status == status)
            entry_date_from = filters.get("entry_date_from")
            if entry_date_from:
                stmt = stmt.where(
                    TimeEntryORM.entry_date >= date_type.fromisoformat(entry_date_from)
                )
            entry_date_to = filters.get("entry_date_to")
            if entry_date_to:
                stmt = stmt.where(
                    TimeEntryORM.entry_date <= date_type.fromisoformat(entry_date_to)
                )
        stmt = stmt.offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return await self._to_domain_list_with_tags(list(result.scalars().all()))
