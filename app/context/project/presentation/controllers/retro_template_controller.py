from __future__ import annotations

from fastapi import Depends

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import SuccessResponse

from app.context.project.application.queries.get_retro_templates import (
    GetRetroTemplatesHandler,
    GetRetroTemplatesQuery,
)
from app.context.project.presentation.dependencies import (
    get_retro_template_repository,
)
from app.context.project.presentation.schemas.responses.retro_template_response import (
    RetroTemplateResponse,
)


class RetroTemplateController(BaseController):
    """
    Контроллер системных шаблонов ретроспектив.

    Доступен без привязки к workspace — возвращает только системные шаблоны.

    Endpoint'ы:
        GET /retro-templates — Список системных шаблонов ретроспектив
    """

    def __init__(self) -> None:
        super().__init__(prefix="/retro-templates", tags=["Project / Retro Templates"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/", self.list_system_templates, methods=["GET"],
            response_model=SuccessResponse[list[RetroTemplateResponse]],
            summary="Системные шаблоны ретроспектив",
            description="Возвращает список системных (предустановленных) шаблонов ретроспектив.",
        )

    async def list_system_templates(
        self,
        retro_template_repo=Depends(get_retro_template_repository),
    ) -> SuccessResponse[list[RetroTemplateResponse]]:
        handler = GetRetroTemplatesHandler(retro_template_repo=retro_template_repo)
        query = GetRetroTemplatesQuery()
        dto = await handler.handle(query)
        items = [RetroTemplateResponse.model_validate(t.__dict__) for t in dto.items]
        return SuccessResponse(data=items)
