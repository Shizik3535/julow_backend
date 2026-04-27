from __future__ import annotations

from fastapi import Depends

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageData,
    MessageResponse,
    SuccessResponse,
)

from app.context.task.application.commands.add_checklist import (
    AddChecklistCommand,
    AddChecklistHandler,
)
from app.context.task.application.commands.remove_checklist import (
    RemoveChecklistCommand,
    RemoveChecklistHandler,
)
from app.context.task.application.commands.add_checklist_item import (
    AddChecklistItemCommand,
    AddChecklistItemHandler,
)
from app.context.task.application.commands.toggle_checklist_item import (
    ToggleChecklistItemCommand,
    ToggleChecklistItemHandler,
)
from app.context.task.application.commands.assign_checklist_item import (
    AssignChecklistItemCommand,
    AssignChecklistItemHandler,
)
from app.context.task.presentation.dependencies import (
    get_current_user_id,
    get_task_event_bus,
    get_task_permission_checker,
    get_task_repository,
)
from app.context.task.presentation.schemas.requests.add_checklist_request import AddChecklistRequest
from app.context.task.presentation.schemas.requests.add_checklist_item_request import AddChecklistItemRequest
from app.context.task.presentation.schemas.requests.assign_checklist_item_request import AssignChecklistItemRequest
from app.context.task.presentation.schemas.responses.task_response import ChecklistResponse


class TaskChecklistController(BaseController):
    """
    Контроллер чек-листов задачи.

    Endpoint'ы:
        POST   /{task_id}/checklists                                — Добавить чек-лист
        DELETE /{task_id}/checklists/{checklist_id}                 — Удалить чек-лист
        POST   /{task_id}/checklists/{checklist_id}/items           — Добавить пункт
        POST   /{task_id}/checklists/{checklist_id}/items/{item_id}/toggle — Переключить пункт
        POST   /{task_id}/checklists/{checklist_id}/items/{item_id}/assign  — Назначить пункт
    """

    def __init__(self) -> None:
        super().__init__(prefix="/tasks", tags=["Task / Checklists"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/{task_id}/checklists",
            self.add_checklist,
            methods=["POST"],
            response_model=SuccessResponse[ChecklistResponse],
            status_code=201,
            summary="Добавить чек-лист",
            description="Добавляет чек-лист к задаче.",
            responses={
                201: {"description": "Чек-лист добавлен"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача не найдена", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/checklists/{checklist_id}",
            self.remove_checklist,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить чек-лист",
            description="Удаляет чек-лист из задачи.",
            responses={
                200: {"description": "Чек-лист удалён"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача или чек-лист не найдены", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/checklists/{checklist_id}/items",
            self.add_checklist_item,
            methods=["POST"],
            response_model=SuccessResponse[dict],
            status_code=201,
            summary="Добавить пункт чек-листа",
            description="Добавляет пункт в чек-лист задачи.",
            responses={
                201: {"description": "Пункт добавлен"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача или чек-лист не найдены", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/checklists/{checklist_id}/items/{item_id}/toggle",
            self.toggle_checklist_item,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Переключить пункт чек-листа",
            description="Переключает состояние пункта чек-листа (checked/unchecked).",
            responses={
                200: {"description": "Пункт переключён"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача, чек-лист или пункт не найдены", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{task_id}/checklists/{checklist_id}/items/{item_id}/assign",
            self.assign_checklist_item,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Назначить исполнителя пункта",
            description="Назначает исполнителя на пункт чек-листа.",
            responses={
                200: {"description": "Исполнитель назначен"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Задача, чек-лист или пункт не найдены", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )

    async def add_checklist(
        self,
        task_id: str,
        body: AddChecklistRequest,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> SuccessResponse[ChecklistResponse]:
        """Добавить чек-лист."""
        handler = AddChecklistHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = AddChecklistCommand(
            caller_id=caller_id,
            task_id=task_id,
            title=body.title,
        )
        checklist_id = await handler.handle(command)
        return SuccessResponse(data=ChecklistResponse(id=checklist_id, title=body.title, items=[]))

    async def remove_checklist(
        self,
        task_id: str,
        checklist_id: str,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Удалить чек-лист."""
        handler = RemoveChecklistHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = RemoveChecklistCommand(
            caller_id=caller_id,
            task_id=task_id,
            checklist_id=checklist_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Чек-лист удалён"))

    async def add_checklist_item(
        self,
        task_id: str,
        checklist_id: str,
        body: AddChecklistItemRequest,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> SuccessResponse[dict]:
        """Добавить пункт чек-листа."""
        handler = AddChecklistItemHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = AddChecklistItemCommand(
            caller_id=caller_id,
            task_id=task_id,
            checklist_id=checklist_id,
            text=body.text,
            assignee_id=body.assignee_id,
            due_date=body.due_date,
        )
        item_id = await handler.handle(command)
        return SuccessResponse(data={"id": item_id})

    async def toggle_checklist_item(
        self,
        task_id: str,
        checklist_id: str,
        item_id: str,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Переключить пункт чек-листа."""
        handler = ToggleChecklistItemHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = ToggleChecklistItemCommand(
            caller_id=caller_id,
            task_id=task_id,
            checklist_id=checklist_id,
            item_id=item_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Пункт чек-листа переключён"))

    async def assign_checklist_item(
        self,
        task_id: str,
        checklist_id: str,
        item_id: str,
        body: AssignChecklistItemRequest,
        caller_id: str = Depends(get_current_user_id),
        task_repo=Depends(get_task_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Назначить исполнителя пункта чек-листа."""
        handler = AssignChecklistItemHandler(
            task_repo=task_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = AssignChecklistItemCommand(
            caller_id=caller_id,
            task_id=task_id,
            checklist_id=checklist_id,
            item_id=item_id,
            assignee_id=body.assignee_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Исполнитель пункта назначен"))
