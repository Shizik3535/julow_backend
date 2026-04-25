from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.domain.exceptions.organization_exceptions import OrganizationNotFoundException
from app.context.organization.domain.repositories.organization_repository import OrganizationRepository


class TransferOwnershipCommand(BaseCommand):
    """
    Команда передачи владения организацией.

    Атрибуты:
        org_id: ID организации.
        from_id: ID текущего владельца.
        to_id: ID нового владельца.
    """

    caller_id: str
    org_id: str
    from_id: str
    to_id: str


class TransferOwnershipHandler(BaseCommandHandler[TransferOwnershipCommand, None]):
    """
    Обработчик передачи владения организацией.

    Загружает Organization, вызывает transfer_ownership, сохраняет.
    """

    REQUIRED_PERMISSION = "org.*"

    def __init__(self, org_repo: OrganizationRepository, org_permission_checker: OrgPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._org_repo = org_repo
        self._org_permission_checker = org_permission_checker
        self._event_bus = event_bus

    async def handle(self, command: TransferOwnershipCommand) -> None:
        caller_id = Id.from_string(command.caller_id)
        org_id = Id.from_string(command.org_id)

        org = await self._org_repo.get_by_id(org_id)
        if org is None:
            raise OrganizationNotFoundException(command.org_id)
        await self._org_permission_checker.require_permission(caller_id, org_id, self.REQUIRED_PERMISSION)

        org.transfer_ownership(
            from_id=Id.from_string(command.from_id),
            to_id=Id.from_string(command.to_id),
        )
        await self._org_repo.update(org)
        await self._event_bus.publish_all(org.clear_domain_events())
