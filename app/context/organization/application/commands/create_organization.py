from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.organization_dto import OrganizationDTO
from app.context.organization.application.ports.integration.inboard.identity_user_port import IdentityUserPort
from app.context.organization.application.exceptions.membership_app_exceptions import UserNotFoundException
from app.context.organization.domain.aggregates.organization import Organization
from app.context.organization.domain.aggregates.org_membership import OrgMembership
from app.context.organization.domain.aggregates.org_role import OrgRole
from app.context.organization.domain.repositories.organization_repository import OrganizationRepository
from app.context.organization.domain.repositories.org_membership_repository import OrgMembershipRepository
from app.context.organization.domain.repositories.org_role_repository import OrgRoleRepository
from app.context.organization.domain.value_objects.org_role_scope import OrgRoleScope
from app.context.organization.infrastructure.persistence.seed.org_roles import SYSTEM_ORG_ROLES


class CreateOrganizationCommand(BaseCommand):
    """
    Команда создания организации.

    Атрибуты:
        owner_id: ID пользователя-владельца.
        name: Название организации.
    """

    owner_id: str
    name: str


class CreateOrganizationHandler(BaseCommandHandler[CreateOrganizationCommand, OrganizationDTO]):
    """
    Обработчик создания организации.

    Создаёт Organization AR, 4 системных OrgRole и OrgMembership AR
    (с владельцем как первым участником с ролью owner).
    Мульти-агрегатный паттерн: все агрегаты создаются в рамках одного use case.
    """

    def __init__(
        self,
        org_repo: OrganizationRepository,
        membership_repo: OrgMembershipRepository,
        org_role_repo: OrgRoleRepository,
        identity_port: IdentityUserPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._org_repo = org_repo
        self._membership_repo = membership_repo
        self._org_role_repo = org_role_repo
        self._identity_port = identity_port
        self._event_bus = event_bus

    async def handle(self, command: CreateOrganizationCommand) -> OrganizationDTO:
        owner_id = Id.from_string(command.owner_id)

        if not await self._identity_port.user_exists(command.owner_id):
            raise UserNotFoundException(command.owner_id)

        org = Organization.create(name=command.name, owner_id=owner_id)

        # Создаём 4 системных орг-ролей для данной организации
        owner_role: OrgRole | None = None
        for seed_role in SYSTEM_ORG_ROLES:
            role = OrgRole.create_custom(
                org_id=org.id,
                name=seed_role["name"],
                permissions=seed_role["permissions"],
                scope=OrgRoleScope(seed_role["scope"]),
                description=seed_role["description"],
            )
            # Системные роли в контексте организации помечаем is_system=True
            role.is_system = True
            await self._org_role_repo.add(role)
            if seed_role["name"] == "owner":
                owner_role = role

        membership = OrgMembership.create(
            org_id=org.id,
            owner_id=owner_id,
            owner_role_id=owner_role.id if owner_role else Id.generate(),
        )

        await self._org_repo.add(org)
        await self._membership_repo.add(membership)

        await self._event_bus.publish_all(org.clear_domain_events())
        await self._event_bus.publish_all(membership.clear_domain_events())

        return OrganizationDTO(
            id=str(org.id),
            name=org.name,
            status=org.status.value,
            owner_ids=[str(oid) for oid in org.owner_ids],
            personalization={},
            security_policy={},
            membership_policy={},
            created_at=org.created_at,
            updated_at=org.updated_at,
        )
