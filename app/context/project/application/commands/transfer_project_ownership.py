from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException
from app.context.project.domain.repositories.project_repository import ProjectRepository
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)


class TransferProjectOwnershipCommand(BaseCommand):
    """
    Команда передачи владения проектом.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        project_id: ID проекта.
        from_owner_id: ID текущего владельца.
        to_owner_id: ID нового владельца.
    """

    caller_id: str
    project_id: str
    from_owner_id: str
    to_owner_id: str


class TransferProjectOwnershipHandler(BaseCommandHandler[TransferProjectOwnershipCommand, None]):
    """Обработчик передачи владения проектом."""


    REQUIRED_PERMISSION = "project.*"

    def __init__(self, project_repo: ProjectRepository, permission_checker: ProjectPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._project_repo = project_repo
        self._event_bus = event_bus
        self._permission_checker = permission_checker

    async def handle(self, command: TransferProjectOwnershipCommand) -> None:
        project_id = Id.from_string(command.project_id)
        project = await self._project_repo.get_by_id(project_id)
        if project is None:
            raise ProjectNotFoundException(command.project_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            project_id=project_id,
            permission=self.REQUIRED_PERMISSION,
        )

        project.transfer_ownership(
            from_id=Id.from_string(command.from_owner_id),
            to_id=Id.from_string(command.to_owner_id),
        )
        await self._project_repo.update(project)
        await self._event_bus.publish_all(project.clear_domain_events())
