from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.domain.exceptions.organization_exceptions import OrganizationNotFoundException
from app.context.organization.domain.repositories.organization_repository import OrganizationRepository
from app.context.organization.domain.value_objects.membership_policy import MembershipPolicy


class UpdateMembershipPolicyCommand(BaseCommand):
    """
    Команда обновления политики членства.

    Атрибуты:
        org_id: ID организации.
        allow_invitation_links: Разрешить ссылки-приглашения.
        default_role: Роль по умолчанию для новых участников.
        require_approval: Приглашения требуют подтверждения.
        max_members: Максимум участников.
        allowed_email_domains: Разрешённые домены email.
    """

    caller_id: str
    org_id: str
    allow_invitation_links: bool = True
    default_role: str = "member"
    require_approval: bool = False
    max_members: int | None = None
    allowed_email_domains: list[str] = []


class UpdateMembershipPolicyHandler(BaseCommandHandler[UpdateMembershipPolicyCommand, None]):
    """
    Обработчик обновления политики членства.

    Конвертирует примитивы в VO MembershipPolicy, вызывает
    доменный метод update_membership_policy.
    """

    REQUIRED_PERMISSION = "org.settings.write"

    def __init__(self, org_repo: OrganizationRepository, org_permission_checker: OrgPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._org_repo = org_repo
        self._org_permission_checker = org_permission_checker
        self._event_bus = event_bus

    async def handle(self, command: UpdateMembershipPolicyCommand) -> None:
        caller_id = Id.from_string(command.caller_id)
        org_id = Id.from_string(command.org_id)

        org = await self._org_repo.get_by_id(org_id)
        if org is None:
            raise OrganizationNotFoundException(command.org_id)
        await self._org_permission_checker.require_permission(caller_id, org_id, self.REQUIRED_PERMISSION)

        policy = MembershipPolicy(
            allow_invitation_links=command.allow_invitation_links,
            default_role=command.default_role,
            require_approval=command.require_approval,
            max_members=command.max_members,
            allowed_email_domains=command.allowed_email_domains,
        )

        org.update_membership_policy(policy)
        await self._org_repo.update(org)
        await self._event_bus.publish_all(org.clear_domain_events())
