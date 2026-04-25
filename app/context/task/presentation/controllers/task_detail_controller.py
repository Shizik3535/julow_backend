from __future__ import annotations

from fastapi import Depends

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageData,
    MessageResponse,
    SuccessResponse,
)

from app.context.task.application.commands.update_task_info import (
    UpdateTaskInfoCommand,
    UpdateTaskInfoHandler,
)
from app.context.task.application.commands.delete_task import (
    DeleteTaskCommand,
    DeleteTaskHandler,
)
from app.context.task.application.commands.archive_task import (
    ArchiveTaskCommand,
    ArchiveTaskHandler,
)
from app.context.task.application.commands.restore_task import (
    RestoreTaskCommand,
    RestoreTaskHandler,
)
from app.context.task.application.commands.change_task_status import (
    ChangeTaskStatusCommand,
    ChangeTaskStatusHandler,
)
from app.context.task.application.commands.change_task_priority import (
    ChangeTaskPriorityCommand,
    ChangeTaskPriorityHandler,
)
from app.context.task.application.commands.change_task_type import (
    ChangeTaskTypeCommand,
    ChangeTaskTypeHandler,
)
from app.context.task.application.commands.move_task import (
    MoveTaskCommand,
    MoveTaskHandler,
)
from app.context.task.application.commands.set_effort_estimate import (
    SetEffortEstimateCommand,
    SetEffortEstimateHandler,
)
from app.context.task.application.commands.set_actual_effort import (
    SetActualEffortCommand,
    SetActualEffortHandler,
)
from app.context.task.application.commands.update_task_progress import (
    UpdateTaskProgressCommand,
    UpdateTaskProgressHandler,
)
from app.context.task.application.commands.compute_task_progress import (
    ComputeTaskProgressCommand,
    ComputeTaskProgressHandler,
)
from app.context.task.application.queries.get_task import (
    GetTaskHandler,
    GetTaskQuery,
)
from app.context.task.presentation.dependencies import (
    get_current_user_id,
    get_task_board_port,
    get_task_changelog_repository,
    get_task_event_bus,
    get_task_permission_checker,
    get_task_repository,
)
from app.context.task.presentation.schemas.requests.update_task_info_request import UpdateTaskInfoRequest
from app.context.task.presentation.schemas.requests.change_task_status_request import ChangeTaskStatusRequest
from app.context.task.presentation.schemas.requests.change_task_priority_request import ChangeTaskPriorityRequest
from app.context.task.presentation.schemas.requests.change_task_type_request import ChangeTaskTypeRequest
from app.context.task.presentation.schemas.requests.move_task_request import MoveTaskRequest
from app.context.task.presentation.schemas.requests.set_effort_estimate_request import SetEffortEstimateRequest
from app.context.task.presentation.schemas.requests.set_actual_effort_request import SetActualEffortRequest
from app.context.task.presentation.schemas.requests.update_task_progress_request import UpdateTaskProgressRequest
from app.context.task.presentation.schemas.responses.task_response import TaskResponse


class TaskDetailController(BaseController):
    """
    Контроллер операций с конкретной задачей.

    Endpoint'ы:
        GET    /{task_id}                     — Получить задачу
        PATCH  /{task_id}                     — Обновить информацию
        DELETE /{task_id}                     — Удалить задачу
        POST   /{task_id}/archive             — Архивировать
        POST   /{task_id}/restore             — Восстановить
        POST   /{task_id}/change-status       — Сменить статус
        POST   /{task_id}/change-priority     — Сменить приоритет
        POST   /{task_id}/change-type         — Сменить тип
        POST   /{task_id}/move                — Переместить на доске
        PATCH  /{task_id}/effort-estimate     — Установить оценку
        PATCH  /{task_id}/actual-effort       — Установить факт
        PATCH  /{task_id}/progress            — Обновить прогресс
        POST   /{task_id}/compute-progress    — Вычислить прогресс
    """

    def __init__(self) -> None:
        super().__init__(prefix="/tasks", tags=["Task / Detail"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/{task_id}",
            self.get_task,
            methods=["GET"],
            response_model=SuccessResponse[TaskResponse],
            summary="Получить задачу",
            description="Возвращает данные задачи по UUID.",
            responses={
                200: {"description": "Данные задачи"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}",
            self.update_task_info,
            methods=["PATCH"],
            response_model=MessageResponse,
            summary="Обновить информацию задачи",
            description="Обновляет заголовок, описание, даты задачи.",
            responses={
                200: {"description": "Информация обновлена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}",
            self.delete_task,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить задачу",
            description="Удаляет задачу.",
            responses={
                200: {"description": "Задача удалена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/archive",
            self.archive_task,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Архивировать задачу",
            description="Перемещает задачу в архив.",
            responses={
                200: {"description": "Задача архивирована"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/restore",
            self.restore_task,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Восстановить задачу",
            description="Восстанавливает задачу из архива.",
            responses={
                200: {"description": "Задача восстановлена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/change-status",
            self.change_task_status,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Сменить статус задачи",
            description="Сменяет workflow-статус задачи.",
            responses={
                200: {"description": "Статус изменён"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
                409: {"description": "Переход не разрешён", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/change-priority",
            self.change_task_priority,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Сменить приоритет задачи",
            description="Сменяет приоритет задачи.",
            responses={
                200: {"description": "Приоритет изменён"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/change-type",
            self.change_task_type,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Сменить тип задачи",
            description="Сменяет тип задачи.",
            responses={
                200: {"description": "Тип изменён"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/move",
            self.move_task,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Переместить задачу на доске",
            description="Перемещает задачу в указанную колонку и позицию (drag-n-drop).",
            responses={
                200: {"description": "Задача перемещена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/effort-estimate",
            self.set_effort_estimate,
            methods=["PATCH"],
            response_model=MessageResponse,
            summary="Установить оценку усилия",
            description="Устанавливает оценку усилия задачи.",
            responses={
                200: {"description": "Оценка установлена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/actual-effort",
            self.set_actual_effort,
            methods=["PATCH"],
            response_model=MessageResponse,
            summary="Установить фактическое усилие",
            description="Устанавливает фактическое усилие задачи.",
            responses={
                200: {"description": "Фактическое усилие установлено"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/progress",
            self.update_task_progress,
            methods=["PATCH"],
            response_model=MessageResponse,
            summary="Обновить прогресс задачи",
            description="Устанавливает прогресс задачи (0–100).",
            responses={
                200: {"description": "Прогресс обновлён"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/compute-progress",
            self.compute_task_progress,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Вычислить прогресс задачи",
            description="Вычисляет прогресс задачи на основе чек-листов.",
            responses={
                200: {"description": "Прогресс вычислен"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
            },
        )

    async def get_task(
        self,
        task_id: str,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
    ) -> SuccessResponse[TaskResponse]:
        """Получить задачу по ID."""
        handler = GetTaskHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
        )
        query = GetTaskQuery(caller_id=caller_id, task_id=task_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=TaskResponse.model_validate(dto.model_dump()))

    async def update_task_info(
        self,
        task_id: str,
        body: UpdateTaskInfoRequest,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        changelog_repo=Depends(get_task_changelog_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Обновить информацию задачи."""
        handler = UpdateTaskInfoHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = UpdateTaskInfoCommand(
            task_id=task_id,
            changed_by=caller_id,
            title=body.title,
            description_content=body.description_content,
            description_format=body.description_format,
            start_date=body.start_date,
            due_date=body.due_date,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Информация задачи обновлена"))

    async def delete_task(
        self,
        task_id: str,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Удалить задачу."""
        handler = DeleteTaskHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = DeleteTaskCommand(
            caller_id=caller_id,
            task_id=task_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Задача удалена"))

    async def archive_task(
        self,
        task_id: str,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Архивировать задачу."""
        handler = ArchiveTaskHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = ArchiveTaskCommand(
            caller_id=caller_id,
            task_id=task_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Задача архивирована"))

    async def restore_task(
        self,
        task_id: str,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Восстановить задачу из архива."""
        handler = RestoreTaskHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = RestoreTaskCommand(
            caller_id=caller_id,
            task_id=task_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Задача восстановлена"))

    async def change_task_status(
        self,
        task_id: str,
        body: ChangeTaskStatusRequest,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        changelog_repo=Depends(get_task_changelog_repository),
        permission_checker=Depends(get_task_permission_checker),
        board_port=Depends(get_task_board_port),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Сменить workflow-статус задачи."""
        handler = ChangeTaskStatusHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            board_port=board_port,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = ChangeTaskStatusCommand(
            task_id=task_id,
            new_status_id=body.new_status_id,
            changed_by=caller_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Статус задачи изменён"))

    async def change_task_priority(
        self,
        task_id: str,
        body: ChangeTaskPriorityRequest,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        changelog_repo=Depends(get_task_changelog_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Сменить приоритет задачи."""
        handler = ChangeTaskPriorityHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = ChangeTaskPriorityCommand(
            task_id=task_id,
            new_priority=body.priority,
            changed_by=caller_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Приоритет задачи изменён"))

    async def change_task_type(
        self,
        task_id: str,
        body: ChangeTaskTypeRequest,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        changelog_repo=Depends(get_task_changelog_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Сменить тип задачи."""
        handler = ChangeTaskTypeHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = ChangeTaskTypeCommand(
            task_id=task_id,
            new_type=body.task_type,
            changed_by=caller_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Тип задачи изменён"))

    async def move_task(
        self,
        task_id: str,
        body: MoveTaskRequest,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        changelog_repo=Depends(get_task_changelog_repository),
        permission_checker=Depends(get_task_permission_checker),
        board_port=Depends(get_task_board_port),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Переместить задачу на доске."""
        handler = MoveTaskHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            board_port=board_port,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = MoveTaskCommand(
            task_id=task_id,
            column_id=body.column_id,
            position=body.position,
            changed_by=caller_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Задача перемещена"))

    async def set_effort_estimate(
        self,
        task_id: str,
        body: SetEffortEstimateRequest,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        changelog_repo=Depends(get_task_changelog_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Установить оценку усилия."""
        handler = SetEffortEstimateHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = SetEffortEstimateCommand(
            caller_id=caller_id,
            task_id=task_id,
            value=body.value,
            unit=body.unit,
            changed_by=caller_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Оценка усилия установлена"))

    async def set_actual_effort(
        self,
        task_id: str,
        body: SetActualEffortRequest,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        changelog_repo=Depends(get_task_changelog_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Установить фактическое усилие."""
        handler = SetActualEffortHandler(
            task_repo=task_repo,
            changelog_repo=changelog_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = SetActualEffortCommand(
            caller_id=caller_id,
            task_id=task_id,
            value=body.value,
            unit=body.unit,
            changed_by=caller_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Фактическое усилие установлено"))

    async def update_task_progress(
        self,
        task_id: str,
        body: UpdateTaskProgressRequest,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Обновить прогресс задачи."""
        handler = UpdateTaskProgressHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = UpdateTaskProgressCommand(
            caller_id=caller_id,
            task_id=task_id,
            progress=body.progress,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Прогресс задачи обновлён"))

    async def compute_task_progress(
        self,
        task_id: str,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Вычислить прогресс задачи на основе чек-листов."""
        handler = ComputeTaskProgressHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = ComputeTaskProgressCommand(
            caller_id=caller_id,
            task_id=task_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Прогресс задачи вычислен"))
