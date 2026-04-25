from __future__ import annotations

from fastapi import Depends, Query

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageData,
    MessageResponse,
    SuccessResponse,
)

from app.context.task.application.commands.add_task_relation import (
    AddTaskRelationCommand,
    AddTaskRelationHandler,
)
from app.context.task.application.commands.remove_task_relation import (
    RemoveTaskRelationCommand,
    RemoveTaskRelationHandler,
)
from app.context.task.presentation.dependencies import (
    get_current_user_id,
    get_task_event_bus,
    get_task_permission_checker,
    get_task_repository,
)
from app.context.task.presentation.schemas.requests.add_task_relation_request import AddTaskRelationRequest


class TaskRelationController(BaseController):
    """
    Контроллер связей между задачами.

    Endpoint'ы:
        POST   /{task_id}/relations                          — Добавить связь
        DELETE /{task_id}/relations/{related_task_id}        — Удалить связь
    """

    def __init__(self) -> None:
        super().__init__(prefix="/tasks", tags=["Task / Relations"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/{task_id}/relations",
            self.add_relation,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Добавить связь между задачами",
            description="Добавляет связь между задачами (BLOCKS, IS_BLOCKED_BY, RELATES_TO и т.д.).",
            responses={
                200: {"description": "Связь добавлена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
                409: {"description": "Циклическая зависимость или дубликат", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/relations/{related_task_id}",
            self.remove_relation,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить связь между задачами",
            description="Удаляет связь между задачами.",
            responses={
                200: {"description": "Связь удалена"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
            },
        )

    async def add_relation(
        self,
        task_id: str,
        body: AddTaskRelationRequest,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Добавить связь между задачами."""
        handler = AddTaskRelationHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = AddTaskRelationCommand(
            caller_id=caller_id,
            task_id=task_id,
            related_task_id=body.related_task_id,
            relation_type=body.relation_type,
            created_by=caller_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Связь добавлена"))

    async def remove_relation(
        self,
        task_id: str,
        related_task_id: str,
        relation_type: str = Query(default="", description="Тип связи"),
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Удалить связь между задачами."""
        handler = RemoveTaskRelationHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = RemoveTaskRelationCommand(
            caller_id=caller_id,
            task_id=task_id,
            related_task_id=related_task_id,
            relation_type=relation_type,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Связь удалена"))
