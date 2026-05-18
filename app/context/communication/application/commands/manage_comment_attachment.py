from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.url_vo import Url
from app.context.filestorage.domain.entities.file_tag import FileTag
from app.context.filestorage.domain.repositories.file_repository import FileRepository

from app.context.communication.application.dto.attachment_dto import AttachmentDTO
from app.context.communication.application.dto.mappers import attachment_to_dto
from app.context.communication.application.exceptions.authorization_exceptions import (
    CommentTargetForbiddenException,
)
from app.context.communication.application.ports.integration.inboard.comment_target_access_port import (
    CommentTargetAccessPort,
)
from app.context.communication.application.ports.integration.inboard.file_attachment_port import (
    FileAttachmentPort,
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
        file_repo: FileRepository,
        file_attachment_port: FileAttachmentPort,
        target_access: CommentTargetAccessPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = comment_repo
        self._file_repo = file_repo
        self._file_attachment_port = file_attachment_port
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

        # Резолвим workspace_id через target → project → workspace.
        workspace_id = await self._target_access.resolve_workspace_id(
            target_type=comment.target_type,
            target_id=str(comment.target_id),
        )
        if workspace_id is None:
            raise CommentTargetForbiddenException(
                target_type=comment.target_type.value,
                target_id=str(comment.target_id),
                user_id=command.caller_id,
                reason="не удалось определить workspace для квоты хранилища",
            )

        result = await self._file_attachment_port.upload_attachment(
            workspace_id=workspace_id,
            uploader_id=command.caller_id,
            filename=command.filename,
            file_data=command.file_data,
            content_type=command.content_type,
        )

        # Помечаем файл системными тегами:
        # * ``source:comment`` — для фильтра «Источник = Комментарий» в UI.
        # * ``project:<id>`` — чтобы файл попадал в фильтр проекта в UI
        #   документов, не зависимо от типа цели (task/epic/sprint/...).
        file = await self._file_repo.get_by_id(Id.from_string(result.file_id))
        if file is not None:
            wanted_tags: list[str] = ["source:comment"]
            project_id = await self._target_access.resolve_project_id(
                target_type=comment.target_type,
                target_id=str(comment.target_id),
            )
            if project_id:
                wanted_tags.append(f"project:{project_id}")
            existing = {tag.name for tag in file.tags}
            tags_changed = False
            for name in wanted_tags:
                if name not in existing:
                    file.add_tag(FileTag(name=name))
                    tags_changed = True
            if tags_changed:
                await self._file_repo.update(file)

        attachment = Attachment(
            id=Id.from_string(result.file_id),
            file_id=Id.from_string(result.file_id),
            url=Url(value=result.url) if result.url else None,
            attachment_type=AttachmentType(command.attachment_type),
            name=command.filename,
            size_bytes=result.size_bytes,
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
        file_attachment_port: FileAttachmentPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = comment_repo
        self._file_attachment_port = file_attachment_port
        self._event_bus = event_bus

    async def handle(self, command: RemoveCommentAttachmentCommand) -> None:
        comment = await self._repo.get_by_id(Id.from_string(command.comment_id))
        if comment is None:
            raise CommentNotFoundException(command.comment_id)

        if str(comment.author_id) != command.caller_id:
            raise NotCommentAuthorException()

        # Сохраняем file_id вложения до удаления из агрегата.
        attachment = next(
            (a for a in comment.attachments if str(a.id) == command.attachment_id),
            None,
        )
        file_id = str(attachment.file_id) if attachment else None

        comment.remove_attachment(Id.from_string(command.attachment_id))
        await self._repo.update(comment)
        await self._event_bus.publish_all(comment.clear_domain_events())

        # Освобождаем квоту и удаляем blob в FileStorage BC.
        if file_id:
            await self._file_attachment_port.delete_attachment(file_id)
