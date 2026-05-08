"""Команды управления вложениями сообщений чата."""

from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.url_vo import Url

from app.context.communication.application.dto.attachment_dto import AttachmentDTO
from app.context.communication.application.dto.mappers import attachment_to_dto
from app.context.communication.application.exceptions.authorization_exceptions import (
    NotMessageAuthorException,
)
from app.context.communication.application.ports.integration.inboard.file_attachment_port import (
    FileAttachmentPort,
)
from app.context.communication.domain.entities.attachment import Attachment
from app.context.communication.domain.exceptions.chat_exceptions import (
    ChatNotFoundException,
)
from app.context.communication.domain.exceptions.message_exceptions import (
    MessageNotFoundException,
)
from app.context.communication.domain.repositories.chat_repository import (
    ChatRepository,
)
from app.context.communication.domain.repositories.message_repository import (
    MessageRepository,
)
from app.context.communication.domain.value_objects.attachment_type import (
    AttachmentType,
)


class AddMessageAttachmentCommand(BaseCommand):
    """Добавить вложение к сообщению (только автор).

    Файл загружается через FileStoragePort, ``file_id`` генерируется
    handler'ом.
    """

    caller_id: str
    message_id: str
    filename: str
    file_data: bytes
    content_type: str = "application/octet-stream"
    attachment_type: str = "file"


class AddMessageAttachmentHandler(
    BaseCommandHandler[AddMessageAttachmentCommand, AttachmentDTO]
):
    """
    Обработчик добавления вложения к сообщению.

    Делегирует загрузку файла в FileStorage BC через ``FileAttachmentPort``
    (создание агрегата ``File``, учёт квоты, события).

    Для DM-чатов (``chat.workspace_id is None``) attachment не поддерживается —
    выбрасывается ``MessageNotFoundException`` (нет квоты хранилища).
    """

    def __init__(
        self,
        message_repo: MessageRepository,
        chat_repo: ChatRepository,
        file_attachment_port: FileAttachmentPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = message_repo
        self._chat_repo = chat_repo
        self._file_attachment_port = file_attachment_port
        self._event_bus = event_bus

    async def handle(self, command: AddMessageAttachmentCommand) -> AttachmentDTO:
        message = await self._repo.get_by_id(Id.from_string(command.message_id))
        if message is None:
            raise MessageNotFoundException(command.message_id)

        if str(message.sender_id) != command.caller_id:
            raise NotMessageAuthorException()

        chat = await self._chat_repo.get_by_id(message.chat_id)
        if chat is None:
            raise ChatNotFoundException(str(message.chat_id))
        if chat.workspace_id is None:
            # DM/private chat — нет workspace для квоты. Загрузка вложений
            # в DM не поддерживается через FileStorage BC.
            raise MessageNotFoundException(command.message_id)

        result = await self._file_attachment_port.upload_attachment(
            workspace_id=str(chat.workspace_id),
            uploader_id=command.caller_id,
            filename=command.filename,
            file_data=command.file_data,
            content_type=command.content_type,
        )

        attachment = Attachment(
            id=Id.from_string(result.file_id),
            file_id=Id.from_string(result.file_id),
            url=Url(value=result.url) if result.url else None,
            attachment_type=AttachmentType(command.attachment_type),
            name=command.filename,
            size_bytes=result.size_bytes,
            preview_url=None,
        )
        message.add_attachment(attachment)
        await self._repo.update(message)
        await self._event_bus.publish_all(message.clear_domain_events())
        return attachment_to_dto(attachment)


class RemoveMessageAttachmentCommand(BaseCommand):
    """Удалить вложение сообщения (только автор)."""

    caller_id: str
    message_id: str
    attachment_id: str


class RemoveMessageAttachmentHandler(
    BaseCommandHandler[RemoveMessageAttachmentCommand, None]
):
    """Обработчик удаления вложения сообщения."""

    def __init__(
        self,
        message_repo: MessageRepository,
        file_attachment_port: FileAttachmentPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = message_repo
        self._file_attachment_port = file_attachment_port
        self._event_bus = event_bus

    async def handle(self, command: RemoveMessageAttachmentCommand) -> None:
        message = await self._repo.get_by_id(Id.from_string(command.message_id))
        if message is None:
            raise MessageNotFoundException(command.message_id)

        if str(message.sender_id) != command.caller_id:
            raise NotMessageAuthorException()

        attachment = next(
            (a for a in message.attachments if str(a.id) == command.attachment_id),
            None,
        )
        file_id = str(attachment.file_id) if attachment else None

        message.remove_attachment(Id.from_string(command.attachment_id))
        await self._repo.update(message)
        await self._event_bus.publish_all(message.clear_domain_events())

        if file_id:
            await self._file_attachment_port.delete_attachment(file_id)
