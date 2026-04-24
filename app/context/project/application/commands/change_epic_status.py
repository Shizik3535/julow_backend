from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.exceptions.epic_exceptions import EpicNotFoundException
from app.context.project.domain.repositories.epic_repository import EpicRepository
from app.context.project.domain.value_objects.epic_status import EpicStatus
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)


class ChangeEpicStatusCommand(BaseCommand):
    """
    Команда смены статуса эпика.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        epic_id: ID эпика.
        new_status: Новый статус (OPEN, IN_PROGRESS, DONE, CANCELLED).
    """

    caller_id: str
    epic_id: str
    new_status: str


class ChangeEpicStatusHandler(BaseCommandHandler[ChangeEpicStatusCommand, None]):
    """Обработчик смены статуса эпика."""


    REQUIRED_PERMISSION = "epics.write"

    def __init__(self, epic_repo: EpicRepository, permission_checker: ProjectPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._epic_repo = epic_repo
        self._event_bus = event_bus
        self._permission_checker = permission_checker

    async def handle(self, command: ChangeEpicStatusCommand) -> None:
        epic = await self._epic_repo.get_by_id(Id.from_string(command.epic_id))
        if epic is None:
            raise EpicNotFoundException(command.epic_id)


        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            project_id=epic.project_id,
            permission=self.REQUIRED_PERMISSION,
        )
        epic.change_status(EpicStatus(command.new_status))
        await self._epic_repo.update(epic)
        await self._event_bus.publish_all(epic.clear_domain_events())
