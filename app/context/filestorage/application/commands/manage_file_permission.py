from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.filestorage.application.ports.integration.inboard.identity_user_port import (
    IdentityUserPort,
)
from app.context.filestorage.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.filestorage.domain.exceptions.file_exceptions import FileNotFoundException
from app.context.filestorage.domain.repositories.file_repository import FileRepository
from app.context.filestorage.domain.value_objects.file_access_level import FileAccessLevel


class GrantFilePermissionCommand(BaseCommand):
    """
    Команда выдачи разрешения на файл пользователю или команде.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        file_id: ID файла.
        user_id: ID пользователя (None — для команды).
        team_id: ID команды (None — для пользователя).
        access_level: Уровень доступа (view/comment/edit/admin/owner).
    """

    caller_id: str
    file_id: str
    user_id: str | None = None
    team_id: str | None = None
    access_level: str = FileAccessLevel.VIEW.value


class GrantFilePermissionHandler(BaseCommandHandler[GrantFilePermissionCommand, None]):
    """Выдача разрешения на файл."""

    REQUIRED_PERMISSION = "files.share"

    def __init__(
        self,
        file_repo: FileRepository,
        permission_checker: WorkspacePermissionCheckerPort,
        identity_port: IdentityUserPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._file_repo = file_repo
        self._permission_checker = permission_checker
        self._identity_port = identity_port
        self._event_bus = event_bus

    async def handle(self, command: GrantFilePermissionCommand) -> None:
        if command.user_id is None and command.team_id is None:
            raise ValueError("Хотя бы один из user_id/team_id должен быть указан")
        file = await self._file_repo.get_by_id(Id.from_string(command.file_id))
        if file is None:
            raise FileNotFoundException(id=command.file_id)
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=str(file.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )
        if command.user_id and not await self._identity_port.user_exists(command.user_id):
            raise FileNotFoundException(id=command.user_id)

        file.grant_permission(
            access_level=FileAccessLevel(command.access_level),
            granted_by=Id.from_string(command.caller_id),
            user_id=Id.from_string(command.user_id) if command.user_id else None,
            team_id=Id.from_string(command.team_id) if command.team_id else None,
        )
        await self._file_repo.update(file)
        await self._event_bus.publish_all(file.clear_domain_events())


class RevokeFilePermissionCommand(BaseCommand):
    """Команда отзыва разрешения на файл."""

    caller_id: str
    file_id: str
    user_id: str | None = None
    team_id: str | None = None


class RevokeFilePermissionHandler(BaseCommandHandler[RevokeFilePermissionCommand, None]):
    """Отзыв разрешения на файл."""

    REQUIRED_PERMISSION = "files.share"

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

    async def handle(self, command: RevokeFilePermissionCommand) -> None:
        if command.user_id is None and command.team_id is None:
            raise ValueError("Хотя бы один из user_id/team_id должен быть указан")
        file = await self._file_repo.get_by_id(Id.from_string(command.file_id))
        if file is None:
            raise FileNotFoundException(id=command.file_id)
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=str(file.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )
        file.revoke_permission(
            user_id=Id.from_string(command.user_id) if command.user_id else None,
            team_id=Id.from_string(command.team_id) if command.team_id else None,
        )
        await self._file_repo.update(file)
        await self._event_bus.publish_all(file.clear_domain_events())
