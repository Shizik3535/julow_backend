from __future__ import annotations

import uuid

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.ports.file_storage.file_storage_port import FileStoragePort
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.url_vo import Url
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository


class ChangeWorkspaceLogoCommand(BaseCommand):
    """
    Команда изменения логотипа workspace.

    Атрибуты:
        caller_id: ID пользователя, выполняющего операцию.
        workspace_id: ID workspace.
        file_data: Содержимое файла логотипа (байты).
        content_type: MIME-тип файла (например image/png).
    """

    caller_id: str
    workspace_id: str
    file_data: bytes
    content_type: str = "image/png"


class ChangeWorkspaceLogoHandler(BaseCommandHandler[ChangeWorkspaceLogoCommand, None]):
    """
    Обработчик изменения логотипа workspace.

    Загружает файл в хранилище через FileStoragePort,
    получает URL и вызывает доменный метод change_logo.
    """

    REQUIRED_PERMISSION = "ws.settings.write"

    def __init__(
        self,
        ws_repo: WorkspaceRepository,
        file_storage: FileStoragePort,
        permission_checker: WorkspacePermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._ws_repo = ws_repo
        self._file_storage = file_storage
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: ChangeWorkspaceLogoCommand) -> None:
        ws_id = Id.from_string(command.workspace_id)
        caller_id = Id.from_string(command.caller_id)

        ws = await self._ws_repo.get_by_id(ws_id)
        if ws is None:
            raise WorkspaceNotFoundException(command.workspace_id)

        await self._permission_checker.require_permission(
            user_id=caller_id,
            workspace_id=ws_id,
            permission=self.REQUIRED_PERMISSION,
        )

        key = f"logos/{command.workspace_id}/{uuid.uuid4()}"
        await self._file_storage.upload(
            key=key,
            data=command.file_data,
            content_type=command.content_type,
        )
        url_str = await self._file_storage.get_url(key=key)

        ws.change_logo(Url(url_str))
        await self._ws_repo.update(ws)

        await self._event_bus.publish_all(ws.clear_domain_events())
