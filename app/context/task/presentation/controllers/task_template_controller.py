from __future__ import annotations

from fastapi import Depends, Query

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    PaginatedResponse,
    SuccessResponse,
)

from app.context.task.application.queries.get_task_templates import (
    GetTaskTemplatesHandler,
    GetTaskTemplatesQuery,
)
from app.context.task.application.queries.get_task_template import (
    GetTaskTemplateHandler,
    GetTaskTemplateQuery,
)
from app.context.task.presentation.dependencies import (
    get_current_user_id,
    get_task_template_repository,
    get_task_permission_checker,
)
from app.context.task.presentation.schemas.responses.task_template_response import TaskTemplateResponse


class TaskTemplateController(BaseController):
    """
    Контроллер системных шаблонов задач.

    Endpoint'ы:
        GET /        — Список системных шаблонов
        GET /{template_id} — Получить шаблон
    """

    def __init__(self) -> None:
        super().__init__(prefix="/task-templates", tags=["Task / Templates"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/",
            self.list_templates,
            methods=["GET"],
            response_model=PaginatedResponse[TaskTemplateResponse],
            summary="Список системных шаблонов",
            description="Возвращает системные шаблоны задач.",
            responses={
                200: {"description": "Список шаблонов"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{template_id}",
            self.get_template,
            methods=["GET"],
            response_model=SuccessResponse[TaskTemplateResponse],
            summary="Получить шаблон задачи",
            description="Возвращает данные шаблона задачи по UUID.",
            responses={
                200: {"description": "Данные шаблона"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Шаблон не найден", "model": ErrorResponse},
            },
        )

    async def list_templates(
        self,
        offset: int = Query(default=0, ge=0, description="Смещение пагинации"),
        limit: int = Query(default=100, ge=1, le=500, description="Размер страницы"),
        caller_id: str = Depends(get_current_user_id),
        template_repo=Depends(get_task_template_repository),
    ) -> PaginatedResponse[TaskTemplateResponse]:
        """Список системных шаблонов."""
        handler = GetTaskTemplatesHandler(
            template_repo=template_repo,
        )
        query = GetTaskTemplatesQuery()
        dto = await handler.handle(query)
        items = [TaskTemplateResponse.model_validate(item.model_dump()) for item in dto.items]
        return PaginatedResponse(items=items, total=dto.total, page=1, page_size=dto.total)

    async def get_template(
        self,
        template_id: str,
        caller_id: str = Depends(get_current_user_id),
        template_repo=Depends(get_task_template_repository),
        permission_checker=Depends(get_task_permission_checker),
    ) -> SuccessResponse[TaskTemplateResponse]:
        """Получить шаблон по ID."""
        handler = GetTaskTemplateHandler(
            template_repo=template_repo,
            permission_checker=permission_checker,
        )
        query = GetTaskTemplateQuery(caller_id=caller_id, template_id=template_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=TaskTemplateResponse.model_validate(dto.model_dump()))
