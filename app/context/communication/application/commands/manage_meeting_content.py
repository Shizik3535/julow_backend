"""Команды управления заметками и action items совещания."""

from __future__ import annotations

from datetime import date

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.rich_text_format import RichTextFormat
from app.shared.domain.value_objects.rich_text_vo import RichText

from app.context.communication.application.exceptions.authorization_exceptions import (
    NotMeetingParticipantException,
)
from app.context.communication.domain.exceptions.meeting_exceptions import (
    MeetingNotFoundException,
)
from app.context.communication.domain.repositories.meeting_repository import (
    MeetingRepository,
)


def _require_participant(meeting, caller_id: str) -> None:
    if not meeting.is_participant(Id.from_string(caller_id)):
        raise NotMeetingParticipantException()


class AddMeetingNoteCommand(BaseCommand):
    """Добавить заметку (только участник, на IN_PROGRESS/COMPLETED)."""

    caller_id: str
    meeting_id: str
    content: str | None = None
    content_format: str = "markdown"


class AddMeetingNoteHandler(BaseCommandHandler[AddMeetingNoteCommand, None]):
    def __init__(
        self,
        meeting_repo: MeetingRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = meeting_repo
        self._event_bus = event_bus

    async def handle(self, command: AddMeetingNoteCommand) -> None:
        meeting = await self._repo.get_by_id(Id.from_string(command.meeting_id))
        if meeting is None:
            raise MeetingNotFoundException(command.meeting_id)
        _require_participant(meeting, command.caller_id)
        content: RichText | None = None
        if command.content is not None:
            content = RichText(
                content=command.content,
                format=RichTextFormat(command.content_format),
            )
        meeting.add_note(content=content, author_id=Id.from_string(command.caller_id))
        await self._repo.update(meeting)
        await self._event_bus.publish_all(meeting.clear_domain_events())


class AddActionItemCommand(BaseCommand):
    """Добавить action item (только участник)."""

    caller_id: str
    meeting_id: str
    text: str
    assignee_id: str | None = None
    due_date: date | None = None


class AddActionItemHandler(BaseCommandHandler[AddActionItemCommand, None]):
    def __init__(
        self,
        meeting_repo: MeetingRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = meeting_repo
        self._event_bus = event_bus

    async def handle(self, command: AddActionItemCommand) -> None:
        meeting = await self._repo.get_by_id(Id.from_string(command.meeting_id))
        if meeting is None:
            raise MeetingNotFoundException(command.meeting_id)
        _require_participant(meeting, command.caller_id)
        meeting.add_action_item(
            text=command.text,
            assignee_id=(
                Id.from_string(command.assignee_id) if command.assignee_id else None
            ),
            due_date=command.due_date,
        )
        await self._repo.update(meeting)
        await self._event_bus.publish_all(meeting.clear_domain_events())


class CompleteActionItemCommand(BaseCommand):
    caller_id: str
    meeting_id: str
    action_item_id: str


class CompleteActionItemHandler(
    BaseCommandHandler[CompleteActionItemCommand, None]
):
    def __init__(
        self,
        meeting_repo: MeetingRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = meeting_repo
        self._event_bus = event_bus

    async def handle(self, command: CompleteActionItemCommand) -> None:
        meeting = await self._repo.get_by_id(Id.from_string(command.meeting_id))
        if meeting is None:
            raise MeetingNotFoundException(command.meeting_id)
        _require_participant(meeting, command.caller_id)
        meeting.complete_action_item(Id.from_string(command.action_item_id))
        await self._repo.update(meeting)
        await self._event_bus.publish_all(meeting.clear_domain_events())


class RemoveActionItemCommand(BaseCommand):
    caller_id: str
    meeting_id: str
    action_item_id: str


class RemoveActionItemHandler(BaseCommandHandler[RemoveActionItemCommand, None]):
    def __init__(
        self,
        meeting_repo: MeetingRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = meeting_repo
        self._event_bus = event_bus

    async def handle(self, command: RemoveActionItemCommand) -> None:
        meeting = await self._repo.get_by_id(Id.from_string(command.meeting_id))
        if meeting is None:
            raise MeetingNotFoundException(command.meeting_id)
        _require_participant(meeting, command.caller_id)
        meeting.remove_action_item(Id.from_string(command.action_item_id))
        await self._repo.update(meeting)
        await self._event_bus.publish_all(meeting.clear_domain_events())
