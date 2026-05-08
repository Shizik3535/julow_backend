from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.exceptions.entity_not_found_exception import (
    EntityNotFoundException,
)
from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import (
    SqlAlchemyRepository,
)

from app.context.communication.domain.aggregates.meeting import Meeting
from app.context.communication.domain.repositories.meeting_repository import (
    MeetingRepository,
)
from app.context.communication.domain.value_objects.meeting_status import MeetingStatus
from app.context.communication.infrastructure.persistence.mappers.meeting_mapper import (
    MeetingMapper,
)
from app.context.communication.infrastructure.persistence.orm_models.meeting_orm import (
    MeetingORM,
    MeetingParticipantORM,
)


class SqlMeetingRepository(
    SqlAlchemyRepository[Meeting, MeetingORM],
    MeetingRepository,
):
    """SQLAlchemy-реализация MeetingRepository."""

    def __init__(self, session: AsyncSession, mapper: MeetingMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=MeetingORM)
        self._mapper: MeetingMapper = mapper

    async def update(self, aggregate: Meeting) -> Meeting:
        uuid_value = self._mapper._map_uuid(aggregate.id)
        stmt = select(MeetingORM).where(MeetingORM.id == uuid_value)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        if orm is None:
            raise EntityNotFoundException(entity_type="Meeting", id=aggregate.id)

        orm.title = aggregate.title
        orm.description = aggregate.description.content if aggregate.description else None
        orm.description_format = (
            aggregate.description.format.value if aggregate.description else "markdown"
        )
        orm.meeting_type = aggregate.meeting_type.value
        orm.status = aggregate.status.value
        orm.scheduled_at = aggregate.scheduled_at
        orm.duration_minutes = aggregate.duration_minutes
        orm.location = aggregate.location
        orm.conference_provider = aggregate.conference_provider.value
        orm.conference_url = (
            str(aggregate.conference_url) if aggregate.conference_url else None
        )
        orm.conference_room_id = aggregate.conference_room_id
        orm.project_id = (
            self._mapper._map_uuid(aggregate.project_id) if aggregate.project_id else None
        )
        orm.workspace_id = self._mapper._map_uuid(aggregate.workspace_id)
        orm.organizer_id = self._mapper._map_uuid(aggregate.organizer_id)
        orm.recurrence_pattern = (
            aggregate.recurrence.pattern.value if aggregate.recurrence else None
        )
        orm.recurrence_interval = (
            aggregate.recurrence.interval if aggregate.recurrence else None
        )
        orm.recurrence_end_date = (
            aggregate.recurrence.end_date if aggregate.recurrence else None
        )
        orm.recurrence_max_occurrences = (
            aggregate.recurrence.max_occurrences if aggregate.recurrence else None
        )
        orm.agenda = (
            [
                {
                    "text": item.text,
                    "duration_minutes": item.duration_minutes,
                    "owner_id": str(item.owner_id) if item.owner_id else None,
                }
                for item in aggregate.agenda.items
            ]
            if aggregate.agenda is not None
            else None
        )
        orm.updated_at = aggregate.updated_at

        orm.participants = [
            self._mapper._participant_to_orm(p, aggregate.id)
            for p in aggregate.participants
        ]
        orm.notes = [self._mapper._note_to_orm(n, aggregate.id) for n in aggregate.notes]
        orm.action_items = [
            self._mapper._action_item_to_orm(ai, aggregate.id)
            for ai in aggregate.action_items
        ]

        await self._session.flush()
        return aggregate

    # ------------------------------------------------------------------
    # MeetingRepository — query-методы
    # ------------------------------------------------------------------

    async def get_by_workspace(self, workspace_id: Id) -> list[Meeting]:
        ws = self._mapper._map_uuid(workspace_id)
        stmt = (
            select(MeetingORM)
            .where(MeetingORM.workspace_id == ws)
            .order_by(MeetingORM.scheduled_at.desc())
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_by_project(self, project_id: Id) -> list[Meeting]:
        p = self._mapper._map_uuid(project_id)
        stmt = (
            select(MeetingORM)
            .where(MeetingORM.project_id == p)
            .order_by(MeetingORM.scheduled_at.desc())
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_upcoming_by_participant(self, user_id: Id) -> list[Meeting]:
        u = self._mapper._map_uuid(user_id)
        stmt = (
            select(MeetingORM)
            .join(
                MeetingParticipantORM,
                MeetingParticipantORM.meeting_id == MeetingORM.id,
            )
            .where(
                MeetingParticipantORM.user_id == u,
                MeetingORM.status.in_(("scheduled", "in_progress")),
            )
            .order_by(MeetingORM.scheduled_at.asc())
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().unique().all()]

    async def get_by_organizer(self, organizer_id: Id) -> list[Meeting]:
        o = self._mapper._map_uuid(organizer_id)
        stmt = (
            select(MeetingORM)
            .where(MeetingORM.organizer_id == o)
            .order_by(MeetingORM.scheduled_at.desc())
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def get_by_status(
        self, workspace_id: Id, status: MeetingStatus
    ) -> list[Meeting]:
        ws = self._mapper._map_uuid(workspace_id)
        stmt = (
            select(MeetingORM)
            .where(
                MeetingORM.workspace_id == ws,
                MeetingORM.status == status.value,
            )
            .order_by(MeetingORM.scheduled_at.desc())
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def search(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[Meeting]:
        stmt = select(MeetingORM)
        if filters:
            for field_name, value in filters.items():
                col = getattr(MeetingORM, field_name, None)
                if col is not None:
                    stmt = stmt.where(col == value)
        stmt = (
            stmt.order_by(MeetingORM.scheduled_at.desc()).offset(offset).limit(limit)
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]
