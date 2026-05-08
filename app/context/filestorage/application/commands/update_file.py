from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.filestorage.application.dto.file_dto import FileDTO
from app.context.filestorage.application.dto.mappers import file_to_dto
from app.context.filestorage.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.filestorage.domain.exceptions.file_exceptions import FileNotFoundException
from app.context.filestorage.domain.exceptions.folder_exceptions import (
    FolderNotFoundException,
)
from app.context.filestorage.domain.repositories.file_repository import FileRepository
from app.context.filestorage.domain.repositories.folder_repository import FolderRepository


REQUIRED_PERMISSION = "files.write"


class _BaseFileUpdateHandler:
    """Общий код: проверка разрешения, загрузка файла."""

    REQUIRED_PERMISSION = REQUIRED_PERMISSION

    def __init__(
        self,
        file_repo: FileRepository,
        permission_checker: WorkspacePermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        self._file_repo = file_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def _load_file_with_permission(self, file_id_str: str, caller_id: str):
        file = await self._file_repo.get_by_id(Id.from_string(file_id_str))
        if file is None:
            raise FileNotFoundException(id=file_id_str)
        await self._permission_checker.require_permission(
            user_id=caller_id,
            workspace_id=str(file.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )
        return file


# --- Rename ---


class RenameFileCommand(BaseCommand):
    """Команда переименования файла."""

    caller_id: str
    file_id: str
    new_name: str


class RenameFileHandler(
    _BaseFileUpdateHandler,
    BaseCommandHandler[RenameFileCommand, FileDTO],
):
    """Переименование файла."""

    def __init__(
        self,
        file_repo: FileRepository,
        permission_checker: WorkspacePermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        BaseCommandHandler.__init__(self)
        _BaseFileUpdateHandler.__init__(self, file_repo, permission_checker, event_bus)

    async def handle(self, command: RenameFileCommand) -> FileDTO:
        file = await self._load_file_with_permission(command.file_id, command.caller_id)
        file.rename(command.new_name)
        await self._file_repo.update(file)
        await self._event_bus.publish_all(file.clear_domain_events())
        return file_to_dto(file)


# --- Move ---


class MoveFileCommand(BaseCommand):
    """Команда перемещения файла в другую папку."""

    caller_id: str
    file_id: str
    new_folder_id: str


class MoveFileHandler(
    _BaseFileUpdateHandler,
    BaseCommandHandler[MoveFileCommand, FileDTO],
):
    """Перемещение файла."""

    def __init__(
        self,
        file_repo: FileRepository,
        folder_repo: FolderRepository,
        permission_checker: WorkspacePermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        BaseCommandHandler.__init__(self)
        _BaseFileUpdateHandler.__init__(self, file_repo, permission_checker, event_bus)
        self._folder_repo = folder_repo

    async def handle(self, command: MoveFileCommand) -> FileDTO:
        file = await self._load_file_with_permission(command.file_id, command.caller_id)
        new_folder_id = Id.from_string(command.new_folder_id)
        folder = await self._folder_repo.get_by_id(new_folder_id)
        if folder is None:
            raise FolderNotFoundException(id=command.new_folder_id)
        file.move(new_folder_id)
        await self._file_repo.update(file)
        await self._event_bus.publish_all(file.clear_domain_events())
        return file_to_dto(file)


# --- Update description ---


class UpdateFileDescriptionCommand(BaseCommand):
    """Команда обновления описания файла."""

    caller_id: str
    file_id: str
    description: str | None = None


class UpdateFileDescriptionHandler(
    _BaseFileUpdateHandler,
    BaseCommandHandler[UpdateFileDescriptionCommand, FileDTO],
):
    """Обновление описания файла."""

    def __init__(
        self,
        file_repo: FileRepository,
        permission_checker: WorkspacePermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        BaseCommandHandler.__init__(self)
        _BaseFileUpdateHandler.__init__(self, file_repo, permission_checker, event_bus)

    async def handle(self, command: UpdateFileDescriptionCommand) -> FileDTO:
        file = await self._load_file_with_permission(command.file_id, command.caller_id)
        file.update_description(command.description)
        await self._file_repo.update(file)
        await self._event_bus.publish_all(file.clear_domain_events())
        return file_to_dto(file)
