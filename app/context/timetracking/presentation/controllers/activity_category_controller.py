from __future__ import annotations

from fastapi import Depends

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageData,
    MessageResponse,
    SuccessResponse,
)

from app.context.timetracking.application.commands.create_activity_category import (
    CreateActivityCategoryCommand,
    CreateActivityCategoryHandler,
)
from app.context.timetracking.application.commands.delete_activity_category import (
    DeleteActivityCategoryCommand,
    DeleteActivityCategoryHandler,
)
from app.context.timetracking.application.commands.update_activity_category import (
    UpdateActivityCategoryCommand,
    UpdateActivityCategoryHandler,
)
from app.context.timetracking.application.queries.get_activity_categories import (
    GetActivityCategoriesHandler,
    GetActivityCategoriesQuery,
)
from app.context.timetracking.presentation.dependencies import (
    get_activity_category_repository,
    get_current_user_id,
    get_time_entry_repository,
    get_timetracking_event_bus,
    get_timetracking_permission_checker,
    get_timetracking_workspace_port,
)
from app.context.timetracking.presentation.schemas.requests.category_requests import (
    CreateActivityCategoryRequest,
    UpdateActivityCategoryRequest,
)
from app.context.timetracking.presentation.schemas.responses.activity_category_response import (
    ActivityCategoryResponse,
)


class ActivityCategoryController(BaseController):
    """
    Контроллер категорий деятельности.

    Endpoint'ы:
        GET    /workspaces/{ws_id}/time/categories            — Список категорий
        POST   /workspaces/{ws_id}/time/categories            — Создать категорию (admin)
        PATCH  /time/categories/{category_id}                 — Обновить категорию (admin)
        DELETE /time/categories/{category_id}                 — Удалить категорию (admin)
    """

    def __init__(self) -> None:
        super().__init__(prefix="", tags=["TimeTracking — Categories"])

    def _register_routes(self) -> None:
        std = {
            401: {"description": "Не аутентифицирован", "model": ErrorResponse},
            403: {"description": "Недостаточно прав", "model": ErrorResponse},
        }
        self._router.add_api_route(
            "/workspaces/{workspace_id}/time/categories", self.list_, methods=["GET"],
            response_model=SuccessResponse[list[ActivityCategoryResponse]],
            summary="Список категорий деятельности", responses={200: {}, **std},
        )
        self._router.add_api_route(
            "/workspaces/{workspace_id}/time/categories", self.create, methods=["POST"],
            response_model=SuccessResponse[ActivityCategoryResponse], status_code=201,
            summary="Создать категорию",
            responses={201: {"description": "Создано"}, **std, 422: {"model": ErrorResponse}},
        )
        self._router.add_api_route(
            "/time/categories/{category_id}", self.update, methods=["PATCH"],
            response_model=SuccessResponse[ActivityCategoryResponse],
            summary="Обновить категорию",
            responses={200: {}, 404: {"model": ErrorResponse}, **std},
        )
        self._router.add_api_route(
            "/time/categories/{category_id}", self.delete, methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить категорию",
            responses={200: {"description": "Удалено"}, 404: {"model": ErrorResponse},
                       409: {"description": "Категория используется или системная",
                             "model": ErrorResponse}, **std},
        )

    async def list_(
        self,
        workspace_id: str,
        caller_id: str = Depends(get_current_user_id),
        category_repo=Depends(get_activity_category_repository),
        permission_checker=Depends(get_timetracking_permission_checker),
    ) -> SuccessResponse[list[ActivityCategoryResponse]]:
        handler = GetActivityCategoriesHandler(
            category_repo=category_repo,
            permission_checker=permission_checker,
        )
        dto = await handler.handle(GetActivityCategoriesQuery(
            caller_id=caller_id, workspace_id=workspace_id,
        ))
        items = [ActivityCategoryResponse.model_validate(c.model_dump()) for c in dto.items]
        return SuccessResponse(data=items)

    async def create(
        self,
        workspace_id: str,
        body: CreateActivityCategoryRequest,
        caller_id: str = Depends(get_current_user_id),
        category_repo=Depends(get_activity_category_repository),
        permission_checker=Depends(get_timetracking_permission_checker),
        workspace_port=Depends(get_timetracking_workspace_port),
        event_bus=Depends(get_timetracking_event_bus),
    ) -> SuccessResponse[ActivityCategoryResponse]:
        handler = CreateActivityCategoryHandler(
            category_repo=category_repo,
            permission_checker=permission_checker,
            workspace_port=workspace_port,
            event_bus=event_bus,
        )
        dto = await handler.handle(CreateActivityCategoryCommand(
            caller_id=caller_id, workspace_id=workspace_id,
            name=body.name, color=body.color, description=body.description,
        ))
        return SuccessResponse(data=ActivityCategoryResponse.model_validate(dto.model_dump()))

    async def update(
        self,
        category_id: str,
        body: UpdateActivityCategoryRequest,
        caller_id: str = Depends(get_current_user_id),
        category_repo=Depends(get_activity_category_repository),
        permission_checker=Depends(get_timetracking_permission_checker),
        event_bus=Depends(get_timetracking_event_bus),
    ) -> SuccessResponse[ActivityCategoryResponse]:
        handler = UpdateActivityCategoryHandler(
            category_repo=category_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        dto = await handler.handle(UpdateActivityCategoryCommand(
            caller_id=caller_id, category_id=category_id,
            name=body.name, color=body.color, description=body.description,
        ))
        return SuccessResponse(data=ActivityCategoryResponse.model_validate(dto.model_dump()))

    async def delete(
        self,
        category_id: str,
        caller_id: str = Depends(get_current_user_id),
        category_repo=Depends(get_activity_category_repository),
        time_entry_repo=Depends(get_time_entry_repository),
        permission_checker=Depends(get_timetracking_permission_checker),
        event_bus=Depends(get_timetracking_event_bus),
    ) -> MessageResponse:
        handler = DeleteActivityCategoryHandler(
            category_repo=category_repo,
            time_entry_repo=time_entry_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        await handler.handle(DeleteActivityCategoryCommand(
            caller_id=caller_id, category_id=category_id,
        ))
        return SuccessResponse(data=MessageData(message="Категория удалена"))
