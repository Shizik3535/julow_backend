from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.timetracking.application.dto.mappers import time_entry_to_dto
from app.context.timetracking.application.dto.time_entry_dto import TimeEntryDTO
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


class StopTimerCommand(BaseCommand):
    """Команда остановки таймера и финализации записи."""

    caller_id: str
    entry_id: str


class StopTimerHandler(BaseCommandHandler[StopTimerCommand, TimeEntryDTO]):
    """Остановка таймера. Применяет правила округления при stop."""

    REQUIRED_PERMISSION = "time.write"

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

    async def handle(self, command: StopTimerCommand) -> TimeEntryDTO:
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

        entry.stop_timer()
        await self._repo.update(entry)
        await self._event_bus.publish_all(entry.clear_domain_events())
        return time_entry_to_dto(entry)
