from __future__ import annotations

from fastapi import Depends

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import ErrorResponse, MessageResponse, SuccessResponse

from app.context.project.application.commands.create_sprint import (
    CreateSprintCommand,
    CreateSprintHandler,
)
from app.context.project.application.commands.start_sprint import (
    StartSprintCommand,
    StartSprintHandler,
)
from app.context.project.application.commands.update_sprint_goal import (
    UpdateSprintGoalCommand,
    UpdateSprintGoalHandler,
)
from app.context.project.application.commands.update_sprint_date_range import (
    UpdateSprintDateRangeCommand,
    UpdateSprintDateRangeHandler,
)
from app.context.project.application.commands.create_sprint_retro import (
    CreateSprintRetroCommand,
    CreateSprintRetroHandler,
)
from app.context.project.application.queries.get_sprints_by_project import (
    GetSprintsByProjectHandler,
    GetSprintsByProjectQuery,
)
from app.context.project.application.queries.get_sprint import (
    GetSprintHandler,
    GetSprintQuery,
)
from app.context.project.application.queries.get_active_sprint import (
    GetActiveSprintHandler,
    GetActiveSprintQuery,
)
from app.context.project.presentation.dependencies import (
    get_current_user_id,
    get_project_event_bus,
    get_project_permission_checker,
    get_project_repository,
    get_retro_template_repository,
    get_sprint_repository,
)
from app.context.project.presentation.schemas.requests.create_sprint_request import (
    CreateSprintRequest,
)
from app.context.project.presentation.schemas.requests.update_sprint_goal_request import (
    UpdateSprintGoalRequest,
)
from app.context.project.presentation.schemas.requests.update_sprint_date_range_request import (
    UpdateSprintDateRangeRequest,
)
from app.context.project.presentation.schemas.requests.create_sprint_retro_request import (
    CreateSprintRetroRequest,
)
from app.context.project.presentation.schemas.responses.sprint_response import (
    SprintResponse,
)


class SprintController(BaseController):
    """
    Контроллер спринтов.

    Endpoint'ы:
        GET    /{project_id}/sprints                        — Список спринтов
        GET    /{project_id}/sprints/active                  — Активный спринт
        GET    /{project_id}/sprints/{sprint_id}             — Получить спринт
        POST   /{project_id}/sprints                         — Создать спринт
        POST   /{project_id}/sprints/{sprint_id}/start       — Запустить спринт
        PATCH  /{project_id}/sprints/{sprint_id}/goal        — Обновить цель
        PATCH  /{project_id}/sprints/{sprint_id}/date-range  — Обновить даты
        POST   /{project_id}/sprints/{sprint_id}/retro       — Создать ретроспективу
    """

    def __init__(self) -> None:
        super().__init__(prefix="/workspaces/{ws_id}/projects", tags=["Project / Sprints"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/{project_id}/sprints", self.list_sprints, methods=["GET"],
            response_model=SuccessResponse[list[SprintResponse]],
            summary="Список спринтов проекта",
        )
        self._router.add_api_route(
            "/{project_id}/sprints/active", self.get_active_sprint, methods=["GET"],
            response_model=SuccessResponse[SprintResponse],
            summary="Активный спринт",
            responses={404: {"model": ErrorResponse}},
        )
        self._router.add_api_route(
            "/{project_id}/sprints/{sprint_id}", self.get_sprint, methods=["GET"],
            response_model=SuccessResponse[SprintResponse],
            summary="Получить спринт",
            responses={404: {"model": ErrorResponse}},
        )
        self._router.add_api_route(
            "/{project_id}/sprints", self.create_sprint, methods=["POST"],
            response_model=SuccessResponse[SprintResponse], status_code=201,
            summary="Создать спринт",
        )
        self._router.add_api_route(
            "/{project_id}/sprints/{sprint_id}/start", self.start_sprint, methods=["POST"],
            response_model=MessageResponse, summary="Запустить спринт",
        )
        self._router.add_api_route(
            "/{project_id}/sprints/{sprint_id}/goal", self.update_sprint_goal, methods=["PATCH"],
            response_model=MessageResponse, summary="Обновить цель спринта",
        )
        self._router.add_api_route(
            "/{project_id}/sprints/{sprint_id}/date-range", self.update_sprint_date_range, methods=["PATCH"],
            response_model=MessageResponse, summary="Обновить даты спринта",
        )
        self._router.add_api_route(
            "/{project_id}/sprints/{sprint_id}/retro", self.create_sprint_retro, methods=["POST"],
            response_model=MessageResponse, summary="Создать ретроспективу спринта",
        )

    async def list_sprints(
        self, ws_id: str, project_id: str,
        caller_id: str = Depends(get_current_user_id),
        sprint_repo=Depends(get_sprint_repository),
        permission_checker=Depends(get_project_permission_checker),
    ) -> SuccessResponse[list[SprintResponse]]:
        handler = GetSprintsByProjectHandler(sprint_repo=sprint_repo, permission_checker=permission_checker)
        query = GetSprintsByProjectQuery(caller_id=caller_id, project_id=project_id)
        dto = await handler.handle(query)
        items = [SprintResponse.model_validate(s.__dict__) for s in dto.items]
        return SuccessResponse(data=items)

    async def get_active_sprint(
        self, ws_id: str, project_id: str,
        caller_id: str = Depends(get_current_user_id),
        sprint_repo=Depends(get_sprint_repository),
        permission_checker=Depends(get_project_permission_checker),
    ) -> SuccessResponse[SprintResponse]:
        handler = GetActiveSprintHandler(sprint_repo=sprint_repo, permission_checker=permission_checker)
        query = GetActiveSprintQuery(caller_id=caller_id, project_id=project_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=SprintResponse.model_validate(dto.__dict__))

    async def get_sprint(
        self, ws_id: str, project_id: str, sprint_id: str,
        caller_id: str = Depends(get_current_user_id),
        sprint_repo=Depends(get_sprint_repository),
        permission_checker=Depends(get_project_permission_checker),
    ) -> SuccessResponse[SprintResponse]:
        handler = GetSprintHandler(sprint_repo=sprint_repo, permission_checker=permission_checker)
        query = GetSprintQuery(caller_id=caller_id, sprint_id=sprint_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=SprintResponse.model_validate(dto.__dict__))

    async def create_sprint(
        self, ws_id: str, project_id: str, body: CreateSprintRequest,
        caller_id: str = Depends(get_current_user_id),
        project_repo=Depends(get_project_repository),
        sprint_repo=Depends(get_sprint_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> SuccessResponse[SprintResponse]:
        handler = CreateSprintHandler(
            project_repo=project_repo, sprint_repo=sprint_repo,
            permission_checker=permission_checker, event_bus=event_bus,
        )
        command = CreateSprintCommand(
            caller_id=caller_id, project_id=project_id,
            name=body.name, goal=body.goal,
            start_date=str(body.start_date) if body.start_date else None,
            end_date=str(body.end_date) if body.end_date else None,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=SprintResponse.model_validate(dto.__dict__))

    async def start_sprint(
        self, ws_id: str, project_id: str, sprint_id: str,
        caller_id: str = Depends(get_current_user_id),
        sprint_repo=Depends(get_sprint_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = StartSprintHandler(
            sprint_repo=sprint_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(StartSprintCommand(caller_id=caller_id, sprint_id=sprint_id))
        return SuccessResponse(data={"message": "Спринт запущен"})

    async def update_sprint_goal(
        self, ws_id: str, project_id: str, sprint_id: str, body: UpdateSprintGoalRequest,
        caller_id: str = Depends(get_current_user_id),
        sprint_repo=Depends(get_sprint_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = UpdateSprintGoalHandler(
            sprint_repo=sprint_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(UpdateSprintGoalCommand(caller_id=caller_id, sprint_id=sprint_id, goal=body.goal))
        return SuccessResponse(data={"message": "Цель спринта обновлена"})

    async def update_sprint_date_range(
        self, ws_id: str, project_id: str, sprint_id: str, body: UpdateSprintDateRangeRequest,
        caller_id: str = Depends(get_current_user_id),
        sprint_repo=Depends(get_sprint_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = UpdateSprintDateRangeHandler(
            sprint_repo=sprint_repo, permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(UpdateSprintDateRangeCommand(
            caller_id=caller_id, sprint_id=sprint_id,
            start_date=str(body.start_date) if body.start_date else None,
            end_date=str(body.end_date) if body.end_date else None,
        ))
        return SuccessResponse(data={"message": "Даты спринта обновлены"})

    async def create_sprint_retro(
        self, ws_id: str, project_id: str, sprint_id: str, body: CreateSprintRetroRequest,
        caller_id: str = Depends(get_current_user_id),
        sprint_repo=Depends(get_sprint_repository),
        retro_template_repo=Depends(get_retro_template_repository),
        permission_checker=Depends(get_project_permission_checker),
        event_bus=Depends(get_project_event_bus),
    ) -> MessageResponse:
        handler = CreateSprintRetroHandler(
            sprint_repo=sprint_repo, retro_template_repo=retro_template_repo,
            permission_checker=permission_checker, event_bus=event_bus,
        )
        await handler.handle(CreateSprintRetroCommand(
            caller_id=caller_id, sprint_id=sprint_id, template_id=body.template_id,
        ))
        return SuccessResponse(data={"message": "Ретроспектива создана"})
