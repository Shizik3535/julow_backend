from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.domain.exceptions.org_role_exceptions import OrgRoleNotFoundException
from app.context.organization.domain.repositories.org_role_repository import OrgRoleRepository


class UpdateOrgRoleCommand(BaseCommand):
    """
    Команда обновления роли организации.

    Атрибуты:
        role_id: ID роли.
        permissions: Новый список разрешений.
        description: Новое описание.
    """

    caller_id: str
    org_id: str
    role_id: str
    permissions: list[str] | None = None
    description: str | None = None


class UpdateOrgRoleHandler(BaseCommandHandler[UpdateOrgRoleCommand, None]):
    """
    Обработчик обновления роли.

    Загружает OrgRole, вызывает update, сохраняет.
    """

    REQUIRED_PERMISSION = "roles.write"

    def __init__(self, role_repo: OrgRoleRepository, org_permission_checker: OrgPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._role_repo = role_repo
        self._org_permission_checker = org_permission_checker
        self._event_bus = event_bus

    async def handle(self, command: UpdateOrgRoleCommand) -> None:
        caller_id = Id.from_string(command.caller_id)
        org_id = Id.from_string(command.org_id)

        await self._org_permission_checker.require_permission(caller_id, org_id, self.REQUIRED_PERMISSION)
        role = await self._role_repo.get_by_id(Id.from_string(command.role_id))
        if role is None:
            raise OrgRoleNotFoundException(command.role_id)

        role.update(permissions=command.permissions, description=command.description)
        await self._role_repo.update(role)
        await self._event_bus.publish_all(role.clear_domain_events())
