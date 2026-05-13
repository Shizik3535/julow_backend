from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.color_vo import Color
from app.shared.domain.value_objects.id_vo import Id

from app.context.timetracking.application.dto.mappers import tag_to_dto
from app.context.timetracking.application.dto.time_entry_tag_dto import TimeEntryTagDTO
from app.context.timetracking.application.exceptions.timetracking_app_exceptions import (
    TimeEntryWorkspaceNotFoundException,
)
from app.context.timetracking.application.ports.authorization.timetracking_permission_checker_port import (
    TimeTrackingPermissionCheckerPort,
)
from app.context.timetracking.application.ports.integration.inboard.workspace_port import (
    WorkspacePort,
)
from app.context.timetracking.domain.aggregates.time_entry_tag import TimeEntryTag
from app.context.timetracking.domain.exceptions.category_exceptions import (
    DuplicateTimeEntryTagException,
)
from app.context.timetracking.domain.repositories.time_entry_tag_repository import (
    TimeEntryTagRepository,
)


class CreateTimeEntryTagCommand(BaseCommand):
    """Команда создания тега записи времени."""

    caller_id: str
    workspace_id: str
    name: str
    color: str | None = None


class CreateTimeEntryTagHandler(
    BaseCommandHandler[CreateTimeEntryTagCommand, TimeEntryTagDTO]
):
    """Создание тега. Уникальность имени в пределах workspace."""

    REQUIRED_PERMISSION = "time.admin"

    def __init__(
        self,
        tag_repo: TimeEntryTagRepository,
        permission_checker: TimeTrackingPermissionCheckerPort,
        workspace_port: WorkspacePort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = tag_repo
        self._permission_checker = permission_checker
        self._workspace_port = workspace_port
        self._event_bus = event_bus

    async def handle(self, command: CreateTimeEntryTagCommand) -> TimeEntryTagDTO:
        if not await self._workspace_port.workspace_exists(command.workspace_id):
            raise TimeEntryWorkspaceNotFoundException(command.workspace_id)
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=command.workspace_id,
            permission=self.REQUIRED_PERMISSION,
        )

        workspace_id = Id.from_string(command.workspace_id)
        existing = await self._repo.get_by_name(command.name, workspace_id)
        if existing is not None:
            raise DuplicateTimeEntryTagException(name=command.name)

        tag = TimeEntryTag.create(
            workspace_id=Id.from_string(command.workspace_id),
            name=command.name,
            color=Color(value=command.color) if command.color else None,
        )
        await self._repo.add(tag)
        await self._event_bus.publish_all(tag.clear_domain_events())
        return tag_to_dto(tag)
