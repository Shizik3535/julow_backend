from __future__ import annotations

import uuid
from datetime import datetime

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.invitation_dto import InvitationDTO
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.domain.aggregates.invitation import Invitation
from app.context.organization.domain.exceptions.organization_exceptions import OrganizationNotFoundException
from app.context.organization.domain.repositories.invitation_repository import InvitationRepository
from app.context.organization.domain.repositories.organization_repository import OrganizationRepository


class GenerateInvitationLinkCommand(BaseCommand):
    """
    Команда генерации ссылки-приглашения.

    Атрибуты:
        org_id: ID организации.
        role_id: ID роли.
        invited_by: ID создателя ссылки.
        expires_at: Время истечения (ISO формат или None).
        max_uses: Максимум использований.
    """

    caller_id: str
    org_id: str
    role_id: str
    invited_by: str
    expires_at: datetime | None = None
    max_uses: int | None = None


class GenerateInvitationLinkHandler(BaseCommandHandler[GenerateInvitationLinkCommand, InvitationDTO]):
    """
    Обработчик генерации ссылки-приглашения.

    Генерирует uuid4-токен, создаёт link-Invitation AR, сохраняет.
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

    async def handle(self, command: GenerateInvitationLinkCommand) -> InvitationDTO:
        caller_id = Id.from_string(command.caller_id)
        org_id = Id.from_string(command.org_id)

        await self._org_permission_checker.require_permission(caller_id, org_id, self.REQUIRED_PERMISSION)

        org = await self._org_repo.get_by_id(org_id)
        if org is None:
            raise OrganizationNotFoundException(command.org_id)

        token_value = str(uuid.uuid4())

        invitation = Invitation.create_link_invitation(
            org_id=org_id,
            role_id=Id.from_string(command.role_id),
            invited_by=Id.from_string(command.invited_by),
            token_value=token_value,
            expires_at=command.expires_at,
            max_uses=command.max_uses,
        )

        await self._invitation_repo.add(invitation)
        await self._event_bus.publish_all(invitation.clear_domain_events())

        link_data = {
            "value": token_value,
            "expires_at": command.expires_at.isoformat() if command.expires_at else None,
            "max_uses": command.max_uses,
            "used_count": 0,
        }

        return InvitationDTO(
            id=str(invitation.id),
            org_id=str(invitation.org_id),
            email=None,
            link=link_data,
            role_id=str(invitation.role_id),
            invited_by=str(invitation.invited_by),
            invited_at=invitation.invited_at,
            status=invitation.status.value,
            approved_by=None,
            created_at=invitation.created_at,
            updated_at=invitation.updated_at,
        )
