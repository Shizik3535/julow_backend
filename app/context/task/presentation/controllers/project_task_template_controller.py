from __future__ import annotations

from fastapi import Depends

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageData,
    MessageResponse,
    PaginatedResponse,
    SuccessResponse,
)

from app.context.task.application.commands.create_task_template import (
    CreateTaskTemplateCommand,
    CreateTaskTemplateHandler,
)
from app.context.task.application.commands.update_task_template import (
    UpdateTaskTemplateCommand,
    UpdateTaskTemplateHandler,
)
from app.context.task.application.commands.delete_task_template import (
    DeleteTaskTemplateCommand,
    DeleteTaskTemplateHandler,
)
from app.context.task.application.queries.get_task_templates_by_project import (
    GetTaskTemplatesByProjectHandler,
    GetTaskTemplatesByProjectQuery,
)
from app.context.task.presentation.dependencies import (
    get_current_user_id,
    get_task_event_bus,
    get_task_permission_checker,
    get_task_template_repository,
)
from app.context.task.presentation.schemas.requests.create_task_template_request import CreateTaskTemplateRequest
from app.context.task.presentation.schemas.requests.update_task_template_request import UpdateTaskTemplateRequest
from app.context.task.presentation.schemas.responses.task_template_response import TaskTemplateResponse


class ProjectTaskTemplateController(BaseController):
    """
    Контроллер шаблонов задач проекта.

    Endpoint'ы:
        GET    /{project_id}/task-templates                        — Список шаблонов проекта
        POST   /{project_id}/task-templates                        — Создать шаблон
        PATCH  /{project_id}/task-templates/{template_id}          — Обновить шаблон
        DELETE /{project_id}/task-templates/{template_id}          — Удалить шаблон
    """

    def __init__(self) -> None:
        super().__init__(prefix="/workspaces/{ws_id}/projects", tags=["Task / Project Templates"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/{project_id}/task-templates",
            self.list_templates,
            methods=["GET"],
            response_model=PaginatedResponse[TaskTemplateResponse],
            summary="Список шаблонов проекта",
            description="Возвращает шаблоны задач, доступные в проекте.",
            responses={
                200: {"description": "Список шаблонов"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{project_id}/task-templates",
            self.create_template,
            methods=["POST"],
            response_model=SuccessResponse[TaskTemplateResponse],
            status_code=201,
            summary="Создать шаблон задачи",
            description="Создаёт пользовательский шаблон задачи в проекте.",
            responses={
                201: {"description": "Шаблон создан"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                409: {"description": "Шаблон с таким именем уже существует", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{project_id}/task-templates/{template_id}",
            self.update_template,
            methods=["PATCH"],
            response_model=MessageResponse,
            summary="Обновить шаблон задачи",
            description="Обновляет шаблон задачи (метки, чек-листы, кастомные поля).",
            responses={
                200: {"description": "Шаблон обновлён"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Шаблон не найден", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{project_id}/task-templates/{template_id}",
            self.delete_template,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить шаблон задачи",
            description="Удаляет пользовательский шаблон задачи.",
            responses={
                200: {"description": "Шаблон удалён"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Шаблон не найден", "model": ErrorResponse},
                409: {"description": "Нельзя удалить системный шаблон", "model": ErrorResponse},
            },
        )

    async def list_templates(
        self,
        ws_id: str,
        project_id: str,
        caller_id: str = Depends(get_current_user_id),
        template_repo=Depends(get_task_template_repository),
        permission_checker=Depends(get_task_permission_checker),
    ) -> PaginatedResponse[TaskTemplateResponse]:
        """Список шаблонов проекта."""
        handler = GetTaskTemplatesByProjectHandler(
            template_repo=template_repo,
            permission_checker=permission_checker,
        )
        query = GetTaskTemplatesByProjectQuery(
            caller_id=caller_id,
            project_id=project_id,
        )
        dto = await handler.handle(query)
        items = [TaskTemplateResponse.model_validate(item.model_dump()) for item in dto.items]
        return PaginatedResponse(items=items, total=dto.total, page=1, page_size=dto.total)

    async def create_template(
        self,
        ws_id: str,
        project_id: str,
        body: CreateTaskTemplateRequest,
        caller_id: str = Depends(get_current_user_id),
        template_repo=Depends(get_task_template_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> SuccessResponse[TaskTemplateResponse]:
        """Создать шаблон задачи."""
        handler = CreateTaskTemplateHandler(
            template_repo=template_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = CreateTaskTemplateCommand(
            caller_id=caller_id,
            project_id=project_id,
            name=body.name,
            task_type=body.task_type,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=TaskTemplateResponse.model_validate(dto.model_dump()))

    async def update_template(
        self,
        ws_id: str,
        project_id: str,
        template_id: str,
        body: UpdateTaskTemplateRequest,
        caller_id: str = Depends(get_current_user_id),
        template_repo=Depends(get_task_template_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Обновить шаблон задачи."""
        handler = UpdateTaskTemplateHandler(
            template_repo=template_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = UpdateTaskTemplateCommand(
            caller_id=caller_id,
            template_id=template_id,
            default_labels=body.default_labels,
            default_checklists=body.default_checklists,
            default_custom_fields=body.default_custom_fields,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Шаблон обновлён"))

    async def delete_template(
        self,
        ws_id: str,
        project_id: str,
        template_id: str,
        caller_id: str = Depends(get_current_user_id),
        template_repo=Depends(get_task_template_repository),
        permission_checker=Depends(get_task_permission_checker),
        event_bus=Depends(get_task_event_bus),
    ) -> MessageResponse:
        """Удалить шаблон задачи."""
        handler = DeleteTaskTemplateHandler(
            template_repo=template_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = DeleteTaskTemplateCommand(
            caller_id=caller_id,
            template_id=template_id,
        )
        await handler.handle(command)
        return SuccessResponse(data=MessageData(message="Шаблон удалён"))
