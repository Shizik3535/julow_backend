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


class TransferWorkspaceOwnershipCommand(BaseCommand):
    """
    Команда передачи владения workspace.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        workspace_id: ID workspace.
        from_id: ID текущего владельца.
        to_id: ID нового владельца.
    """

    caller_id: str
    workspace_id: str
    from_id: str
    to_id: str


class TransferWorkspaceOwnershipHandler(BaseCommandHandler[TransferWorkspaceOwnershipCommand, None]):
    """Обработчик передачи владения workspace."""

    REQUIRED_PERMISSION = "ws.*"

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

    async def handle(self, command: TransferWorkspaceOwnershipCommand) -> None:
        ws_id = Id.from_string(command.workspace_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            workspace_id=ws_id,
            permission=self.REQUIRED_PERMISSION,
        )
        ws = await self._ws_repo.get_by_id(ws_id)
        if ws is None:
            raise WorkspaceNotFoundException(command.workspace_id)

        ws.transfer_ownership(
            from_id=Id.from_string(command.from_id),
            to_id=Id.from_string(command.to_id),
        )
        await self._ws_repo.update(ws)
        await self._event_bus.publish_all(ws.clear_domain_events())
