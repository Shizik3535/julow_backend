from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.domain.exceptions.organization_exceptions import OrganizationNotFoundException
from app.context.organization.domain.repositories.org_membership_repository import OrgMembershipRepository
from app.context.organization.domain.repositories.organization_repository import OrganizationRepository


class DeactivateOrgMemberCommand(BaseCommand):
    """
    Команда деактивации участника организации.

    Атрибуты:
        org_id: ID организации.
        user_id: ID деактивируемого участника.
    """

    caller_id: str
    org_id: str
    user_id: str


class DeactivateOrgMemberHandler(BaseCommandHandler[DeactivateOrgMemberCommand, None]):
    """
    Обработчик деактивации участника организации.

    Проверяет, является ли пользователь владельцем (через Organization AR),
    затем деактивирует в OrgMembership.
    """

    REQUIRED_PERMISSION = "members.write"

    def __init__(
        self,
        org_repo: OrganizationRepository,
        membership_repo: OrgMembershipRepository,
        org_permission_checker: OrgPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._org_repo = org_repo
        self._membership_repo = membership_repo
        self._org_permission_checker = org_permission_checker
        self._event_bus = event_bus

    async def handle(self, command: DeactivateOrgMemberCommand) -> None:
        caller_id = Id.from_string(command.caller_id)
        org_id = Id.from_string(command.org_id)
        user_id = Id.from_string(command.user_id)

        await self._org_permission_checker.require_permission(caller_id, org_id, self.REQUIRED_PERMISSION)

        org = await self._org_repo.get_by_id(org_id)
        if org is None:
            raise OrganizationNotFoundException(command.org_id)

        is_owner = user_id in org.owner_ids

        membership = await self._membership_repo.get_by_org_id(org_id)
        if membership is None:
            raise OrganizationNotFoundException(command.org_id)

        membership.deactivate_member(user_id=user_id, is_owner=is_owner)
        await self._membership_repo.update(membership)
        await self._event_bus.publish_all(membership.clear_domain_events())
