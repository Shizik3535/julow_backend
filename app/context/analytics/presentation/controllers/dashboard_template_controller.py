from __future__ import annotations

from fastapi import Depends

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageData,
    MessageResponse,
    SuccessResponse,
)

from app.context.analytics.application.commands.create_custom_template import (
    CreateCustomTemplateCommand,
    CreateCustomTemplateHandler,
)
from app.context.analytics.application.commands.delete_template import DeleteTemplateCommand, DeleteTemplateHandler
from app.context.analytics.application.dto.dashboard_template_dto import CustomTemplateWidgetDTO
from app.context.analytics.application.queries.list_dashboard_templates import (
    ListDashboardTemplatesHandler,
    ListDashboardTemplatesQuery,
)

from app.context.analytics.presentation.dependencies import (
    get_analytics_permission_checker,
    get_current_user_id,
    get_dashboard_template_repository,
)
from app.context.analytics.presentation.schemas.requests.analytics_requests import (
    CreateCustomTemplateRequest,
)
from app.context.analytics.presentation.schemas.requests.query_mapper import query_request_to_dto
from app.context.analytics.presentation.schemas.responses.analytics_responses import (
    DashboardTemplateResponse,
)


class DashboardTemplateController(BaseController):
    """
    Контроллер шаблонов дашбордов.

    Endpoint'ы:
        GET    /                           — Список шаблонов (системные + workspace)
        POST   /                           — Создать пользовательский шаблон
        DELETE /{template_id}              — Удалить пользовательский шаблон
    """

    def __init__(self) -> None:
        super().__init__(prefix="/dashboard-templates", tags=["Analytics — Templates"])

    def _register_routes(self) -> None:
        std = {
            401: {"description": "Не аутентифицирован", "model": ErrorResponse},
            403: {"description": "Недостаточно прав", "model": ErrorResponse},
        }
        self._router.add_api_route(
            "",
            self.list_templates,
            methods=["GET"],
            response_model=SuccessResponse[list[DashboardTemplateResponse]],
            summary="Список шаблонов дашбордов",
            description="Возвращает системные шаблоны + шаблоны workspace (если указан workspace_id).",
            responses={200: {"description": "Список шаблонов"}, **std},
        )
        self._router.add_api_route(
            "",
            self.create_custom_template,
            methods=["POST"],
            response_model=SuccessResponse[DashboardTemplateResponse],
            status_code=201,
            summary="Создать пользовательский шаблон",
            description="Создаёт пользовательский шаблон дашборда (is_system=False).",
            responses={
                201: {"description": "Шаблон создан"},
                **std,
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{template_id}",
            self.delete_template,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить шаблон",
            description="Удаляет пользовательский шаблон. Системные удалить нельзя.",
            responses={
                200: {"description": "Шаблон удалён"},
                **std,
                404: {"description": "Шаблон не найден", "model": ErrorResponse},
                409: {"description": "Нельзя удалить системный шаблон", "model": ErrorResponse},
            },
        )

    async def list_templates(
        self,
        workspace_id: str | None = None,
        caller_id: str = Depends(get_current_user_id),
        template_repo=Depends(get_dashboard_template_repository),
    ) -> SuccessResponse[list[DashboardTemplateResponse]]:
        handler = ListDashboardTemplatesHandler(template_repo=template_repo)
        query = ListDashboardTemplatesQuery(
            caller_id=caller_id,
            workspace_id=workspace_id,
        )
        dto = await handler.handle(query)
        items = [DashboardTemplateResponse.model_validate(t.model_dump()) for t in dto.items]
        return SuccessResponse(data=items)

    async def create_custom_template(
        self,
        body: CreateCustomTemplateRequest,
        caller_id: str = Depends(get_current_user_id),
        template_repo=Depends(get_dashboard_template_repository),
        permission_checker=Depends(get_analytics_permission_checker),
    ) -> SuccessResponse[DashboardTemplateResponse]:
        widgets = [
            CustomTemplateWidgetDTO(
                widget_type=w.widget_type.value,
                query=query_request_to_dto(w.query),
                display_params=w.display_params,
            )
            for w in body.widgets
        ]

        handler = CreateCustomTemplateHandler(
            template_repo=template_repo,
            permission_checker=permission_checker,
        )
        command = CreateCustomTemplateCommand(
            caller_id=caller_id,
            workspace_id=body.workspace_id,
            name=body.name,
            description=body.description,
            widgets=widgets,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=DashboardTemplateResponse.model_validate(dto.model_dump()))

    async def delete_template(
        self,
        template_id: str,
        workspace_id: str,
        caller_id: str = Depends(get_current_user_id),
        template_repo=Depends(get_dashboard_template_repository),
        permission_checker=Depends(get_analytics_permission_checker),
    ) -> MessageResponse:
        handler = DeleteTemplateHandler(
            template_repo=template_repo,
            permission_checker=permission_checker,
        )
        command = DeleteTemplateCommand(
            caller_id=caller_id,
            workspace_id=workspace_id,
            template_id=template_id,
        )
        await handler.handle(command)
        return MessageResponse(data=MessageData(message="Шаблон удалён"))
