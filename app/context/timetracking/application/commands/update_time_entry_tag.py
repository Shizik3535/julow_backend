from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.exceptions.entity_not_found_exception import EntityNotFoundException
from app.shared.domain.value_objects.color_vo import Color
from app.shared.domain.value_objects.id_vo import Id

from app.context.timetracking.application.dto.mappers import tag_to_dto
from app.context.timetracking.application.dto.time_entry_tag_dto import TimeEntryTagDTO
from app.context.timetracking.application.ports.authorization.timetracking_permission_checker_port import (
    TimeTrackingPermissionCheckerPort,
)
from app.context.timetracking.domain.exceptions.category_exceptions import (
    DuplicateTimeEntryTagException,
)
from app.context.timetracking.domain.repositories.time_entry_tag_repository import (
    TimeEntryTagRepository,
)


class UpdateTimeEntryTagCommand(BaseCommand):
    """Команда обновления тега."""

    caller_id: str
    tag_id: str
    name: str | None = None
    color: str | None = None


class UpdateTimeEntryTagHandler(BaseCommandHandler[UpdateTimeEntryTagCommand, TimeEntryTagDTO]):
    """Обновление тега."""

    REQUIRED_PERMISSION = "time.admin"

    def __init__(
        self,
        tag_repo: TimeEntryTagRepository,
        permission_checker: TimeTrackingPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = tag_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: UpdateTimeEntryTagCommand) -> TimeEntryTagDTO:
        tag = await self._repo.get_by_id(Id.from_string(command.tag_id))
        if tag is None:
            raise EntityNotFoundException(entity_type="TimeEntryTag", id=command.tag_id)
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=str(tag.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )

        if command.name is not None and command.name != tag.name:
            existing = await self._repo.get_by_name(command.name, tag.workspace_id)
            if existing is not None and existing.id != tag.id:
                raise DuplicateTimeEntryTagException(name=command.name)

        tag.update(
            name=command.name,
            color=Color(value=command.color) if command.color else None,
        )
        await self._repo.update(tag)
        await self._event_bus.publish_all(tag.clear_domain_events())
        return tag_to_dto(tag)
