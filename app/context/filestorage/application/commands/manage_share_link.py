from __future__ import annotations

import secrets
from datetime import datetime

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.ports.auth.password_port import PasswordPort
from app.shared.domain.value_objects.id_vo import Id

from app.context.filestorage.application.dto.file_dto import PublicShareLinkDTO
from app.context.filestorage.application.dto.mappers import share_link_to_dto
from app.context.filestorage.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.filestorage.domain.exceptions.file_exceptions import (
    FileNotFoundException,
    InvalidSharePasswordException,
    PublicShareLinkNotFoundException,
)
from app.context.filestorage.domain.repositories.file_repository import FileRepository
from app.context.filestorage.domain.value_objects.file_access_level import FileAccessLevel


def _generate_token() -> str:
    """Сгенерировать криптостойкий токен ссылки."""
    return secrets.token_urlsafe(32)


class CreateShareLinkCommand(BaseCommand):
    """Команда создания публичной ссылки на файл."""

    caller_id: str
    file_id: str
    access_level: str = FileAccessLevel.VIEW.value
    password: str | None = None
    expires_at: datetime | None = None
    max_uses: int | None = None


class CreateShareLinkHandler(BaseCommandHandler[CreateShareLinkCommand, PublicShareLinkDTO]):
    """Создание публичной ссылки."""

    REQUIRED_PERMISSION = "files.share"

    def __init__(
        self,
        file_repo: FileRepository,
        permission_checker: WorkspacePermissionCheckerPort,
        password_port: PasswordPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._file_repo = file_repo
        self._permission_checker = permission_checker
        self._password_port = password_port
        self._event_bus = event_bus

    async def handle(self, command: CreateShareLinkCommand) -> PublicShareLinkDTO:
        file = await self._file_repo.get_by_id(Id.from_string(command.file_id))
        if file is None:
            raise FileNotFoundException(id=command.file_id)
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=str(file.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )
        link = file.create_share_link(
            token=_generate_token(),
            access_level=FileAccessLevel(command.access_level),
            created_by=Id.from_string(command.caller_id),
            password_hash=self._password_port.hash_password(command.password) if command.password else None,
            expires_at=command.expires_at,
            max_uses=command.max_uses,
        )
        await self._file_repo.update(file)
        await self._event_bus.publish_all(file.clear_domain_events())
        return share_link_to_dto(link)


class RevokeShareLinkCommand(BaseCommand):
    """Команда отзыва публичной ссылки."""

    caller_id: str
    file_id: str
    link_id: str


class RevokeShareLinkHandler(BaseCommandHandler[RevokeShareLinkCommand, None]):
    """Отзыв публичной ссылки."""

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

    async def handle(self, command: RevokeShareLinkCommand) -> None:
        file = await self._file_repo.get_by_id(Id.from_string(command.file_id))
        if file is None:
            raise FileNotFoundException(id=command.file_id)
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=str(file.workspace_id),
            permission=self.REQUIRED_PERMISSION,
        )
        link_id = Id.from_string(command.link_id)
        if not any(l.id == link_id for l in file.share_links):
            raise PublicShareLinkNotFoundException(id=command.link_id)
        file.revoke_share_link(link_id)
        await self._file_repo.update(file)
        await self._event_bus.publish_all(file.clear_domain_events())


class AccessShareLinkCommand(BaseCommand):
    """
    Команда перехода по публичной ссылке (без авторизации).

    Атрибуты:
        token: Токен ссылки.
        password: Пароль (если установлен).
    """

    token: str
    password: str | None = None


class AccessShareLinkHandler(BaseCommandHandler[AccessShareLinkCommand, dict]):
    """
    Переход по публичной ссылке.

    Возвращает file_id и storage_path для скачивания.
    Инкрементирует current_uses.
    """

    def __init__(
        self,
        file_repo: FileRepository,
        password_port: PasswordPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._file_repo = file_repo
        self._password_port = password_port
        self._event_bus = event_bus

    async def handle(self, command: AccessShareLinkCommand) -> dict:
        # Найти файл по токену в его share_links — для простоты ищем перебором.
        # На практике должен быть прямой репо-метод. Пока — fallback через search.
        # NB: Эффективная реализация требует индекса по токену в БД;
        # здесь мы делегируем в репо через workspace-широкий поиск.
        file = await self._find_file_by_token(command.token)
        if file is None:
            raise PublicShareLinkNotFoundException(id=command.token)

        # Передаём verify_password из PasswordPort в агрегат для верификации хэша.
        file.access_share_link(
            token=command.token,
            password=command.password,
            verify_password=self._password_port.verify_password,
        )
        await self._file_repo.update(file)
        await self._event_bus.publish_all(file.clear_domain_events())
        return {
            "file_id": str(file.id),
            "storage_path": file.storage_path,
            "name": file.name,
            "mime_type": file.mime_type,
            "size_bytes": file.size.value,
        }

    async def _find_file_by_token(self, token: str):
        """Поиск файла по токену ссылки (сканирование).

        Метод присутствует на репо как ``get_by_share_token`` —
        реализация подключается на инфраструктурном слое.
        """
        get_by_token = getattr(self._file_repo, "get_by_share_token", None)
        if get_by_token is None:
            return None
        return await get_by_token(token)
