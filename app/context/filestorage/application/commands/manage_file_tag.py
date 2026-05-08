from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.color_vo import Color
from app.shared.domain.value_objects.id_vo import Id

from app.context.filestorage.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.filestorage.domain.entities.file_tag import FileTag
from app.context.filestorage.domain.exceptions.file_exceptions import FileNotFoundException
from app.context.filestorage.domain.repositories.file_repository import FileRepository


class AddFileTagCommand(BaseCommand):
    """Команда добавления тега к файлу."""

    caller_id: str
    file_id: str
    tag_name: str
    color: str | None = None


class AddFileTagHandler(BaseCommandHandler[AddFileTagCommand, None]):
    """Добавление тега."""

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

    async def handle(self, command: AddFileTagCommand) -> None:
        file = await self._file_repo.get_by_id(Id.from_string(command.file_id))
        if file is None:
            raise FileNotFoundException(id=command.file_id)
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=str(file.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )
        file.add_tag(
            FileTag(
                name=command.tag_name,
                color=Color(value=command.color) if command.color else None,
            )
        )
        await self._file_repo.update(file)
        await self._event_bus.publish_all(file.clear_domain_events())


class RemoveFileTagCommand(BaseCommand):
    """Команда удаления тега."""

    caller_id: str
    file_id: str
    tag_name: str


class RemoveFileTagHandler(BaseCommandHandler[RemoveFileTagCommand, None]):
    """Удаление тега."""

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

    async def handle(self, command: RemoveFileTagCommand) -> None:
        file = await self._file_repo.get_by_id(Id.from_string(command.file_id))
        if file is None:
            raise FileNotFoundException(id=command.file_id)
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=str(file.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )
        file.remove_tag(command.tag_name)
        await self._file_repo.update(file)
        await self._event_bus.publish_all(file.clear_domain_events())
