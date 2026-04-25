from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.url_vo import Url
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.application.ports.encryption.encryption_port import EncryptionPort
from app.shared.domain.exceptions import EntityNotFoundException
from app.context.organization.domain.repositories.storage_integration_repository import StorageIntegrationRepository
from app.context.organization.domain.value_objects.storage_config import StorageConfig
from app.context.organization.domain.value_objects.storage_provider import StorageProvider
from app.context.organization.domain.value_objects.storage_quota import StorageQuota


class UpdateOrgStorageCommand(BaseCommand):
    """
    Команда обновления хранилища организации.

    Атрибуты:
        storage_id: ID хранилища.
        provider: Новый провайдер.
        endpoint: Новый эндпоинт.
        bucket: Новый бакет.
        region: Новый регион.
        access_key: Новый ключ доступа (открытый текст).
        max_bytes: Новый максимум.
        max_file_size_bytes: Новый максимум размера файла.
        allowed_extensions: Новые разрешённые расширения.
    """

    caller_id: str
    org_id: str
    storage_id: str
    provider: str | None = None
    endpoint: str | None = None
    bucket: str | None = None
    region: str | None = None
    access_key: str | None = None
    max_bytes: int | None = None
    max_file_size_bytes: int | None = None
    allowed_extensions: list[str] | None = None


class UpdateOrgStorageHandler(BaseCommandHandler[UpdateOrgStorageCommand, None]):
    """
    Обработчик обновления хранилища организации.

    Обновляет config и/или quota StorageIntegration.
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

    async def handle(self, command: UpdateOrgStorageCommand) -> None:
        caller_id = Id.from_string(command.caller_id)
        org_id = Id.from_string(command.org_id)

        storage = await self._storage_repo.get_by_id(Id.from_string(command.storage_id))
        if storage is None:
            raise EntityNotFoundException(entity_type="StorageIntegration", id=command.storage_id)
        await self._org_permission_checker.require_permission(caller_id, org_id, self.REQUIRED_PERMISSION)

        has_config_change = any([
            command.provider is not None,
            command.endpoint is not None,
            command.bucket is not None,
            command.region is not None,
            command.access_key is not None,
        ])
        if has_config_change:
            encrypted_key = storage.config.access_key
            if command.access_key is not None:
                encrypted_key = await self._encryption_port.encrypt(command.access_key)

            new_config = StorageConfig(
                provider=StorageProvider(command.provider) if command.provider else storage.config.provider,
                endpoint=Url(command.endpoint) if command.endpoint is not None else storage.config.endpoint,
                bucket=command.bucket if command.bucket is not None else storage.config.bucket,
                region=command.region if command.region is not None else storage.config.region,
                access_key=encrypted_key,
            )
            storage.update_config(config=new_config)

        has_quota_change = any([
            command.max_bytes is not None,
            command.max_file_size_bytes is not None,
            command.allowed_extensions is not None,
        ])
        if has_quota_change:
            new_quota = StorageQuota(
                max_bytes=command.max_bytes if command.max_bytes is not None else storage.quota.max_bytes,
                used_bytes=storage.quota.used_bytes,
                max_file_size_bytes=command.max_file_size_bytes if command.max_file_size_bytes is not None else storage.quota.max_file_size_bytes,
                allowed_extensions=command.allowed_extensions if command.allowed_extensions is not None else storage.quota.allowed_extensions,
            )
            storage.update_quota(quota=new_quota)

        await self._storage_repo.update(storage)
        await self._event_bus.publish_all(storage.clear_domain_events())
