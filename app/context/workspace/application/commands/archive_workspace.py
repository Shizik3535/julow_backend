from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import (
    CannotArchiveWithChildrenException,
    WorkspaceNotFoundException,
)
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository
from app.context.workspace.domain.value_objects.workspace_status import WorkspaceStatus


class ArchiveWorkspaceCommand(BaseCommand):
    """
    Команда архивирования workspace.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        workspace_id: ID workspace.
    """

    caller_id: str
    workspace_id: str


class ArchiveWorkspaceHandler(BaseCommandHandler[ArchiveWorkspaceCommand, None]):
    """
    Обработчик архивирования workspace.

    Проверяет отсутствие активных дочерних workspace,
    затем вызывает archive.
    """

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

    async def handle(self, command: ArchiveWorkspaceCommand) -> None:
        ws_id = Id.from_string(command.workspace_id)
        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            workspace_id=ws_id,
            permission=self.REQUIRED_PERMISSION,
        )
        ws = await self._ws_repo.get_by_id(ws_id)
        if ws is None:
            raise WorkspaceNotFoundException(command.workspace_id)

        children = await self._ws_repo.get_children(ws_id)
        active_children = [c for c in children if c.status == WorkspaceStatus.ACTIVE]
        if active_children:
            raise CannotArchiveWithChildrenException()

        ws.archive()
        await self._ws_repo.update(ws)
        await self._event_bus.publish_all(ws.clear_domain_events())
