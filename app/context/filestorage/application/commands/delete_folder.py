from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.filestorage.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.filestorage.domain.exceptions.folder_exceptions import (
    FolderNotEmptyException,
    FolderNotFoundException,
)
from app.context.filestorage.domain.repositories.file_repository import FileRepository
from app.context.filestorage.domain.repositories.folder_repository import FolderRepository


class DeleteFolderCommand(BaseCommand):
    """Команда удаления папки."""

    caller_id: str
    folder_id: str


class DeleteFolderHandler(BaseCommandHandler[DeleteFolderCommand, None]):
    """
    Удаление папки. Папка должна быть пустой
    (нет файлов и подпапок).
    """

    REQUIRED_PERMISSION = "files.delete"

    def __init__(
        self,
        folder_repo: FolderRepository,
        file_repo: FileRepository,
        permission_checker: WorkspacePermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._folder_repo = folder_repo
        self._file_repo = file_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: DeleteFolderCommand) -> None:
        folder_id = Id.from_string(command.folder_id)
        folder = await self._folder_repo.get_by_id(folder_id)
        if folder is None:
            raise FolderNotFoundException(id=command.folder_id)
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=str(folder.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )

        # Проверка пустоты
        files = await self._file_repo.get_by_folder(folder_id)
        if files:
            raise FolderNotEmptyException()
        subfolders = await self._folder_repo.get_by_parent(folder_id)
        if subfolders:
            raise FolderNotEmptyException()

        folder.delete()
        await self._folder_repo.delete(folder_id)
        await self._event_bus.publish_all(folder.clear_domain_events())
