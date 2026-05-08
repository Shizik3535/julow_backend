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
from app.context.communication.application.ports.integration.inboard.comment_target_access_port import (
    CommentTargetAccessPort,
)
from app.context.communication.domain.entities.attachment import Attachment
from app.context.communication.domain.exceptions.comment_exceptions import (
    CommentNotFoundException,
    NotCommentAuthorException,
)
from app.context.communication.domain.repositories.comment_repository import (
    CommentRepository,
)
from app.context.communication.domain.value_objects.attachment_type import (
    AttachmentType,
)


class AddCommentAttachmentCommand(BaseCommand):
    """
    Команда добавления вложения к комментарию.

    Файл загружается через FileStoragePort внутри handler'а; снаружи
    передаются сами байты, имя и MIME-тип. ``file_id`` генерируется
    handler'ом — это единый атомарный шаг "upload + регистрация".

    Атрибуты:
        comment_id: ID комментария.
        caller_id: ID инициатора (только автор комментария).
        filename: Имя файла (берётся из ``UploadFile.filename``).
        file_data: Содержимое файла.
        content_type: MIME-тип.
        attachment_type: Тип вложения (image/video/file/link/voice).
    """

    comment_id: str
    caller_id: str
    filename: str
    file_data: bytes
    content_type: str = "application/octet-stream"
    attachment_type: str = "file"


class AddCommentAttachmentHandler(
    BaseCommandHandler[AddCommentAttachmentCommand, AttachmentDTO]
):
    """
    Обработчик добавления вложения.

    Загружает файл в S3 через ``FileStoragePort``, формирует ссылку
    и регистрирует ``Attachment`` в агрегате ``Comment``.
    """

    def __init__(
        self,
        comment_repo: CommentRepository,
        file_storage: FileStoragePort,
        target_access: CommentTargetAccessPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = comment_repo
        self._file_storage = file_storage
        self._target_access = target_access
        self._event_bus = event_bus

    async def handle(self, command: AddCommentAttachmentCommand) -> AttachmentDTO:
        comment = await self._repo.get_by_id(Id.from_string(command.comment_id))
        if comment is None:
            raise CommentNotFoundException(command.comment_id)

        if str(comment.author_id) != command.caller_id:
            raise NotCommentAuthorException()

        await self._target_access.require_access(
            user_id=command.caller_id,
            target_type=comment.target_type,
            target_id=str(comment.target_id),
        )

        file_id = Id.generate()
        key = (
            f"comments/{command.comment_id}/attachments/"
            f"{uuid.uuid4()}/{command.filename}"
        )
        await self._file_storage.upload(
            key=key,
            data=command.file_data,
            content_type=command.content_type,
        )

        # Бессрочный (публичный) URL — для приватных файлов следует использовать
        # подписанный URL с TTL, генерируемый по запросу.
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
        comment.add_attachment(attachment)
        await self._repo.update(comment)
        await self._event_bus.publish_all(comment.clear_domain_events())

        return attachment_to_dto(attachment)


class RemoveCommentAttachmentCommand(BaseCommand):
    """
    Команда удаления вложения комментария.

    Атрибуты:
        comment_id: ID комментария.
        attachment_id: ID вложения.
        caller_id: ID инициатора (только автор).
    """

    comment_id: str
    attachment_id: str
    caller_id: str


class RemoveCommentAttachmentHandler(
    BaseCommandHandler[RemoveCommentAttachmentCommand, None]
):
    """Обработчик удаления вложения."""

    def __init__(
        self,
        comment_repo: CommentRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = comment_repo
        self._event_bus = event_bus

    async def handle(self, command: RemoveCommentAttachmentCommand) -> None:
        comment = await self._repo.get_by_id(Id.from_string(command.comment_id))
        if comment is None:
            raise CommentNotFoundException(command.comment_id)

        if str(comment.author_id) != command.caller_id:
            raise NotCommentAuthorException()

        comment.remove_attachment(Id.from_string(command.attachment_id))
        await self._repo.update(comment)
        await self._event_bus.publish_all(comment.clear_domain_events())
