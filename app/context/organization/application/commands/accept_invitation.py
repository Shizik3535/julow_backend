from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.exceptions.membership_app_exceptions import UserNotFoundException
from app.context.organization.application.ports.integration.inboard.identity_user_port import IdentityUserPort
from app.context.organization.domain.exceptions.invitation_exceptions import InvitationNotFoundException
from app.context.organization.domain.exceptions.organization_exceptions import OrganizationNotFoundException
from app.context.organization.domain.repositories.invitation_repository import InvitationRepository
from app.context.organization.domain.repositories.org_membership_repository import OrgMembershipRepository


class AcceptInvitationCommand(BaseCommand):
    """
    Команда принятия приглашения.

    Атрибуты:
        invitation_id: ID приглашения.
        user_id: ID принимающего пользователя.
    """

    invitation_id: str
    user_id: str


class AcceptInvitationHandler(BaseCommandHandler[AcceptInvitationCommand, None]):
    """
    Обработчик принятия приглашения.

    Мульти-агрегатный паттерн: принимает Invitation + добавляет
    пользователя в OrgMembership.
    """

    def __init__(
        self,
        invitation_repo: InvitationRepository,
        membership_repo: OrgMembershipRepository,
        identity_port: IdentityUserPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._invitation_repo = invitation_repo
        self._membership_repo = membership_repo
        self._identity_port = identity_port
        self._event_bus = event_bus

    async def handle(self, command: AcceptInvitationCommand) -> None:
        user_id = Id.from_string(command.user_id)

        if not await self._identity_port.user_exists(command.user_id):
            raise UserNotFoundException(command.user_id)

        invitation = await self._invitation_repo.get_by_id(Id.from_string(command.invitation_id))
        if invitation is None:
            raise InvitationNotFoundException(command.invitation_id)

        invitation.accept(user_id=user_id)

        if invitation.link is not None:
            invitation.increment_link_usage()

        membership = await self._membership_repo.get_by_org_id(invitation.org_id)
        if membership is None:
            raise OrganizationNotFoundException(str(invitation.org_id))

        membership.add_member(
            user_id=user_id,
            role_id=invitation.role_id,
            invited_by=invitation.invited_by,
        )

        await self._invitation_repo.update(invitation)
        await self._membership_repo.update(membership)
        await self._event_bus.publish_all(invitation.clear_domain_events())
        await self._event_bus.publish_all(membership.clear_domain_events())
