from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.ports.file_storage.file_storage_port import FileStoragePort
from app.shared.domain.value_objects.id_vo import Id

from app.context.filestorage.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.filestorage.domain.exceptions.file_exceptions import FileNotFoundException
from app.context.filestorage.domain.exceptions.storage_exceptions import (
    StorageNotFoundException,
)
from app.context.filestorage.domain.repositories.file_repository import FileRepository
from app.context.filestorage.domain.repositories.storage_repository import StorageRepository


# --- Trash ---


class TrashFileCommand(BaseCommand):
    """Команда перемещения файла в корзину."""

    caller_id: str
    file_id: str


class TrashFileHandler(BaseCommandHandler[TrashFileCommand, None]):
    """Перемещение файла в корзину (soft-delete)."""

    REQUIRED_PERMISSION = "files.write"

    def __init__(
        self,
        file_repo: FileRepository,
        permission_checker: WorkspacePermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._file_repo = file_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: TrashFileCommand) -> None:
        file = await self._file_repo.get_by_id(Id.from_string(command.file_id))
        if file is None:
            raise FileNotFoundException(id=command.file_id)
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=str(file.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )
        file.trash(Id.from_string(command.caller_id))
        await self._file_repo.update(file)
        await self._event_bus.publish_all(file.clear_domain_events())


# --- Restore ---


class RestoreFileCommand(BaseCommand):
    """Команда восстановления файла из корзины."""

    caller_id: str
    file_id: str


class RestoreFileHandler(BaseCommandHandler[RestoreFileCommand, None]):
    """Восстановление файла из корзины."""

    REQUIRED_PERMISSION = "files.write"

    def __init__(
        self,
        file_repo: FileRepository,
        permission_checker: WorkspacePermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._file_repo = file_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: RestoreFileCommand) -> None:
        file = await self._file_repo.get_by_id(Id.from_string(command.file_id))
        if file is None:
            raise FileNotFoundException(id=command.file_id)
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=str(file.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )
        file.restore(Id.from_string(command.caller_id))
        await self._file_repo.update(file)
        await self._event_bus.publish_all(file.clear_domain_events())


# --- Delete permanently ---


class DeleteFileCommand(BaseCommand):
    """Команда окончательного удаления файла."""

    caller_id: str
    file_id: str


class DeleteFileHandler(BaseCommandHandler[DeleteFileCommand, None]):
    """
    Окончательное удаление файла.

    Освобождает квоту хранилища, удаляет blob и saved-агрегат.
    """

    REQUIRED_PERMISSION = "files.delete"

    def __init__(
        self,
        file_repo: FileRepository,
        storage_repo: StorageRepository,
        permission_checker: WorkspacePermissionCheckerPort,
        file_storage: FileStoragePort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._file_repo = file_repo
        self._storage_repo = storage_repo
        self._permission_checker = permission_checker
        self._file_storage = file_storage
        self._event_bus = event_bus

    async def handle(self, command: DeleteFileCommand) -> None:
        file = await self._file_repo.get_by_id(Id.from_string(command.file_id))
        if file is None:
            raise FileNotFoundException(id=command.file_id)
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=str(file.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )

        # Освобождение квоты
        storage = await self._storage_repo.get_by_id(file.storage_id)
        if storage is None:
            raise StorageNotFoundException(id=str(file.storage_id))
        storage.remove_usage(file.size.value)

        # Удаление blob (best-effort)
        try:
            await self._file_storage.delete(file.storage_path)
            for v in file.versions:
                if v.storage_path != file.storage_path:
                    try:
                        await self._file_storage.delete(v.storage_path)
                    except Exception:  # noqa: BLE001
                        pass
        except Exception:  # noqa: BLE001
            pass

        file.delete_permanently()
        await self._file_repo.update(file)
        await self._storage_repo.update(storage)
        await self._file_repo.delete(file.id)

        await self._event_bus.publish_all(file.clear_domain_events())
