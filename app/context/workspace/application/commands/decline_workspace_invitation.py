from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.application.ports.integration.inboard.identity_user_port import IdentityUserPort
from app.context.workspace.domain.exceptions.workspace_invitation_exceptions import InvitationNotFoundException
from app.context.workspace.domain.repositories.workspace_invitation_repository import WorkspaceInvitationRepository


class DeclineWorkspaceInvitationCommand(BaseCommand):
    """
    Команда отклонения приглашения в workspace.

    Атрибуты:
        invitation_id: ID приглашения.
        user_id: ID пользователя, отклоняющего приглашение.
    """

    invitation_id: str
    user_id: str


class DeclineWorkspaceInvitationHandler(BaseCommandHandler[DeclineWorkspaceInvitationCommand, None]):
    """
    Обработчик отклонения приглашения.

    Авторизация: отклонить может только адресат приглашения
    (email совпадает) ИЛИ пользователь с разрешением members.invite.
    """

    REQUIRED_PERMISSION = "members.invite"

    def __init__(
        self,
        invitation_repo: WorkspaceInvitationRepository,
        identity_port: IdentityUserPort,
        permission_checker: WorkspacePermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._invitation_repo = invitation_repo
        self._identity_port = identity_port
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: DeclineWorkspaceInvitationCommand) -> None:
        invitation = await self._invitation_repo.get_by_id(Id.from_string(command.invitation_id))
        if invitation is None:
            raise InvitationNotFoundException(command.invitation_id)

        # Проверка: адресат приглашения (email совпадает) или members.invite
        is_invitee = False
        if invitation.email is not None:
            user_data = await self._identity_port.get_user(command.user_id)
            if user_data and user_data.get("email") == str(invitation.email):
                is_invitee = True

        if not is_invitee:
            await self._permission_checker.require_permission(
                user_id=Id.from_string(command.user_id),
                workspace_id=invitation.workspace_id,
                permission=self.REQUIRED_PERMISSION,
            )

        invitation.decline(user_id=Id.from_string(command.user_id))
        await self._invitation_repo.update(invitation)
        await self._event_bus.publish_all(invitation.clear_domain_events())
