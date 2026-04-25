from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.exceptions.membership_app_exceptions import (
    MemberAlreadyExistsException,
    UserNotFoundException,
)
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.application.ports.integration.inboard.identity_user_port import IdentityUserPort
from app.context.organization.domain.exceptions.organization_exceptions import OrganizationNotFoundException
from app.context.organization.domain.exceptions.org_role_exceptions import OrgRoleNotFoundException
from app.context.organization.domain.repositories.org_membership_repository import OrgMembershipRepository
from app.context.organization.domain.repositories.org_role_repository import OrgRoleRepository
from app.context.organization.domain.repositories.organization_repository import OrganizationRepository


class AddOrgMemberCommand(BaseCommand):
    """
    Команда добавления участника в организацию.

    Атрибуты:
        org_id: ID организации.
        user_id: ID пользователя.
        role_id: ID роли (None — используется default_role из MembershipPolicy).
        invited_by: ID пригласившего.
        display_name: Отображаемое имя.
    """

    caller_id: str
    org_id: str
    user_id: str
    role_id: str | None = None
    invited_by: str | None = None
    display_name: str | None = None


class AddOrgMemberHandler(BaseCommandHandler[AddOrgMemberCommand, None]):
    """
    Обработчик добавления участника в организацию.

    Проверяет существование пользователя через IdentityUserPort,
    проверяет отсутствие дубликата, добавляет в OrgMembership.
    Если role_id не указан — использует default_role из MembershipPolicy организации.
    """

    REQUIRED_PERMISSION = "members.write"

    def __init__(
        self,
        membership_repo: OrgMembershipRepository,
        org_repo: OrganizationRepository,
        org_role_repo: OrgRoleRepository,
        identity_port: IdentityUserPort,
        org_permission_checker: OrgPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._membership_repo = membership_repo
        self._org_repo = org_repo
        self._org_role_repo = org_role_repo
        self._identity_port = identity_port
        self._org_permission_checker = org_permission_checker
        self._event_bus = event_bus

    async def handle(self, command: AddOrgMemberCommand) -> None:
        caller_id = Id.from_string(command.caller_id)
        org_id = Id.from_string(command.org_id)
        user_id = Id.from_string(command.user_id)

        membership = await self._membership_repo.get_by_org_id(org_id)
        if membership is None:
            raise OrganizationNotFoundException(command.org_id)
        await self._org_permission_checker.require_permission(caller_id, org_id, self.REQUIRED_PERMISSION)

        if not await self._identity_port.user_exists(command.user_id):
            raise UserNotFoundException(command.user_id)

        existing = membership._find_member(user_id)
        if existing is not None:
            raise MemberAlreadyExistsException(command.user_id, command.org_id)

        # Резолвим role_id: явный или default_role из MembershipPolicy
        if command.role_id is not None:
            role_id = Id.from_string(command.role_id)
        else:
            org = await self._org_repo.get_by_id(org_id)
            if org is None:
                raise OrganizationNotFoundException(command.org_id)
            default_role_name = org.membership_policy.default_role
            default_role = await self._org_role_repo.get_by_org_and_name(org_id, default_role_name)
            if default_role is None:
                raise OrgRoleNotFoundException(default_role_name)
            role_id = default_role.id

        membership.add_member(
            user_id=user_id,
            role_id=role_id,
            invited_by=Id.from_string(command.invited_by) if command.invited_by else None,
            display_name=command.display_name,
        )

        await self._membership_repo.update(membership)
        await self._event_bus.publish_all(membership.clear_domain_events())
