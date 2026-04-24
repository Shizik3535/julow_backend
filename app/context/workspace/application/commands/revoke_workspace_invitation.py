from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.domain.exceptions.workspace_invitation_exceptions import InvitationNotFoundException
from app.context.workspace.domain.repositories.workspace_invitation_repository import WorkspaceInvitationRepository


class RevokeWorkspaceInvitationCommand(BaseCommand):
    """
    Команда отзыва приглашения в workspace.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        invitation_id: ID приглашения.
    """

    caller_id: str
    invitation_id: str


class RevokeWorkspaceInvitationHandler(BaseCommandHandler[RevokeWorkspaceInvitationCommand, None]):
    """Обработчик отзыва приглашения."""

    REQUIRED_PERMISSION = "members.invite"

    def __init__(
        self,
        invitation_repo: WorkspaceInvitationRepository,
        permission_checker: WorkspacePermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._invitation_repo = invitation_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: RevokeWorkspaceInvitationCommand) -> None:
        invitation = await self._invitation_repo.get_by_id(Id.from_string(command.invitation_id))
        if invitation is None:
            raise InvitationNotFoundException(command.invitation_id)

        await self._permission_checker.require_permission(
            user_id=Id.from_string(command.caller_id),
            workspace_id=invitation.workspace_id,
            permission=self.REQUIRED_PERMISSION,
        )

        invitation.revoke()
        await self._invitation_repo.update(invitation)
        await self._event_bus.publish_all(invitation.clear_domain_events())
