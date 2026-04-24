from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.exceptions.membership_app_exceptions import (
    MemberAlreadyExistsException,
    UserNotFoundException,
)
from app.context.workspace.application.ports.integration.inboard.identity_user_port import IdentityUserPort
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from app.context.workspace.domain.exceptions.workspace_invitation_exceptions import InvitationNotFoundException
from app.context.workspace.domain.repositories.workspace_invitation_repository import WorkspaceInvitationRepository
from app.context.workspace.domain.repositories.workspace_membership_repository import WorkspaceMembershipRepository
from app.context.workspace.domain.value_objects.member_source import MemberSource


class AcceptWorkspaceInvitationCommand(BaseCommand):
    """
    Команда принятия приглашения в workspace.

    Атрибуты:
        invitation_id: ID приглашения.
        user_id: ID пользователя, принимающего приглашение.
    """

    invitation_id: str
    user_id: str


class AcceptWorkspaceInvitationHandler(BaseCommandHandler[AcceptWorkspaceInvitationCommand, None]):
    """
    Обработчик принятия приглашения.

    Мульти-AR: invitation.accept() + membership.add_member().
    """

    def __init__(
        self,
        invitation_repo: WorkspaceInvitationRepository,
        membership_repo: WorkspaceMembershipRepository,
        identity_port: IdentityUserPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._invitation_repo = invitation_repo
        self._membership_repo = membership_repo
        self._identity_port = identity_port
        self._event_bus = event_bus

    async def handle(self, command: AcceptWorkspaceInvitationCommand) -> None:
        if not await self._identity_port.user_exists(command.user_id):
            raise UserNotFoundException(command.user_id)

        invitation = await self._invitation_repo.get_by_id(Id.from_string(command.invitation_id))
        if invitation is None:
            raise InvitationNotFoundException(command.invitation_id)

        user_id = Id.from_string(command.user_id)
        invitation.accept(user_id=user_id)

        if invitation.link is not None:
            invitation.increment_link_usage()

        membership = await self._membership_repo.get_by_workspace_id(invitation.workspace_id)
        if membership is None:
            raise WorkspaceNotFoundException(str(invitation.workspace_id))

        existing = membership._find_member(user_id)
        if existing is not None:
            raise MemberAlreadyExistsException(command.user_id, str(invitation.workspace_id))

        source = MemberSource.INVITATION_LINK if invitation.link else MemberSource.DIRECT
        membership.add_member(
            user_id=user_id,
            role_id=invitation.role_id,
            source=source,
            invited_by=invitation.invited_by,
        )

        await self._invitation_repo.update(invitation)
        await self._membership_repo.update(membership)
        await self._event_bus.publish_all(invitation.clear_domain_events())
        await self._event_bus.publish_all(membership.clear_domain_events())
