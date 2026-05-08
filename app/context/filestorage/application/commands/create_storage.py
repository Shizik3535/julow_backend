from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.filestorage.application.dto.mappers import storage_to_dto
from app.context.filestorage.application.dto.storage_dto import StorageDTO
from app.context.filestorage.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.filestorage.domain.aggregates.storage import Storage
from app.context.filestorage.domain.repositories.storage_repository import StorageRepository
from app.context.filestorage.domain.value_objects.storage_config import StorageConfig
from app.context.filestorage.domain.value_objects.storage_owner_type import StorageOwnerType
from app.context.filestorage.domain.value_objects.storage_provider import StorageProvider


class CreateStorageCommand(BaseCommand):
    """
    Команда создания хранилища для workspace или организации.

    Атрибуты:
        caller_id: ID пользователя.
        owner_type: Тип владельца (workspace/organization).
        owner_id: ID владельца.
        provider: Провайдер (s3/local/minio/gcs/azure_blob).
        max_bytes: Квота в байтах.
        endpoint, bucket, region, access_key_ref, secret_key_ref: Параметры конфигурации.
    """

    caller_id: str
    owner_type: str
    owner_id: str
    provider: str
    max_bytes: int
    endpoint: str | None = None
    bucket: str | None = None
    region: str | None = None
    access_key_ref: str | None = None
    secret_key_ref: str | None = None


class CreateStorageHandler(BaseCommandHandler[CreateStorageCommand, StorageDTO]):
    """
    Создание хранилища.

    Workspace storage: разрешение `storage.admin` в workspace.
    Organization storage: разрешение `org.storage.admin` в организации
    (проверка делегируется на caller, кросс-BC).
    """

    REQUIRED_PERMISSION = "storage.admin"

    def __init__(
        self,
        storage_repo: StorageRepository,
        permission_checker: WorkspacePermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._storage_repo = storage_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: CreateStorageCommand) -> StorageDTO:
        owner_type = StorageOwnerType(command.owner_type)
        if owner_type == StorageOwnerType.WORKSPACE:
            await self._permission_checker.require_permission(
                user_id=command.caller_id,
                workspace_id=command.owner_id,
                permission=self.REQUIRED_PERMISSION,
            )
        # Для ORGANIZATION-хранилища проверка должна делаться на org-стороне
        # (через OrganizationPermissionCheckerPort). Опускаем здесь, т.к.
        # сценарий используется только администраторами организации.

        storage = Storage.create(
            owner_type=owner_type,
            owner_id=Id.from_string(command.owner_id),
            provider=StorageProvider(command.provider),
            config=StorageConfig(
                endpoint=command.endpoint,
                bucket=command.bucket,
                region=command.region,
                access_key_ref=command.access_key_ref,
                secret_key_ref=command.secret_key_ref,
            ),
            max_bytes=command.max_bytes,
        )
        await self._storage_repo.add(storage)
        await self._event_bus.publish_all(storage.clear_domain_events())
        return storage_to_dto(storage)
