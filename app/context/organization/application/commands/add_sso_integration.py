from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.application.dto.sso_integration_dto import SSOIntegrationDTO
from app.context.organization.application.ports.encryption.encryption_port import EncryptionPort
from app.context.organization.domain.aggregates.sso_integration import SSOIntegration
from app.context.organization.domain.repositories.sso_integration_repository import SSOIntegrationRepository
from app.context.organization.domain.value_objects.sso_provider import SSOProvider


class AddSSOIntegrationCommand(BaseCommand):
    """
    Команда добавления SSO-интеграции.

    Атрибуты:
        org_id: ID организации.
        provider: Провайдер SSO (SAML, OIDC, LDAP).
        entity_id: Entity ID.
        sso_url: SSO URL.
        certificate: Сертификат (открытый текст, будет зашифрован).
        added_by: ID добавившего.
        group_mapping: Маппинг групп.
        attribute_mapping: Маппинг атрибутов.
    """

    caller_id: str
    org_id: str
    provider: str
    entity_id: str
    sso_url: str
    certificate: str
    added_by: str
    group_mapping: dict[str, str] | None = None
    attribute_mapping: dict[str, str] | None = None


class AddSSOIntegrationHandler(BaseCommandHandler[AddSSOIntegrationCommand, SSOIntegrationDTO]):
    """
    Обработчик добавления SSO-интеграции.

    Шифрует сертификат через EncryptionPort, создаёт SSOIntegration AR.
    """

    REQUIRED_PERMISSION = "org.settings.write"

    def __init__(
        self,
        sso_repo: SSOIntegrationRepository,
        encryption_port: EncryptionPort,
        org_permission_checker: OrgPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._sso_repo = sso_repo
        self._encryption_port = encryption_port
        self._org_permission_checker = org_permission_checker
        self._event_bus = event_bus

    async def handle(self, command: AddSSOIntegrationCommand) -> SSOIntegrationDTO:
        caller_id = Id.from_string(command.caller_id)
        org_id = Id.from_string(command.org_id)

        await self._org_permission_checker.require_permission(caller_id, org_id, self.REQUIRED_PERMISSION)
        encrypted_cert = await self._encryption_port.encrypt(command.certificate)

        integration = SSOIntegration.create(
            org_id=Id.from_string(command.org_id),
            provider=SSOProvider(command.provider),
            entity_id=command.entity_id,
            sso_url=command.sso_url,
            certificate=encrypted_cert,
            added_by=Id.from_string(command.added_by),
            group_mapping=command.group_mapping,
            attribute_mapping=command.attribute_mapping,
        )

        await self._sso_repo.add(integration)
        await self._event_bus.publish_all(integration.clear_domain_events())

        return SSOIntegrationDTO(
            id=str(integration.id),
            org_id=str(integration.org_id),
            provider=integration.provider.value,
            entity_id=integration.entity_id,
            sso_url=integration.sso_url,
            is_active=integration.is_active,
            group_mapping=integration.group_mapping,
            attribute_mapping=integration.attribute_mapping,
            added_at=integration.added_at,
            added_by=str(integration.added_by),
            created_at=integration.created_at,
            updated_at=integration.updated_at,
        )
