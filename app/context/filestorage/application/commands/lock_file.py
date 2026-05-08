from __future__ import annotations

from datetime import datetime

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.filestorage.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.filestorage.domain.exceptions.file_exceptions import FileNotFoundException
from app.context.filestorage.domain.repositories.file_repository import FileRepository


class LockFileCommand(BaseCommand):
    """Команда блокировки файла."""

    caller_id: str
    file_id: str
    reason: str | None = None
    expires_at: datetime | None = None


class LockFileHandler(BaseCommandHandler[LockFileCommand, None]):
    """Блокировка файла."""

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

    async def handle(self, command: LockFileCommand) -> None:
        file = await self._file_repo.get_by_id(Id.from_string(command.file_id))
        if file is None:
            raise FileNotFoundException(id=command.file_id)
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=str(file.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )
        file.lock_file(
            locked_by=Id.from_string(command.caller_id),
            reason=command.reason,
            expires_at=command.expires_at,
        )
        await self._file_repo.update(file)
        await self._event_bus.publish_all(file.clear_domain_events())


class UnlockFileCommand(BaseCommand):
    """Команда разблокировки файла."""

    caller_id: str
    file_id: str


class UnlockFileHandler(BaseCommandHandler[UnlockFileCommand, None]):
    """
    Разблокировка файла.

    Только locker, владелец или admin (`files.admin`) могут снять блокировку.
    """

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

    async def handle(self, command: UnlockFileCommand) -> None:
        file = await self._file_repo.get_by_id(Id.from_string(command.file_id))
        if file is None:
            raise FileNotFoundException(id=command.file_id)
        caller = Id.from_string(command.caller_id)

        # Если caller — locker или owner, разрешаем без проверки. Иначе — files.admin.
        is_locker = file.lock is not None and file.lock.locked_by == caller
        is_owner = file.owner_id == caller
        if not (is_locker or is_owner):
            await self._permission_checker.require_permission(
                user_id=command.caller_id,
                workspace_id=str(file.workspace_id),
                permission="files.admin",
            )
            # admin может снять чужую блокировку — используем force_unlock
            file.force_unlock(caller)
        else:
            file.unlock(caller)

        await self._file_repo.update(file)
        await self._event_bus.publish_all(file.clear_domain_events())
