"""Команды управления вложениями сообщений чата."""

from __future__ import annotations

import uuid

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.ports.file_storage.file_storage_port import FileStoragePort
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.url_vo import Url

from app.context.communication.application.dto.attachment_dto import AttachmentDTO
from app.context.communication.application.dto.mappers import attachment_to_dto
from app.context.communication.application.exceptions.authorization_exceptions import (
    NotMessageAuthorException,
)
from app.context.communication.domain.entities.attachment import Attachment
from app.context.communication.domain.exceptions.message_exceptions import (
    MessageNotFoundException,
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
    def __init__(
        self,
        message_repo: MessageRepository,
        file_storage: FileStoragePort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = message_repo
        self._file_storage = file_storage
        self._event_bus = event_bus

    async def handle(self, command: AddMessageAttachmentCommand) -> AttachmentDTO:
        message = await self._repo.get_by_id(Id.from_string(command.message_id))
        if message is None:
            raise MessageNotFoundException(command.message_id)

        if str(message.sender_id) != command.caller_id:
            raise NotMessageAuthorException()

        file_id = Id.generate()
        key = (
            f"chats/{message.chat_id}/messages/{command.message_id}/"
            f"attachments/{uuid.uuid4()}/{command.filename}"
        )
        await self._file_storage.upload(
            key=key,
            data=command.file_data,
            content_type=command.content_type,
        )
        url_str = await self._file_storage.get_url(key=key, expires_in=None)

        attachment = Attachment(
            id=file_id,
            file_id=file_id,
            url=Url(value=url_str) if url_str else None,
            attachment_type=AttachmentType(command.attachment_type),
            name=command.filename,
            size_bytes=len(command.file_data),
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
    def __init__(
        self,
        message_repo: MessageRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = message_repo
        self._event_bus = event_bus

    async def handle(self, command: RemoveMessageAttachmentCommand) -> None:
        message = await self._repo.get_by_id(Id.from_string(command.message_id))
        if message is None:
            raise MessageNotFoundException(command.message_id)

        if str(message.sender_id) != command.caller_id:
            raise NotMessageAuthorException()

        message.remove_attachment(Id.from_string(command.attachment_id))
        await self._repo.update(message)
        await self._event_bus.publish_all(message.clear_domain_events())
