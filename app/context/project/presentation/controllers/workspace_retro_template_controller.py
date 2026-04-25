from __future__ import annotations

from fastapi import Depends

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import ErrorResponse, MessageResponse, SuccessResponse

from app.context.project.application.commands.create_retro_template import (
    CreateRetroTemplateCommand,
    CreateRetroTemplateHandler,
)
from app.context.project.application.commands.update_retro_template import (
    UpdateRetroTemplateCommand,
    UpdateRetroTemplateHandler,
)
from app.context.project.application.commands.delete_retro_template import (
    DeleteRetroTemplateCommand,
    DeleteRetroTemplateHandler,
)
from app.context.project.application.queries.get_retro_templates import (
    GetRetroTemplatesHandler,
    GetRetroTemplatesQuery,
)
from app.context.project.presentation.dependencies import (
    get_current_user_id,
    get_project_event_bus,
    get_project_ws_permission_checker_port,
    get_retro_template_repository,
)
from app.context.project.presentation.schemas.requests.create_retro_template_request import (
    CreateRetroTemplateRequest,
)
from app.context.project.presentation.schemas.requests.update_retro_template_request import (
    UpdateRetroTemplateRequest,
)
from app.context.project.presentation.schemas.responses.retro_template_response import (
    RetroTemplateResponse,
)


class WorkspaceRetroTemplateController(BaseController):
    """
    Контроллер кастомных шаблонов ретроспектив workspace.

    Привязан к workspace — создание, обновление и удаление
    кастомных шаблонов требует workspace-разрешения.

    Endpoint'ы:
        GET    /workspaces/{ws_id}/retro-templates                    — Список шаблонов workspace
        POST   /workspaces/{ws_id}/retro-templates                    — Создать шаблон
        PATCH  /workspaces/{ws_id}/retro-templates/{template_id}      — Обновить шаблон
        DELETE /workspaces/{ws_id}/retro-templates/{template_id}      — Удалить шаблон
    """

    def __init__(self) -> None:
        super().__init__(prefix="/workspaces/{ws_id}/retro-templates", tags=["Project / Workspace Retro Templates"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/", self.list_workspace_templates, methods=["GET"],
            response_model=SuccessResponse[list[RetroTemplateResponse]],
            summary="Шаблоны ретроспектив workspace",
        )
        self._router.add_api_route(
            "/", self.create_template, methods=["POST"],
            response_model=SuccessResponse[RetroTemplateResponse], status_code=201,
            summary="Создать кастомный шаблон ретроспективы",
        )
        self._router.add_api_route(
            "/{template_id}", self.update_template, methods=["PATCH"],
            response_model=MessageResponse, summary="Обновить шаблон ретроспективы",
        )
        self._router.add_api_route(
            "/{template_id}", self.delete_template, methods=["DELETE"],
            response_model=MessageResponse, summary="Удалить шаблон ретроспективы",
        )

    async def list_workspace_templates(
        self, ws_id: str,
        retro_template_repo=Depends(get_retro_template_repository),
    ) -> SuccessResponse[list[RetroTemplateResponse]]:
        handler = GetRetroTemplatesHandler(retro_template_repo=retro_template_repo)
        query = GetRetroTemplatesQuery()
        dto = await handler.handle(query)
        items = [RetroTemplateResponse.model_validate(t.__dict__) for t in dto.items]
        return SuccessResponse(data=items)

    async def create_template(
        self, ws_id: str, body: CreateRetroTemplateRequest,
        caller_id: str = Depends(get_current_user_id),
        retro_template_repo=Depends(get_retro_template_repository),
        ws_permission_checker=Depends(get_project_ws_permission_checker_port),
        event_bus=Depends(get_project_event_bus),
    ) -> SuccessResponse[RetroTemplateResponse]:
        handler = CreateRetroTemplateHandler(
            retro_template_repo=retro_template_repo,
            workspace_permission_checker=ws_permission_checker,
            event_bus=event_bus,
        )
        sections = [{"title": s.title, "prompt": s.prompt, "item_type": s.item_type} for s in body.sections]
        command = CreateRetroTemplateCommand(
            caller_id=caller_id, workspace_id=ws_id,
            name=body.name, sections=sections,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=RetroTemplateResponse.model_validate(dto.__dict__))

    async def update_template(
        self, ws_id: str, template_id: str, body: UpdateRetroTemplateRequest,
        caller_id: str = Depends(get_current_user_id),
        retro_template_repo=Depends(get_retro_template_repository),
        ws_permission_checker=Depends(get_project_ws_permission_checker_port),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = UpdateRetroTemplateHandler(
            retro_template_repo=retro_template_repo,
            workspace_permission_checker=ws_permission_checker,
            event_bus=event_bus,
        )
        sections = None
        if body.sections is not None:
            sections = [{"title": s.title, "prompt": s.prompt, "item_type": s.item_type} for s in body.sections]
        command = UpdateRetroTemplateCommand(
            caller_id=caller_id, workspace_id=ws_id,
            template_id=template_id, sections=sections,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Шаблон ретроспективы обновлён"})

    async def delete_template(
        self, ws_id: str, template_id: str,
        caller_id: str = Depends(get_current_user_id),
        retro_template_repo=Depends(get_retro_template_repository),
        ws_permission_checker=Depends(get_project_ws_permission_checker_port),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = DeleteRetroTemplateHandler(
            retro_template_repo=retro_template_repo,
            workspace_permission_checker=ws_permission_checker,
            event_bus=event_bus,
        )
        await handler.handle(DeleteRetroTemplateCommand(
            caller_id=caller_id, workspace_id=ws_id, template_id=template_id,
        ))
        return SuccessResponse(data={"message": "Шаблон ретроспективы удалён"})
