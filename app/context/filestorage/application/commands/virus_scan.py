from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.filestorage.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.filestorage.domain.exceptions.file_exceptions import FileNotFoundException
from app.context.filestorage.domain.repositories.file_repository import FileRepository


class MarkScanCleanCommand(BaseCommand):
    """Команда отметки файла как чистого после сканирования."""

    caller_id: str
    file_id: str


class MarkScanCleanHandler(BaseCommandHandler[MarkScanCleanCommand, None]):
    """Отметка файла как чистого. Требует `files.admin` (вызов из системного скана)."""

    REQUIRED_PERMISSION = "files.admin"

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

    async def handle(self, command: MarkScanCleanCommand) -> None:
        file = await self._file_repo.get_by_id(Id.from_string(command.file_id))
        if file is None:
            raise FileNotFoundException(id=command.file_id)
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=str(file.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )
        file.mark_scan_clean()
        await self._file_repo.update(file)
        await self._event_bus.publish_all(file.clear_domain_events())


class MarkScanInfectedCommand(BaseCommand):
    """Команда отметки файла как заражённого."""

    caller_id: str
    file_id: str
    virus_name: str | None = None


class MarkScanInfectedHandler(BaseCommandHandler[MarkScanInfectedCommand, None]):
    """Отметка файла как заражённого вирусом."""

    REQUIRED_PERMISSION = "files.admin"

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

    async def handle(self, command: MarkScanInfectedCommand) -> None:
        file = await self._file_repo.get_by_id(Id.from_string(command.file_id))
        if file is None:
            raise FileNotFoundException(id=command.file_id)
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=str(file.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )
        file.mark_scan_infected(command.virus_name)
        await self._file_repo.update(file)
        await self._event_bus.publish_all(file.clear_domain_events())
