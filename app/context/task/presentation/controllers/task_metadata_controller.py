from __future__ import annotations

from fastapi import Depends, UploadFile

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageData,
    MessageResponse,
    SuccessResponse,
)

from app.context.task.application.commands.add_task_label import (
    AddTaskLabelCommand,
    AddTaskLabelHandler,
)
from app.context.task.application.commands.remove_task_label import (
    RemoveTaskLabelCommand,
    RemoveTaskLabelHandler,
)
from app.context.task.application.commands.add_task_watcher import (
    AddTaskWatcherCommand,
    AddTaskWatcherHandler,
)
from app.context.task.application.commands.remove_task_watcher import (
    RemoveTaskWatcherCommand,
    RemoveTaskWatcherHandler,
)
from app.context.task.application.commands.add_task_attachment import (
    AddTaskAttachmentCommand,
    AddTaskAttachmentHandler,
)
from app.context.task.application.commands.remove_task_attachment import (
    RemoveTaskAttachmentCommand,
    RemoveTaskAttachmentHandler,
)
from app.context.task.application.commands.set_task_custom_field import (
    SetTaskCustomFieldCommand,
    SetTaskCustomFieldHandler,
)
from app.context.task.application.commands.remove_task_custom_field import (
    RemoveTaskCustomFieldCommand,
    RemoveTaskCustomFieldHandler,
)
from app.context.task.application.commands.set_task_recurrence import (
    SetTaskRecurrenceCommand,
    SetTaskRecurrenceHandler,
)
from app.context.task.application.commands.remove_task_recurrence import (
    RemoveTaskRecurrenceCommand,
    RemoveTaskRecurrenceHandler,
)
from app.context.task.presentation.dependencies import (
    get_current_user_id,
    get_file_storage_port,
    get_task_changelog_repository,
    get_task_event_bus,
    get_task_file_attachment_port,
    get_task_permission_checker,
    get_task_project_port,
    get_task_repository,
)
from app.context.task.presentation.schemas.requests.add_task_label_request import AddTaskLabelRequest
from app.context.task.presentation.schemas.requests.add_task_watcher_request import AddTaskWatcherRequest
from app.context.task.presentation.schemas.requests.set_task_custom_field_request import SetTaskCustomFieldRequest
from app.context.task.presentation.schemas.requests.set_task_recurrence_request import SetTaskRecurrenceRequest


class TaskMetadataController(BaseController):
    """
    Контроллер метаданных задачи (метки, наблюдатели, вложения, кастомные поля, повторение).

    Endpoint'ы:
        POST   /{task_id}/labels                        — Добавить метку
        DELETE /{task_id}/labels/{label}                — Удалить метку
        POST   /{task_id}/watchers                      — Добавить наблюдателя
        DELETE /{task_id}/watchers/{user_id}            — Удалить наблюдателя
        POST   /{task_id}/attachments                   — Добавить вложение
        DELETE /{task_id}/attachments/{file_id}         — Удалить вложение
        POST   /{task_id}/custom-fields                 — Установить кастомное поле
        DELETE /{task_id}/custom-fields/{field_name}    — Удалить кастомное поле
        POST   /{task_id}/recurrence                    — Установить повторение
        DELETE /{task_id}/recurrence                    — Удалить повторение
    """

    def __init__(self) -> None:
        super().__init__(prefix="/tasks", tags=["Task / Metadata"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/{task_id}/labels",
            self.add_label,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Добавить метку",
            description="Добавляет метку задаче.",
            responses={
                200: {"description": "Метка добавлена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
                409: {"description": "Дубликат метки", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/labels/{label}",
            self.remove_label,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить метку",
            description="Удаляет метку с задачи.",
            responses={
                200: {"description": "Метка удалена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/watchers",
            self.add_watcher,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Добавить наблюдателя",
            description="Добавляет наблюдателя к задаче.",
            responses={
                200: {"description": "Наблюдатель добавлен"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
                409: {"description": "Наблюдатель уже подписан", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/watchers/{user_id}",
            self.remove_watcher,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить наблюдателя",
            description="Удаляет наблюдателя из задачи.",
            responses={
                200: {"description": "Наблюдатель удалён"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/attachments",
            self.add_attachment,
            methods=["POST"],
            response_model=SuccessResponse[dict],
            status_code=201,
            summary="Добавить вложение",
            description="Загружает файл и привязывает его к задаче.",
            responses={
                201: {"description": "Вложение добавлено"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/attachments/{file_id}",
            self.remove_attachment,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить вложение",
            description="Удаляет вложение задачи.",
            responses={
                200: {"description": "Вложение удалено"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача или вложение не найдены", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/custom-fields",
            self.set_custom_field,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Установить кастомное поле",
            description="Устанавливает значение кастомного поля задачи.",
            responses={
                200: {"description": "Поле установлено"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/custom-fields/{field_name}",
            self.remove_custom_field,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить кастомное поле",
            description="Удаляет кастомное поле задачи.",
            responses={
                200: {"description": "Поле удалено"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/recurrence",
            self.set_recurrence,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Установить повторение",
            description="Устанавливает конфигурацию повторения задачи.",
            responses={
                200: {"description": "Повторение установлено"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/recurrence",
            self.remove_recurrence,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить повторение",
            description="Удаляет конфигурацию повторения задачи.",
            responses={
                200: {"description": "Повторение удалено"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
            },
        )

    async def add_label(
        self,
        task_id: str,
        body: AddTaskLabelRequest,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Добавить метку."""
        handler = AddTaskLabelHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = AddTaskLabelCommand(
            caller_id=caller_id,
            task_id=task_id,
            name=body.name,
            color=body.color,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Метка добавлена"))

    async def remove_label(
        self,
        task_id: str,
        label: str,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Удалить метку."""
        handler = RemoveTaskLabelHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = RemoveTaskLabelCommand(
            caller_id=caller_id,
            task_id=task_id,
            label_name=label,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Метка удалена"))

    async def add_watcher(
        self,
        task_id: str,
        body: AddTaskWatcherRequest,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Добавить наблюдателя."""
        handler = AddTaskWatcherHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = AddTaskWatcherCommand(
            caller_id=caller_id,
            task_id=task_id,
            user_id=body.user_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Наблюдатель добавлен"))

    async def remove_watcher(
        self,
        task_id: str,
        user_id: str,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Удалить наблюдателя."""
        handler = RemoveTaskWatcherHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = RemoveTaskWatcherCommand(
            caller_id=caller_id,
            task_id=task_id,
            user_id=user_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Наблюдатель удалён"))

    async def add_attachment(
        self,
        task_id: str,
        file: UploadFile,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
        file_attachment_port=Depends(get_task_file_attachment_port),
        project_port=Depends(get_task_project_port),
        event_bus=Depends(get_task_event_bus),
    ) -> SuccessResponse[dict]:
        """Добавить вложение."""
        file_data = await file.read()
        handler = AddTaskAttachmentHandler(
            task_repo=task_repo,
            file_attachment_port=file_attachment_port,
            project_port=project_port,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = AddTaskAttachmentCommand(
            caller_id=caller_id,
            task_id=task_id,
            filename=file.filename or "unnamed",
            file_data=file_data,
            content_type=file.content_type or "application/octet-stream",
            uploaded_by=caller_id,
        )
        file_id = await handler.handle(command)
        return SuccessResponse(data={"file_id": file_id})

    async def remove_attachment(
        self,
        task_id: str,
        file_id: str,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
        file_attachment_port=Depends(get_task_file_attachment_port),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Удалить вложение."""
        handler = RemoveTaskAttachmentHandler(
            task_repo=task_repo,
            file_attachment_port=file_attachment_port,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = RemoveTaskAttachmentCommand(
            caller_id=caller_id,
            task_id=task_id,
            file_id=file_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Вложение удалено"))

    async def set_custom_field(
        self,
        task_id: str,
        body: SetTaskCustomFieldRequest,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        changelog_repo=Depends(get_task_changelog_repository),
        project_port=Depends(get_task_project_port),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Установить кастомное поле."""
        handler = SetTaskCustomFieldHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            project_port=project_port,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = SetTaskCustomFieldCommand(
            caller_id=caller_id,
            task_id=task_id,
            field_name=body.field_name,
            value=body.value,
            changed_by=caller_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Кастомное поле установлено"))

    async def remove_custom_field(
        self,
        task_id: str,
        field_name: str,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        changelog_repo=Depends(get_task_changelog_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Удалить кастомное поле."""
        handler = RemoveTaskCustomFieldHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = RemoveTaskCustomFieldCommand(
            caller_id=caller_id,
            task_id=task_id,
            field_name=field_name,
            changed_by=caller_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Кастомное поле удалено"))

    async def set_recurrence(
        self,
        task_id: str,
        body: SetTaskRecurrenceRequest,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        changelog_repo=Depends(get_task_changelog_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Установить конфигурацию повторения."""
        handler = SetTaskRecurrenceHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = SetTaskRecurrenceCommand(
            caller_id=caller_id,
            task_id=task_id,
            pattern=body.pattern,
            interval=body.interval,
            end_date=body.end_date,
            max_occurrences=body.max_occurrences,
            changed_by=caller_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Повторение установлено"))

    async def remove_recurrence(
        self,
        task_id: str,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Удалить конфигурацию повторения."""
        handler = RemoveTaskRecurrenceHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = RemoveTaskRecurrenceCommand(
            caller_id=caller_id,
            task_id=task_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Повторение удалено"))
