from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.domain.exceptions.invitation_exceptions import InvitationNotFoundException
from app.context.organization.domain.repositories.invitation_repository import InvitationRepository


class RevokeInvitationCommand(BaseCommand):
    """
    Команда отзыва приглашения.

    Атрибуты:
        invitation_id: ID приглашения.
    """

    caller_id: str
    org_id: str
    invitation_id: str


class RevokeInvitationHandler(BaseCommandHandler[RevokeInvitationCommand, None]):
    """
    Обработчик отзыва приглашения.

    Загружает Invitation, вызывает revoke, сохраняет.
    """

    REQUIRED_PERMISSION = "members.invite"

    def __init__(
        self,
        invitation_repo: InvitationRepository,
        org_permission_checker: OrgPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._invitation_repo = invitation_repo
        self._org_permission_checker = org_permission_checker
        self._event_bus = event_bus

    async def handle(self, command: RevokeInvitationCommand) -> None:
        caller_id = Id.from_string(command.caller_id)
        org_id = Id.from_string(command.org_id)

        invitation = await self._invitation_repo.get_by_id(Id.from_string(command.invitation_id))
        if invitation is None:
            raise InvitationNotFoundException(command.invitation_id)
        await self._org_permission_checker.require_permission(caller_id, org_id, self.REQUIRED_PERMISSION)

        invitation.revoke()
        await self._invitation_repo.update(invitation)
        await self._event_bus.publish_all(invitation.clear_domain_events())
