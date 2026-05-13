from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.timetracking.application.exceptions.timetracking_app_exceptions import (
    TimeEntryNotOwnerException,
)
from app.context.timetracking.application.ports.authorization.timetracking_permission_checker_port import (
    TimeTrackingPermissionCheckerPort,
)
from app.context.timetracking.domain.exceptions.time_entry_exceptions import (
    TimeEntryNotFoundException,
)
from app.context.timetracking.domain.repositories.time_entry_repository import (
    TimeEntryRepository,
)


class DeleteTimeEntryCommand(BaseCommand):
    """Команда удаления записи времени (только в DRAFT)."""

    caller_id: str
    entry_id: str


class DeleteTimeEntryHandler(BaseCommandHandler[DeleteTimeEntryCommand, None]):
    """Удаление записи времени. Только владелец, только в DRAFT."""

    REQUIRED_PERMISSION = "time.delete"

    def __init__(
        self,
        time_entry_repo: TimeEntryRepository,
        permission_checker: TimeTrackingPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = time_entry_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: DeleteTimeEntryCommand) -> None:
        entry = await self._repo.get_by_id(Id.from_string(command.entry_id))
        if entry is None:
            raise TimeEntryNotFoundException(id=command.entry_id)
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=str(entry.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )
        if str(entry.user_id) != command.caller_id:
            raise TimeEntryNotOwnerException(command.entry_id)

        entry.delete()
        events = entry.clear_domain_events()
        await self._repo.delete(entry.id)
        await self._event_bus.publish_all(events)
