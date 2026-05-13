from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.exceptions.entity_not_found_exception import EntityNotFoundException
from app.shared.domain.value_objects.id_vo import Id

from app.context.timetracking.application.ports.authorization.timetracking_permission_checker_port import (
    TimeTrackingPermissionCheckerPort,
)
from app.context.timetracking.domain.repositories.time_entry_tag_repository import (
    TimeEntryTagRepository,
)


class DeleteTimeEntryTagCommand(BaseCommand):
    """Команда удаления тега (soft delete)."""

    caller_id: str
    tag_id: str


class DeleteTimeEntryTagHandler(BaseCommandHandler[DeleteTimeEntryTagCommand, None]):
    """Удаление тега."""

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

    async def handle(self, command: DeleteTimeEntryTagCommand) -> None:
        tag = await self._repo.get_by_id(Id.from_string(command.tag_id))
        if tag is None:
            raise EntityNotFoundException(entity_type="TimeEntryTag", id=command.tag_id)
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=str(tag.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )

        tag.delete()
        await self._repo.update(tag)
        await self._event_bus.publish_all(tag.clear_domain_events())
