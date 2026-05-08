from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.color_vo import Color
from app.shared.domain.value_objects.id_vo import Id

from app.context.filestorage.application.dto.folder_dto import FolderDTO
from app.context.filestorage.application.dto.mappers import folder_to_dto
from app.context.filestorage.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.filestorage.domain.aggregates.folder import Folder
from app.context.filestorage.domain.exceptions.folder_exceptions import (
    FolderNotFoundException,
    MaxFolderDepthExceededException,
)
from app.context.filestorage.domain.repositories.folder_repository import FolderRepository
from app.context.filestorage.domain.value_objects.folder_type import FolderType


MAX_FOLDER_DEPTH = 10


class CreateFolderCommand(BaseCommand):
    """Команда создания папки."""

    caller_id: str
    workspace_id: str
    name: str
    parent_folder_id: str | None = None
    color: str | None = None
    description: str | None = None
    icon: str | None = None


class CreateFolderHandler(BaseCommandHandler[CreateFolderCommand, FolderDTO]):
    """Создание папки в workspace."""

    REQUIRED_PERMISSION = "files.write"

    def __init__(
        self,
        folder_repo: FolderRepository,
        permission_checker: WorkspacePermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._folder_repo = folder_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: CreateFolderCommand) -> FolderDTO:
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=command.workspace_id,
            permission=self.REQUIRED_PERMISSION,
        )

        parent_id: Id | None = None
        if command.parent_folder_id:
            parent_id = Id.from_string(command.parent_folder_id)
            parent = await self._folder_repo.get_by_id(parent_id)
            if parent is None:
                raise FolderNotFoundException(id=command.parent_folder_id)
            depth = await self._compute_depth(parent)
            if depth + 1 >= MAX_FOLDER_DEPTH:
                raise MaxFolderDepthExceededException(max_depth=MAX_FOLDER_DEPTH)

        folder = Folder.create(
            name=command.name,
            workspace_id=Id.from_string(command.workspace_id),
            owner_id=Id.from_string(command.caller_id),
            folder_type=FolderType.REGULAR,
            parent_folder_id=parent_id,
        )
        if command.color:
            folder.color = Color(value=command.color)
        if command.description:
            folder.description = command.description
        if command.icon:
            folder.icon = command.icon

        await self._folder_repo.add(folder)
        await self._event_bus.publish_all(folder.clear_domain_events())
        return folder_to_dto(folder)

    async def _compute_depth(self, folder: Folder) -> int:
        depth = 1
        current = folder
        while current.parent_folder_id is not None:
            parent = await self._folder_repo.get_by_id(current.parent_folder_id)
            if parent is None:
                break
            depth += 1
            if depth >= MAX_FOLDER_DEPTH:
                return depth
            current = parent
        return depth
