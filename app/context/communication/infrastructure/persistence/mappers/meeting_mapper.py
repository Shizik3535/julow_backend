from __future__ import annotations

from app.shared.domain.value_objects.agenda_item import AgendaItem
from app.shared.domain.value_objects.agenda_vo import Agenda
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.rich_text_format import RichTextFormat
from app.shared.domain.value_objects.rich_text_vo import RichText
from app.shared.domain.value_objects.url_vo import Url
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.communication.domain.aggregates.meeting import Meeting
from app.context.communication.domain.entities.meeting_action_item import (
    MeetingActionItem,
)
from app.context.communication.domain.entities.meeting_note import MeetingNote
from app.context.communication.domain.entities.meeting_participant import (
    MeetingParticipant,
)
from app.context.communication.domain.value_objects.conference_provider import (
    ConferenceProvider,
)
from app.context.communication.domain.value_objects.meeting_status import MeetingStatus
from app.context.communication.domain.value_objects.meeting_type import MeetingType
from app.context.communication.domain.value_objects.recurrence_config import (
    RecurrenceConfig,
)
from app.context.communication.domain.value_objects.recurrence_pattern import (
    RecurrencePattern,
)
from app.context.communication.domain.value_objects.rsvp_status import RSVPStatus
from app.context.communication.infrastructure.persistence.orm_models.meeting_orm import (
    MeetingActionItemORM,
    MeetingNoteORM,
    MeetingORM,
    MeetingParticipantORM,
)


class MeetingMapper(BaseMapper[Meeting, MeetingORM]):
    """Data Mapper: Meeting ↔ MeetingORM."""

    def to_domain(self, orm: MeetingORM) -> Meeting:
        description: RichText | None = None
        if orm.description is not None:
            description = RichText(
                content=orm.description,
                format=RichTextFormat(orm.description_format),
            )

        recurrence: RecurrenceConfig | None = None
        if orm.recurrence_pattern is not None:
            recurrence = RecurrenceConfig(
                pattern=RecurrencePattern(orm.recurrence_pattern),
                interval=orm.recurrence_interval or 1,
                end_date=orm.recurrence_end_date,
                max_occurrences=orm.recurrence_max_occurrences,
            )

        agenda: Agenda | None = None
        if orm.agenda:
            items = [
                AgendaItem(
                    text=item.get("text", "") if isinstance(item, dict) else str(item),
                    duration_minutes=(
                        item.get("duration_minutes") if isinstance(item, dict) else None
                    ),
                    owner_id=(
                        Id.from_string(item["owner_id"])
                        if isinstance(item, dict) and item.get("owner_id")
                        else None
                    ),
                )
                for item in orm.agenda
            ]
            agenda = Agenda(items=items)

        participants = [
            MeetingParticipant(
                id=self._map_id(p.id),
                user_id=self._map_id(p.user_id),
                is_mandatory=p.is_mandatory,
                rsvp_status=RSVPStatus(p.rsvp_status),
                joined_at=p.participant_joined_at,
            )
            for p in (orm.participants or [])
        ]
        notes = [
            MeetingNote(
                id=self._map_id(n.id),
                author_id=self._map_id(n.author_id),
                content=(
                    RichText(content=n.content, format=RichTextFormat(n.content_format))
                    if n.content is not None
                    else None
                ),
                created_at=n.note_created_at,
            )
            for n in (orm.notes or [])
        ]
        action_items = [
            MeetingActionItem(
                id=self._map_id(ai.id),
                text=ai.text,
                assignee_id=self._map_id(ai.assignee_id) if ai.assignee_id else None,
                due_date=ai.due_date,
                is_completed=ai.is_completed,
            )
            for ai in (orm.action_items or [])
        ]

        return Meeting(
            id=self._map_id(orm.id),
            title=orm.title,
            description=description,
            meeting_type=MeetingType(orm.meeting_type),
            status=MeetingStatus(orm.status),
            scheduled_at=orm.scheduled_at,
            duration_minutes=orm.duration_minutes,
            location=orm.location,
            conference_provider=ConferenceProvider(orm.conference_provider),
            conference_url=Url(value=orm.conference_url) if orm.conference_url else None,
            conference_room_id=orm.conference_room_id,
            project_id=self._map_id(orm.project_id) if orm.project_id else None,
            workspace_id=self._map_id(orm.workspace_id),
            organizer_id=self._map_id(orm.organizer_id),
            participants=participants,
            notes=notes,
            action_items=action_items,
            recurrence=recurrence,
            agenda=agenda,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    def to_orm(self, aggregate: Meeting) -> MeetingORM:
        orm = MeetingORM(
            id=self._map_uuid(aggregate.id),
            title=aggregate.title,
            description=(
                aggregate.description.content if aggregate.description else None
            ),
            description_format=(
                aggregate.description.format.value
                if aggregate.description
                else "markdown"
            ),
            meeting_type=aggregate.meeting_type.value,
            status=aggregate.status.value,
            scheduled_at=aggregate.scheduled_at,
            duration_minutes=aggregate.duration_minutes,
            location=aggregate.location,
            conference_provider=aggregate.conference_provider.value,
            conference_url=(
                str(aggregate.conference_url) if aggregate.conference_url else None
            ),
            conference_room_id=aggregate.conference_room_id,
            project_id=(
                self._map_uuid(aggregate.project_id) if aggregate.project_id else None
            ),
            workspace_id=self._map_uuid(aggregate.workspace_id),
            organizer_id=self._map_uuid(aggregate.organizer_id),
            recurrence_pattern=(
                aggregate.recurrence.pattern.value if aggregate.recurrence else None
            ),
            recurrence_interval=(
                aggregate.recurrence.interval if aggregate.recurrence else None
            ),
            recurrence_end_date=(
                aggregate.recurrence.end_date if aggregate.recurrence else None
            ),
            recurrence_max_occurrences=(
                aggregate.recurrence.max_occurrences if aggregate.recurrence else None
            ),
            agenda=(
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
            ),
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
        orm.participants = [
            self._participant_to_orm(p, aggregate.id) for p in aggregate.participants
        ]
        orm.notes = [self._note_to_orm(n, aggregate.id) for n in aggregate.notes]
        orm.action_items = [
            self._action_item_to_orm(ai, aggregate.id) for ai in aggregate.action_items
        ]
        return orm

    def _participant_to_orm(
        self, p: MeetingParticipant, meeting_id: Id
    ) -> MeetingParticipantORM:
        return MeetingParticipantORM(
            id=self._map_uuid(p.id),
            meeting_id=self._map_uuid(meeting_id),
            user_id=self._map_uuid(p.user_id),
            is_mandatory=p.is_mandatory,
            rsvp_status=p.rsvp_status.value,
            participant_joined_at=p.joined_at,
        )

    def _note_to_orm(self, n: MeetingNote, meeting_id: Id) -> MeetingNoteORM:
        return MeetingNoteORM(
            id=self._map_uuid(n.id),
            meeting_id=self._map_uuid(meeting_id),
            author_id=self._map_uuid(n.author_id),
            content=n.content.content if n.content else None,
            content_format=n.content.format.value if n.content else "markdown",
            note_created_at=n.created_at,
        )

    def _action_item_to_orm(
        self, ai: MeetingActionItem, meeting_id: Id
    ) -> MeetingActionItemORM:
        return MeetingActionItemORM(
            id=self._map_uuid(ai.id),
            meeting_id=self._map_uuid(meeting_id),
            text=ai.text,
            assignee_id=self._map_uuid(ai.assignee_id) if ai.assignee_id else None,
            due_date=ai.due_date,
            is_completed=ai.is_completed,
        )
