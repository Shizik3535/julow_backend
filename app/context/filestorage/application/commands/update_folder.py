from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.filestorage.application.dto.folder_dto import FolderDTO
from app.context.filestorage.application.dto.mappers import folder_to_dto
from app.context.filestorage.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.filestorage.domain.exceptions.folder_exceptions import (
    CircularFolderReferenceException,
    FolderNotFoundException,
)
from app.context.filestorage.domain.repositories.folder_repository import FolderRepository


class _BaseFolderHandler:
    """Общий базовый класс с проверкой разрешения."""

    REQUIRED_PERMISSION = "files.write"

    def __init__(
        self,
        folder_repo: FolderRepository,
        permission_checker: WorkspacePermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        self._folder_repo = folder_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def _load_folder(self, folder_id_str: str, caller_id: str):
        folder = await self._folder_repo.get_by_id(Id.from_string(folder_id_str))
        if folder is None:
            raise FolderNotFoundException(id=folder_id_str)
        await self._permission_checker.require_permission(
            user_id=caller_id,
            workspace_id=str(folder.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )
        return folder


class RenameFolderCommand(BaseCommand):
    """Команда переименования папки."""

    caller_id: str
    folder_id: str
    new_name: str


class RenameFolderHandler(
    _BaseFolderHandler,
    BaseCommandHandler[RenameFolderCommand, FolderDTO],
):
    """Переименование папки."""

    def __init__(self, folder_repo, permission_checker, event_bus) -> None:
        BaseCommandHandler.__init__(self)
        _BaseFolderHandler.__init__(self, folder_repo, permission_checker, event_bus)

    async def handle(self, command: RenameFolderCommand) -> FolderDTO:
        folder = await self._load_folder(command.folder_id, command.caller_id)
        folder.rename(command.new_name)
        await self._folder_repo.update(folder)
        await self._event_bus.publish_all(folder.clear_domain_events())
        return folder_to_dto(folder)


class MoveFolderCommand(BaseCommand):
    """Команда перемещения папки в другого родителя."""

    caller_id: str
    folder_id: str
    new_parent_folder_id: str


class MoveFolderHandler(
    _BaseFolderHandler,
    BaseCommandHandler[MoveFolderCommand, FolderDTO],
):
    """Перемещение папки. Проверяет циклы."""

    def __init__(self, folder_repo, permission_checker, event_bus) -> None:
        BaseCommandHandler.__init__(self)
        _BaseFolderHandler.__init__(self, folder_repo, permission_checker, event_bus)

    async def handle(self, command: MoveFolderCommand) -> FolderDTO:
        folder = await self._load_folder(command.folder_id, command.caller_id)
        new_parent_id = Id.from_string(command.new_parent_folder_id)

        # Проверка цикла: новый родитель не должен быть потомком folder.
        current_id: Id | None = new_parent_id
        while current_id is not None:
            if current_id == folder.id:
                raise CircularFolderReferenceException()
            parent = await self._folder_repo.get_by_id(current_id)
            if parent is None:
                break
            current_id = parent.parent_folder_id

        folder.move(new_parent_id)
        await self._folder_repo.update(folder)
        await self._event_bus.publish_all(folder.clear_domain_events())
        return folder_to_dto(folder)


class UpdateFolderDescriptionCommand(BaseCommand):
    """Команда обновления описания папки."""

    caller_id: str
    folder_id: str
    description: str | None = None


class UpdateFolderDescriptionHandler(
    _BaseFolderHandler,
    BaseCommandHandler[UpdateFolderDescriptionCommand, FolderDTO],
):
    """Обновление описания папки."""

    def __init__(self, folder_repo, permission_checker, event_bus) -> None:
        BaseCommandHandler.__init__(self)
        _BaseFolderHandler.__init__(self, folder_repo, permission_checker, event_bus)

    async def handle(self, command: UpdateFolderDescriptionCommand) -> FolderDTO:
        folder = await self._load_folder(command.folder_id, command.caller_id)
        folder.update_description(command.description)
        await self._folder_repo.update(folder)
        await self._event_bus.publish_all(folder.clear_domain_events())
        return folder_to_dto(folder)


class PinFolderCommand(BaseCommand):
    """Команда закрепления папки."""

    caller_id: str
    folder_id: str


class PinFolderHandler(
    _BaseFolderHandler,
    BaseCommandHandler[PinFolderCommand, None],
):
    """Закрепление папки."""

    def __init__(self, folder_repo, permission_checker, event_bus) -> None:
        BaseCommandHandler.__init__(self)
        _BaseFolderHandler.__init__(self, folder_repo, permission_checker, event_bus)

    async def handle(self, command: PinFolderCommand) -> None:
        folder = await self._load_folder(command.folder_id, command.caller_id)
        folder.pin()
        await self._folder_repo.update(folder)


class UnpinFolderCommand(BaseCommand):
    """Команда открепления папки."""

    caller_id: str
    folder_id: str


class UnpinFolderHandler(
    _BaseFolderHandler,
    BaseCommandHandler[UnpinFolderCommand, None],
):
    """Открепление папки."""

    def __init__(self, folder_repo, permission_checker, event_bus) -> None:
        BaseCommandHandler.__init__(self)
        _BaseFolderHandler.__init__(self, folder_repo, permission_checker, event_bus)

    async def handle(self, command: UnpinFolderCommand) -> None:
        folder = await self._load_folder(command.folder_id, command.caller_id)
        folder.unpin()
        await self._folder_repo.update(folder)
