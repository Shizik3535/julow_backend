from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.invitation_dto import InvitationDTO, InvitationListDTO
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.domain.aggregates.invitation import Invitation
from app.context.organization.domain.exceptions.organization_exceptions import OrganizationNotFoundException
from app.context.organization.domain.repositories.invitation_repository import InvitationRepository
from app.context.organization.domain.repositories.organization_repository import OrganizationRepository


class SendBulkInvitationsCommand(BaseCommand):
    """
    Команда массовой отправки email-приглашений.

    Атрибуты:
        org_id: ID организации.
        emails: Список email приглашаемых.
        role_id: ID роли.
        invited_by: ID пригласившего.
    """

    caller_id: str
    org_id: str
    emails: list[str]
    role_id: str
    invited_by: str


class SendBulkInvitationsHandler(BaseCommandHandler[SendBulkInvitationsCommand, InvitationListDTO]):
    """
    Обработчик массовой отправки email-приглашений.

    Создаёт Invitation AR для каждого email, пропуская дубликаты.
    """

    REQUIRED_PERMISSION = "members.invite"

    def __init__(
        self,
        org_repo: OrganizationRepository,
        invitation_repo: InvitationRepository,
        org_permission_checker: OrgPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._org_repo = org_repo
        self._invitation_repo = invitation_repo
        self._org_permission_checker = org_permission_checker
        self._event_bus = event_bus

    async def handle(self, command: SendBulkInvitationsCommand) -> InvitationListDTO:
        caller_id = Id.from_string(command.caller_id)
        org_id = Id.from_string(command.org_id)

        await self._org_permission_checker.require_permission(caller_id, org_id, self.REQUIRED_PERMISSION)

        org = await self._org_repo.get_by_id(org_id)
        if org is None:
            raise OrganizationNotFoundException(command.org_id)

        pending = await self._invitation_repo.get_pending_by_org(org_id)
        existing_emails = {str(inv.email) for inv in pending if inv.email is not None}

        created: list[InvitationDTO] = []
        for email_str in command.emails:
            if email_str in existing_emails:
                continue

            invitation = Invitation.create_email_invitation(
                org_id=org_id,
                email=Email(email_str),
                role_id=Id.from_string(command.role_id),
                invited_by=Id.from_string(command.invited_by),
            )
            await self._invitation_repo.add(invitation)
            await self._event_bus.publish_all(invitation.clear_domain_events())

            created.append(
                InvitationDTO(
                    id=str(invitation.id),
                    org_id=str(invitation.org_id),
                    email=email_str,
                    link=None,
                    role_id=str(invitation.role_id),
                    invited_by=str(invitation.invited_by),
                    invited_at=invitation.invited_at,
                    status=invitation.status.value,
                    approved_by=None,
                    created_at=invitation.created_at,
                    updated_at=invitation.updated_at,
                )
            )

        return InvitationListDTO(items=created, total=len(created))
