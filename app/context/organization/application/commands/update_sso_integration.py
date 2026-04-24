from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.ports.encryption.encryption_port import EncryptionPort
from app.shared.domain.exceptions import EntityNotFoundException
from app.context.organization.domain.repositories.sso_integration_repository import SSOIntegrationRepository


class UpdateSSOIntegrationCommand(BaseCommand):
    """
    Команда обновления SSO-интеграции.

    Атрибуты:
        integration_id: ID SSO-интеграции.
        entity_id: Новый Entity ID.
        sso_url: Новый SSO URL.
        certificate: Новый сертификат (открытый текст).
        group_mapping: Новый маппинг групп.
        attribute_mapping: Новый маппинг атрибутов.
    """

    integration_id: str
    entity_id: str | None = None
    sso_url: str | None = None
    certificate: str | None = None
    group_mapping: dict[str, str] | None = None
    attribute_mapping: dict[str, str] | None = None


class UpdateSSOIntegrationHandler(BaseCommandHandler[UpdateSSOIntegrationCommand, None]):
    """
    Обработчик обновления SSO-интеграции.

    Загружает SSOIntegration, шифрует сертификат при необходимости,
    вызывает update, сохраняет.
    """

    def __init__(
        self,
        sso_repo: SSOIntegrationRepository,
        encryption_port: EncryptionPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._sso_repo = sso_repo
        self._encryption_port = encryption_port
        self._event_bus = event_bus

    async def handle(self, command: UpdateSSOIntegrationCommand) -> None:
        integration = await self._sso_repo.get_by_id(Id.from_string(command.integration_id))
        if integration is None:
            raise EntityNotFoundException(entity_type="SSOIntegration", id=command.integration_id)

        encrypted_cert: str | None = None
        if command.certificate is not None:
            encrypted_cert = await self._encryption_port.encrypt(command.certificate)

        integration.update(
            entity_id=command.entity_id,
            sso_url=command.sso_url,
            certificate=encrypted_cert,
            group_mapping=command.group_mapping,
            attribute_mapping=command.attribute_mapping,
        )
        await self._sso_repo.update(integration)
        await self._event_bus.publish_all(integration.clear_domain_events())
