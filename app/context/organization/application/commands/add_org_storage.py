from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.url_vo import Url
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.application.dto.storage_integration_dto import StorageIntegrationDTO
from app.context.organization.application.ports.encryption.encryption_port import EncryptionPort
from app.context.organization.domain.aggregates.storage_integration import StorageIntegration
from app.context.organization.domain.repositories.storage_integration_repository import StorageIntegrationRepository
from app.context.organization.domain.value_objects.storage_config import StorageConfig
from app.context.organization.domain.value_objects.storage_provider import StorageProvider
from app.context.organization.domain.value_objects.storage_quota import StorageQuota


class AddOrgStorageCommand(BaseCommand):
    """
    Команда добавления хранилища организации.

    Атрибуты:
        org_id: ID организации.
        provider: Провайдер хранилища.
        endpoint: URL эндпоинта.
        bucket: Имя бакета.
        region: Регион.
        access_key: Ключ доступа (открытый текст).
        max_bytes: Максимальный объём.
        max_file_size_bytes: Максимальный размер файла.
        allowed_extensions: Разрешённые расширения.
    """

    caller_id: str
    org_id: str
    provider: str = "LOCAL"
    endpoint: str | None = None
    bucket: str = ""
    region: str = ""
    access_key: str = ""
    max_bytes: int = 0
    max_file_size_bytes: int | None = None
    allowed_extensions: list[str] | None = None


class AddOrgStorageHandler(BaseCommandHandler[AddOrgStorageCommand, StorageIntegrationDTO]):
    """
    Обработчик добавления хранилища организации.

    Шифрует access_key через EncryptionPort, создаёт StorageIntegration AR.
    """

    REQUIRED_PERMISSION = "org.settings.write"

    def __init__(
        self,
        storage_repo: StorageIntegrationRepository,
        encryption_port: EncryptionPort,
        org_permission_checker: OrgPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._storage_repo = storage_repo
        self._encryption_port = encryption_port
        self._org_permission_checker = org_permission_checker
        self._event_bus = event_bus

    async def handle(self, command: AddOrgStorageCommand) -> StorageIntegrationDTO:
        caller_id = Id.from_string(command.caller_id)
        org_id = Id.from_string(command.org_id)

        await self._org_permission_checker.require_permission(caller_id, org_id, self.REQUIRED_PERMISSION)
        encrypted_key = await self._encryption_port.encrypt(command.access_key) if command.access_key else ""

        config = StorageConfig(
            provider=StorageProvider(command.provider),
            endpoint=Url(command.endpoint) if command.endpoint else None,
            bucket=command.bucket,
            region=command.region,
            access_key=encrypted_key,
        )
        quota = StorageQuota(
            max_bytes=command.max_bytes,
            used_bytes=0,
            max_file_size_bytes=command.max_file_size_bytes,
            allowed_extensions=command.allowed_extensions,
        )

        storage = StorageIntegration.create(
            org_id=Id.from_string(command.org_id),
            config=config,
            quota=quota,
        )

        await self._storage_repo.add(storage)
        await self._event_bus.publish_all(storage.clear_domain_events())

        return StorageIntegrationDTO(
            id=str(storage.id),
            org_id=str(storage.org_id),
            provider=storage.config.provider.value,
            endpoint=str(storage.config.endpoint) if storage.config.endpoint else None,
            bucket=storage.config.bucket,
            region=storage.config.region,
            max_bytes=storage.quota.max_bytes,
            used_bytes=storage.quota.used_bytes,
            max_file_size_bytes=storage.quota.max_file_size_bytes,
            allowed_extensions=storage.quota.allowed_extensions,
            created_at=storage.created_at,
            updated_at=storage.updated_at,
        )
