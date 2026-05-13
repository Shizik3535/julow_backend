from __future__ import annotations

from fastapi import Depends

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageData,
    MessageResponse,
    SuccessResponse,
)

from app.context.timetracking.application.commands.create_time_entry_tag import (
    CreateTimeEntryTagCommand,
    CreateTimeEntryTagHandler,
)
from app.context.timetracking.application.commands.delete_time_entry_tag import (
    DeleteTimeEntryTagCommand,
    DeleteTimeEntryTagHandler,
)
from app.context.timetracking.application.commands.update_time_entry_tag import (
    UpdateTimeEntryTagCommand,
    UpdateTimeEntryTagHandler,
)
from app.context.timetracking.application.queries.get_time_entry_tags import (
    GetTimeEntryTagsHandler,
    GetTimeEntryTagsQuery,
)
from app.context.timetracking.presentation.dependencies import (
    get_current_user_id,
    get_time_entry_tag_repository,
    get_timetracking_event_bus,
    get_timetracking_permission_checker,
    get_timetracking_workspace_port,
)
from app.context.timetracking.presentation.schemas.requests.tag_requests import (
    CreateTimeEntryTagRequest,
    UpdateTimeEntryTagRequest,
)
from app.context.timetracking.presentation.schemas.responses.time_entry_tag_response import (
    TimeEntryTagResponse,
)


class TimeEntryTagController(BaseController):
    """
    Контроллер тегов записей времени.

    Endpoint'ы:
        GET    /workspaces/{ws_id}/time/tags        — Список тегов
        POST   /workspaces/{ws_id}/time/tags        — Создать тег (admin)
        PATCH  /time/tags/{tag_id}                  — Обновить тег (admin)
        DELETE /time/tags/{tag_id}                  — Удалить тег (admin)
    """

    def __init__(self) -> None:
        super().__init__(prefix="", tags=["TimeTracking — Tags"])

    def _register_routes(self) -> None:
        std = {
            401: {"description": "Не аутентифицирован", "model": ErrorResponse},
            403: {"description": "Недостаточно прав", "model": ErrorResponse},
        }
        self._router.add_api_route(
            "/workspaces/{workspace_id}/time/tags", self.list_, methods=["GET"],
            response_model=SuccessResponse[list[TimeEntryTagResponse]],
            summary="Список тегов записей времени", responses={200: {}, **std},
        )
        self._router.add_api_route(
            "/workspaces/{workspace_id}/time/tags", self.create, methods=["POST"],
            response_model=SuccessResponse[TimeEntryTagResponse], status_code=201,
            summary="Создать тег",
            responses={201: {"description": "Создано"},
                       409: {"description": "Тег с таким именем уже существует",
                             "model": ErrorResponse}, **std},
        )
        self._router.add_api_route(
            "/time/tags/{tag_id}", self.update, methods=["PATCH"],
            response_model=SuccessResponse[TimeEntryTagResponse],
            summary="Обновить тег",
            responses={200: {}, 404: {"model": ErrorResponse}, **std},
        )
        self._router.add_api_route(
            "/time/tags/{tag_id}", self.delete, methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить тег",
            responses={200: {"description": "Удалено"}, 404: {"model": ErrorResponse}, **std},
        )

    async def list_(
        self,
        workspace_id: str,
        caller_id: str = Depends(get_current_user_id),
        tag_repo=Depends(get_time_entry_tag_repository),
        permission_checker=Depends(get_timetracking_permission_checker),
    ) -> SuccessResponse[list[TimeEntryTagResponse]]:
        handler = GetTimeEntryTagsHandler(
            tag_repo=tag_repo,
            permission_checker=permission_checker,
        )
        dto = await handler.handle(GetTimeEntryTagsQuery(
            caller_id=caller_id, workspace_id=workspace_id,
        ))
        items = [TimeEntryTagResponse.model_validate(t.model_dump()) for t in dto.items]
        return SuccessResponse(data=items)

    async def create(
        self,
        workspace_id: str,
        body: CreateTimeEntryTagRequest,
        caller_id: str = Depends(get_current_user_id),
        tag_repo=Depends(get_time_entry_tag_repository),
        permission_checker=Depends(get_timetracking_permission_checker),
        workspace_port=Depends(get_timetracking_workspace_port),
        event_bus=Depends(get_timetracking_event_bus),
    ) -> SuccessResponse[TimeEntryTagResponse]:
        handler = CreateTimeEntryTagHandler(
            tag_repo=tag_repo,
            permission_checker=permission_checker,
            workspace_port=workspace_port,
            event_bus=event_bus,
        )
        dto = await handler.handle(CreateTimeEntryTagCommand(
            caller_id=caller_id, workspace_id=workspace_id,
            name=body.name, color=body.color,
        ))
        return SuccessResponse(data=TimeEntryTagResponse.model_validate(dto.model_dump()))

    async def update(
        self,
        tag_id: str,
        body: UpdateTimeEntryTagRequest,
        caller_id: str = Depends(get_current_user_id),
        tag_repo=Depends(get_time_entry_tag_repository),
        permission_checker=Depends(get_timetracking_permission_checker),
        event_bus=Depends(get_timetracking_event_bus),
    ) -> SuccessResponse[TimeEntryTagResponse]:
        handler = UpdateTimeEntryTagHandler(
            tag_repo=tag_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        dto = await handler.handle(UpdateTimeEntryTagCommand(
            caller_id=caller_id, tag_id=tag_id,
            name=body.name, color=body.color,
        ))
        return SuccessResponse(data=TimeEntryTagResponse.model_validate(dto.model_dump()))

    async def delete(
        self,
        tag_id: str,
        caller_id: str = Depends(get_current_user_id),
        tag_repo=Depends(get_time_entry_tag_repository),
        permission_checker=Depends(get_timetracking_permission_checker),
        event_bus=Depends(get_timetracking_event_bus),
    ) -> MessageResponse:
        handler = DeleteTimeEntryTagHandler(
            tag_repo=tag_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        await handler.handle(DeleteTimeEntryTagCommand(caller_id=caller_id, tag_id=tag_id))
        return SuccessResponse(data=MessageData(message="Тег удалён"))
