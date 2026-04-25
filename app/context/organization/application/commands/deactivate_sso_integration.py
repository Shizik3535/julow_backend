from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.shared.domain.exceptions import EntityNotFoundException
from app.context.organization.domain.repositories.sso_integration_repository import SSOIntegrationRepository


class DeactivateSSOIntegrationCommand(BaseCommand):
    """
    Команда деактивации SSO-интеграции.

    Атрибуты:
        integration_id: ID SSO-интеграции.
    """

    caller_id: str
    org_id: str
    integration_id: str


class DeactivateSSOIntegrationHandler(BaseCommandHandler[DeactivateSSOIntegrationCommand, None]):
    """
    Обработчик деактивации SSO-интеграции.

    Загружает SSOIntegration, вызывает deactivate, сохраняет.
    """

    REQUIRED_PERMISSION = "org.settings.write"

    def __init__(self, sso_repo: SSOIntegrationRepository, org_permission_checker: OrgPermissionCheckerPort, event_bus: DomainEventBus) -> None:
        super().__init__()
        self._sso_repo = sso_repo
        self._org_permission_checker = org_permission_checker
        self._event_bus = event_bus

    async def handle(self, command: DeactivateSSOIntegrationCommand) -> None:
        caller_id = Id.from_string(command.caller_id)
        org_id = Id.from_string(command.org_id)

        integration = await self._sso_repo.get_by_id(Id.from_string(command.integration_id))
        if integration is None:
            raise EntityNotFoundException(entity_type="SSOIntegration", id=command.integration_id)
        await self._org_permission_checker.require_permission(caller_id, org_id, self.REQUIRED_PERMISSION)

        integration.deactivate()
        await self._sso_repo.update(integration)
        await self._event_bus.publish_all(integration.clear_domain_events())
