from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.domain.exceptions.organization_exceptions import OrganizationNotFoundException
from app.context.organization.domain.repositories.org_membership_repository import OrgMembershipRepository


class ReactivateOrgMemberCommand(BaseCommand):
    """
    Команда реактивации участника организации.

    Атрибуты:
        org_id: ID организации.
        user_id: ID реактивируемого участника.
    """

    caller_id: str
    org_id: str
    user_id: str


class ReactivateOrgMemberHandler(BaseCommandHandler[ReactivateOrgMemberCommand, None]):
    """
    Обработчик реактивации участника организации.

    Загружает OrgMembership, вызывает reactivate_member, сохраняет.
    """

    REQUIRED_PERMISSION = "members.write"

    def __init__(
        self,
        membership_repo: OrgMembershipRepository,
        org_permission_checker: OrgPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._membership_repo = membership_repo
        self._org_permission_checker = org_permission_checker
        self._event_bus = event_bus

    async def handle(self, command: ReactivateOrgMemberCommand) -> None:
        caller_id = Id.from_string(command.caller_id)
        org_id = Id.from_string(command.org_id)

        await self._org_permission_checker.require_permission(caller_id, org_id, self.REQUIRED_PERMISSION)

        user_id = Id.from_string(command.user_id)

        membership = await self._membership_repo.get_by_org_id(org_id)
        if membership is None:
            raise OrganizationNotFoundException(command.org_id)

        membership.reactivate_member(user_id=user_id)
        await self._membership_repo.update(membership)
        await self._event_bus.publish_all(membership.clear_domain_events())
