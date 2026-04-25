from __future__ import annotations

from fastapi import Depends

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import ErrorResponse, MessageResponse, SuccessResponse

from app.context.project.application.commands.create_epic import (
    CreateEpicCommand,
    CreateEpicHandler,
)
from app.context.project.application.commands.update_epic import (
    UpdateEpicCommand,
    UpdateEpicHandler,
)
from app.context.project.application.commands.change_epic_status import (
    ChangeEpicStatusCommand,
    ChangeEpicStatusHandler,
)
from app.context.project.application.queries.get_epics_by_project import (
    GetEpicsByProjectHandler,
    GetEpicsByProjectQuery,
)
from app.context.project.application.queries.get_epic import (
    GetEpicHandler,
    GetEpicQuery,
)
from app.context.project.presentation.dependencies import (
    get_current_user_id,
    get_epic_repository,
    get_project_event_bus,
    get_project_permission_checker,
    get_project_repository,
)
from app.context.project.presentation.schemas.requests.create_epic_request import (
    CreateEpicRequest,
)
from app.context.project.presentation.schemas.requests.update_epic_request import (
    UpdateEpicRequest,
)
from app.context.project.presentation.schemas.requests.change_epic_status_request import (
    ChangeEpicStatusRequest,
)
from app.context.project.presentation.schemas.responses.epic_response import (
    EpicResponse,
)


class EpicController(BaseController):
    """
    Контроллер эпиков.

    Endpoint'ы:
        GET    /{project_id}/epics                           — Список эпиков
        GET    /{project_id}/epics/{epic_id}                 — Получить эпик
        POST   /{project_id}/epics                           — Создать эпик
        PATCH  /{project_id}/epics/{epic_id}                 — Обновить эпик
        POST   /{project_id}/epics/{epic_id}/change-status   — Изменить статус
    """

    def __init__(self) -> None:
        super().__init__(prefix="/workspaces/{ws_id}/projects", tags=["Project / Epics"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/{project_id}/epics", self.list_epics, methods=["GET"],
            response_model=SuccessResponse[list[EpicResponse]],
            summary="Список эпиков проекта",
        )
        self._router.add_api_route(
            "/{project_id}/epics/{epic_id}", self.get_epic, methods=["GET"],
            response_model=SuccessResponse[EpicResponse],
            summary="Получить эпик",
            responses={404: {"model": ErrorResponse}},
        )
        self._router.add_api_route(
            "/{project_id}/epics", self.create_epic, methods=["POST"],
            response_model=SuccessResponse[EpicResponse], status_code=201,
            summary="Создать эпик",
        )
        self._router.add_api_route(
            "/{project_id}/epics/{epic_id}", self.update_epic, methods=["PATCH"],
            response_model=MessageResponse, summary="Обновить эпик",
        )
        self._router.add_api_route(
            "/{project_id}/epics/{epic_id}/change-status", self.change_epic_status, methods=["POST"],
            response_model=MessageResponse, summary="Изменить статус эпика",
        )

    async def list_epics(
        self, ws_id: str, project_id: str,
        caller_id: str = Depends(get_current_user_id),
        epic_repo=Depends(get_epic_repository),
        permission_checker=Depends(get_project_permission_checker),
    ) -> SuccessResponse[list[EpicResponse]]:
        handler = GetEpicsByProjectHandler(epic_repo=epic_repo, permission_checker=permission_checker)
        query = GetEpicsByProjectQuery(caller_id=caller_id, project_id=project_id)
        dto = await handler.handle(query)
        items = [EpicResponse.model_validate(e.__dict__) for e in dto.items]
        return SuccessResponse(data=items)

    async def get_epic(
        self, ws_id: str, project_id: str, epic_id: str,
        caller_id: str = Depends(get_current_user_id),
        epic_repo=Depends(get_epic_repository),
        permission_checker=Depends(get_project_permission_checker),
    ) -> SuccessResponse[EpicResponse]:
        handler = GetEpicHandler(epic_repo=epic_repo, permission_checker=permission_checker)
        query = GetEpicQuery(caller_id=caller_id, epic_id=epic_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=EpicResponse.model_validate(dto.__dict__))

    async def create_epic(
        self, ws_id: str, project_id: str, body: CreateEpicRequest,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        epic_repo=Depends(get_epic_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> SuccessResponse[EpicResponse]:
        handler = CreateEpicHandler(
            project_repo=project_repo, epic_repo=epic_repo,
            permission_checker=permission_checker, event_bus=event_bus,
        )
        command = CreateEpicCommand(
            caller_id=caller_id, project_id=project_id,
            name=body.name, owner_id=body.owner_id,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=EpicResponse.model_validate(dto.__dict__))

    async def update_epic(
        self, ws_id: str, project_id: str, epic_id: str, body: UpdateEpicRequest,
        caller_id: str = Depends(get_current_user_id),
        epic_repo=Depends(get_epic_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = UpdateEpicHandler(
            epic_repo=epic_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        command = UpdateEpicCommand(
            epic_id=epic_id, caller_id=caller_id,
            name=body.name,
            description_content=body.description.content if body.description else None,
            description_format=body.description.format if body.description else None,
            owner_id=body.owner_id, color=body.color,
            start_date=body.start_date, due_date=body.due_date,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Эпик обновлён"})

    async def change_epic_status(
        self, ws_id: str, project_id: str, epic_id: str, body: ChangeEpicStatusRequest,
        caller_id: str = Depends(get_current_user_id),
        epic_repo=Depends(get_epic_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = ChangeEpicStatusHandler(
            epic_repo=epic_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(ChangeEpicStatusCommand(
            caller_id=caller_id, epic_id=epic_id, new_status=body.new_status,
        ))
        return SuccessResponse(data={"message": "Статус эпика изменён"})
