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
from app.context.filestorage.domain.exceptions.storage_exceptions import StorageNotFoundException
from app.context.filestorage.domain.repositories.storage_repository import StorageRepository
from app.context.filestorage.domain.value_objects.file_type import FileType
from app.context.filestorage.domain.value_objects.storage_config import StorageConfig
from app.context.filestorage.domain.value_objects.storage_owner_type import StorageOwnerType


REQUIRED_PERMISSION = "storage.admin"


class _BaseStorageUpdateHandler:
    """Общая база с проверкой разрешения и загрузкой Storage."""

    REQUIRED_PERMISSION = REQUIRED_PERMISSION

    def __init__(
        self,
        storage_repo: StorageRepository,
        permission_checker: WorkspacePermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        self._storage_repo = storage_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def _load_storage(self, storage_id_str: str, caller_id: str):
        storage = await self._storage_repo.get_by_id(Id.from_string(storage_id_str))
        if storage is None:
            raise StorageNotFoundException(id=storage_id_str)
        if storage.owner_type == StorageOwnerType.WORKSPACE:
            await self._permission_checker.require_permission(
                user_id=caller_id,
                workspace_id=str(storage.owner_id),
                permission=self.REQUIRED_PERMISSION,
            )
        return storage


class UpdateStorageConfigCommand(BaseCommand):
    """Команда обновления конфигурации хранилища."""

    caller_id: str
    storage_id: str
    endpoint: str | None = None
    bucket: str | None = None
    region: str | None = None
    access_key_ref: str | None = None
    secret_key_ref: str | None = None


class UpdateStorageConfigHandler(
    _BaseStorageUpdateHandler,
    BaseCommandHandler[UpdateStorageConfigCommand, StorageDTO],
):
    """Обновление параметров провайдера хранилища."""

    def __init__(self, storage_repo, permission_checker, event_bus) -> None:
        BaseCommandHandler.__init__(self)
        _BaseStorageUpdateHandler.__init__(self, storage_repo, permission_checker, event_bus)

    async def handle(self, command: UpdateStorageConfigCommand) -> StorageDTO:
        storage = await self._load_storage(command.storage_id, command.caller_id)
        storage.update_config(
            StorageConfig(
                endpoint=command.endpoint or storage.config.endpoint,
                bucket=command.bucket or storage.config.bucket,
                region=command.region or storage.config.region,
                access_key_ref=command.access_key_ref or storage.config.access_key_ref,
                secret_key_ref=command.secret_key_ref or storage.config.secret_key_ref,
                custom_params=storage.config.custom_params,
            )
        )
        await self._storage_repo.update(storage)
        return storage_to_dto(storage)


class UpdateStorageQuotaCommand(BaseCommand):
    """Команда обновления квоты хранилища."""

    caller_id: str
    storage_id: str
    max_bytes: int


class UpdateStorageQuotaHandler(
    _BaseStorageUpdateHandler,
    BaseCommandHandler[UpdateStorageQuotaCommand, StorageDTO],
):
    """Обновление квоты."""

    def __init__(self, storage_repo, permission_checker, event_bus) -> None:
        BaseCommandHandler.__init__(self)
        _BaseStorageUpdateHandler.__init__(self, storage_repo, permission_checker, event_bus)

    async def handle(self, command: UpdateStorageQuotaCommand) -> StorageDTO:
        storage = await self._load_storage(command.storage_id, command.caller_id)
        storage.update_quota(command.max_bytes)
        await self._storage_repo.update(storage)
        return storage_to_dto(storage)


class SetStorageAllowedFileTypesCommand(BaseCommand):
    """Команда задания разрешённых типов файлов."""

    caller_id: str
    storage_id: str
    file_types: list[str] | None = None  # None = все типы


class SetStorageAllowedFileTypesHandler(
    _BaseStorageUpdateHandler,
    BaseCommandHandler[SetStorageAllowedFileTypesCommand, StorageDTO],
):
    """Задание списка разрешённых FileType."""

    def __init__(self, storage_repo, permission_checker, event_bus) -> None:
        BaseCommandHandler.__init__(self)
        _BaseStorageUpdateHandler.__init__(self, storage_repo, permission_checker, event_bus)

    async def handle(self, command: SetStorageAllowedFileTypesCommand) -> StorageDTO:
        storage = await self._load_storage(command.storage_id, command.caller_id)
        types = (
            [FileType(t) for t in command.file_types]
            if command.file_types is not None
            else None
        )
        storage.set_allowed_file_types(types)
        await self._storage_repo.update(storage)
        return storage_to_dto(storage)


class SetStorageMaxFileSizeCommand(BaseCommand):
    """Команда задания макс. размера одного файла."""

    caller_id: str
    storage_id: str
    max_file_size_bytes: int | None = None  # None = без лимита


class SetStorageMaxFileSizeHandler(
    _BaseStorageUpdateHandler,
    BaseCommandHandler[SetStorageMaxFileSizeCommand, StorageDTO],
):
    """Задание макс. размера одного файла."""

    def __init__(self, storage_repo, permission_checker, event_bus) -> None:
        BaseCommandHandler.__init__(self)
        _BaseStorageUpdateHandler.__init__(self, storage_repo, permission_checker, event_bus)

    async def handle(self, command: SetStorageMaxFileSizeCommand) -> StorageDTO:
        storage = await self._load_storage(command.storage_id, command.caller_id)
        storage.set_max_file_size(command.max_file_size_bytes)
        await self._storage_repo.update(storage)
        return storage_to_dto(storage)
