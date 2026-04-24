from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.domain.exceptions.organization_exceptions import OrganizationNotFoundException
from app.context.organization.domain.repositories.organization_repository import OrganizationRepository


class ReactivateOrganizationCommand(BaseCommand):
    """
    Команда реактивации организации.

    Атрибуты:
        org_id: ID организации.
    """

    caller_id: str
    org_id: str


class ReactivateOrganizationHandler(BaseCommandHandler[ReactivateOrganizationCommand, None]):
    """
    Обработчик реактивации организации.

    Загружает Organization, вызывает reactivate, сохраняет.
    """

    REQUIRED_PERMISSION = "org.settings.write"

    def __init__(self, org_repo: OrganizationRepository, org_permission_checker: OrgPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._org_repo = org_repo
        self._org_permission_checker = org_permission_checker
        self._event_bus = event_bus

    async def handle(self, command: ReactivateOrganizationCommand) -> None:
        caller_id = Id.from_string(command.caller_id)
        org_id = Id.from_string(command.org_id)

        await self._org_permission_checker.require_permission(caller_id, org_id, self.REQUIRED_PERMISSION)
        org = await self._org_repo.get_by_id(Id.from_string(command.org_id))
        if org is None:
            raise OrganizationNotFoundException(command.org_id)

        org.reactivate()
        await self._org_repo.update(org)
        await self._event_bus.publish_all(org.clear_domain_events())
