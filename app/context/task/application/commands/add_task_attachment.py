from __future__ import annotations

import uuid

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.ports.file_storage.file_storage_port import FileStoragePort
from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.ports.authorization.task_permission_checker_port import (
    TaskPermissionCheckerPort,
)
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.repositories.task_repository import TaskRepository


class AddTaskAttachmentCommand(BaseCommand):
    """
    Команда добавления вложения задаче.

    Атрибуты:
        task_id: ID задачи.
        filename: Имя файла.
        file_data: Содержимое файла.
        content_type: MIME-тип.
        uploaded_by: ID загрузившего.
    """

    caller_id: str
    task_id: str
    filename: str
    file_data: bytes
    content_type: str = "application/octet-stream"
    uploaded_by: str = ""


class AddTaskAttachmentHandler(BaseCommandHandler[AddTaskAttachmentCommand, str]):
    """
    Обработчик добавления вложения.

    Загружает файл через FileStoragePort, сохраняет ссылку в Task.
    Возвращает file_id.
    """

    REQUIRED_PERMISSION = "tasks.update"

    def __init__(
        self,
        task_repo: TaskRepository,
        file_storage: FileStoragePort,
        permission_checker: TaskPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._file_storage = file_storage
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: AddTaskAttachmentCommand) -> str:
        task = await self._task_repo.get_by_id(Id.from_string(command.task_id))
        if task is None:
            raise TaskNotFoundException(id=command.task_id)

        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            project_id=str(task.project_id),
            permission=self.REQUIRED_PERMISSION,
        )

        file_id = Id.generate()
        key = f"tasks/{command.task_id}/attachments/{uuid.uuid4()}/{command.filename}"
        await self._file_storage.upload(
            key=key,
            data=command.file_data,
            content_type=command.content_type,
        )

        task.add_attachment(
            file_id=file_id,
            filename=command.filename,
            size_bytes=len(command.file_data),
            uploaded_by=Id.from_string(command.uploaded_by),
        )
        await self._task_repo.update(task)
        await self._event_bus.publish_all(task.clear_domain_events())
        return str(file_id)
