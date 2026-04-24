from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository


class RestoreWorkspaceCommand(BaseCommand):
    """
    Команда восстановления workspace из архива.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        workspace_id: ID workspace.
    """

    caller_id: str
    workspace_id: str


class RestoreWorkspaceHandler(BaseCommandHandler[RestoreWorkspaceCommand, None]):
    """Обработчик восстановления workspace из архива."""

    REQUIRED_PERMISSION = "ws.settings.write"

    def __init__(
        self,
        ws_repo: WorkspaceRepository,
        permission_checker: WorkspacePermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._ws_repo = ws_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: RestoreWorkspaceCommand) -> None:
        ws_id = Id.from_string(command.workspace_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            workspace_id=ws_id,
            permission=self.REQUIRED_PERMISSION,
        )
        ws = await self._ws_repo.get_by_id(ws_id)
        if ws is None:
            raise WorkspaceNotFoundException(command.workspace_id)

        ws.restore()
        await self._ws_repo.update(ws)
        await self._event_bus.publish_all(ws.clear_domain_events())
