from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from app.context.workspace.domain.repositories.workspace_membership_repository import WorkspaceMembershipRepository
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository


class RemoveWorkspaceMemberCommand(BaseCommand):
    """
    Команда удаления участника из workspace.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        workspace_id: ID workspace.
        user_id: ID пользователя.
    """

    caller_id: str
    workspace_id: str
    user_id: str


class RemoveWorkspaceMemberHandler(BaseCommandHandler[RemoveWorkspaceMemberCommand, None]):
    """Обработчик удаления участника из workspace."""

    REQUIRED_PERMISSION = "members.write"

    def __init__(
        self,
        ws_repo: WorkspaceRepository,
        membership_repo: WorkspaceMembershipRepository,
        permission_checker: WorkspacePermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._ws_repo = ws_repo
        self._membership_repo = membership_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: RemoveWorkspaceMemberCommand) -> None:
        ws_id = Id.from_string(command.workspace_id)
        user_id = Id.from_string(command.user_id)

        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            workspace_id=ws_id,
            permission=self.REQUIRED_PERMISSION,
        )

        ws = await self._ws_repo.get_by_id(ws_id)
        if ws is None:
            raise WorkspaceNotFoundException(command.workspace_id)

        membership = await self._membership_repo.get_by_workspace_id(ws_id)
        if membership is None:
            raise WorkspaceNotFoundException(command.workspace_id)

        is_owner = user_id in ws.owner_ids
        membership.remove_member(user_id=user_id, is_owner=is_owner)
        await self._membership_repo.update(membership)
        await self._event_bus.publish_all(membership.clear_domain_events())
