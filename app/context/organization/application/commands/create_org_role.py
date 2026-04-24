from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.org_role_dto import OrgRoleDTO
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.domain.aggregates.org_role import OrgRole
from app.context.organization.domain.repositories.org_role_repository import OrgRoleRepository
from app.context.organization.domain.value_objects.org_role_scope import OrgRoleScope


class CreateOrgRoleCommand(BaseCommand):
    """
    Команда создания кастомной роли организации.

    Атрибуты:
        org_id: ID организации.
        name: Название роли.
        permissions: Список разрешений.
        scope: Область действия роли (ORG, DEPARTMENT, TEAM).
        description: Описание роли.
    """

    caller_id: str
    org_id: str
    name: str
    permissions: list[str]
    scope: str = "ORG"
    description: str | None = None


class CreateOrgRoleHandler(BaseCommandHandler[CreateOrgRoleCommand, OrgRoleDTO]):
    """
    Обработчик создания кастомной роли.

    Создаёт OrgRole AR с is_system=False, сохраняет.
    """

    REQUIRED_PERMISSION = "roles.write"

    def __init__(self, role_repo: OrgRoleRepository, org_permission_checker: OrgPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._role_repo = role_repo
        self._org_permission_checker = org_permission_checker
        self._event_bus = event_bus

    async def handle(self, command: CreateOrgRoleCommand) -> OrgRoleDTO:
        caller_id = Id.from_string(command.caller_id)
        org_id = Id.from_string(command.org_id)

        await self._org_permission_checker.require_permission(caller_id, org_id, self.REQUIRED_PERMISSION)
        role = OrgRole.create_custom(
            org_id=Id.from_string(command.org_id),
            name=command.name,
            permissions=command.permissions,
            scope=OrgRoleScope(command.scope),
            description=command.description,
        )

        await self._role_repo.add(role)
        await self._event_bus.publish_all(role.clear_domain_events())

        return OrgRoleDTO(
            id=str(role.id),
            org_id=str(role.org_id) if role.org_id else "",
            name=role.name,
            permissions=role.permissions,
            is_system=role.is_system,
            description=role.description,
            scope=role.scope.value,
            created_at=role.created_at,
            updated_at=role.updated_at,
        )
