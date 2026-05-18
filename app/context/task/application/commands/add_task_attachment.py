from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.filestorage.domain.entities.file_tag import FileTag
from app.context.filestorage.domain.repositories.file_repository import FileRepository
from app.context.task.application.ports.authorization.task_permission_checker_port import (
    TaskPermissionCheckerPort,
)
from app.context.task.application.ports.integration.inboard.file_attachment_port import (
    FileAttachmentPort,
)
from app.context.task.application.ports.integration.inboard.project_port import (
    ProjectPort,
)
from app.context.task.domain.exceptions.task_exceptions import TaskNotFoundException
from app.context.task.domain.repositories.task_repository import TaskRepository


class AddTaskAttachmentCommand(BaseCommand):
    """
    Команда добавления вложения задаче.

    Файл регистрируется как полноценный агрегат ``File`` в FileStorage BC
    (учёт квоты, события, антивирус), а в ``Task.attachments`` сохраняется
    ссылка на ``file_id``.

    Атрибуты:
        task_id: ID задачи.
        filename: Имя файла.
        file_data: Содержимое файла.
        content_type: MIME-тип.
        uploaded_by: ID загрузившего (по умолчанию = caller_id).
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

    Делегирует загрузку файла в FileStorage BC через ``FileAttachmentPort``
    (создание агрегата ``File``, учёт квоты, события). В ``Task.attachments``
    сохраняется реальный ``file_id``.
    """

    REQUIRED_PERMISSION = "tasks.update_own"

    def __init__(
        self,
        task_repo: TaskRepository,
        file_repo: FileRepository,
        file_attachment_port: FileAttachmentPort,
        project_port: ProjectPort,
        permission_checker: TaskPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._task_repo = task_repo
        self._file_repo = file_repo
        self._file_attachment_port = file_attachment_port
        self._project_port = project_port
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

        # Резолвим workspace_id через project (для квоты FileStorage BC).
        project = await self._project_port.get_project(str(task.project_id))
        workspace_id = (project or {}).get("workspace_id")
        if workspace_id is None:
            raise TaskNotFoundException(id=command.task_id)

        uploader_id = command.uploaded_by or command.caller_id
        result = await self._file_attachment_port.upload_attachment(
            workspace_id=str(workspace_id),
            uploader_id=uploader_id,
            filename=command.filename,
            file_data=command.file_data,
            content_type=command.content_type,
        )

        # Помечаем файл системными тегами:
        # * ``source:task`` — чтобы UI документов умел фильтровать по
        #   источнику «Задача».
        # * ``project:<task.project_id>`` — чтобы файлы попадали в
        #   фильтр выбранного проекта в сайдбаре документов, не зависимо
        #   от того, в какой папке лежит сам файл. Без этого тега
        #   задачные вложения «теряются» при выборе проекта на UI.
        file = await self._file_repo.get_by_id(Id.from_string(result.file_id))
        if file is not None:
            wanted_tags: list[str] = ["source:task", f"project:{str(task.project_id)}"]
            existing = {tag.name for tag in file.tags}
            tags_changed = False
            for name in wanted_tags:
                if name not in existing:
                    file.add_tag(FileTag(name=name))
                    tags_changed = True
            if tags_changed:
                await self._file_repo.update(file)

        task.add_attachment(
            file_id=Id.from_string(result.file_id),
            filename=command.filename,
            size_bytes=result.size_bytes,
            uploaded_by=Id.from_string(uploader_id),
        )
        await self._task_repo.update(task)
        await self._event_bus.publish_all(task.clear_domain_events())
        return result.file_id
