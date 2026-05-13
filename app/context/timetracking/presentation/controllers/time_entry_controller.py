from __future__ import annotations

from fastapi import Depends, Query

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageData,
    MessageResponse,
    SuccessResponse,
)

from app.context.timetracking.application.commands.add_time_entry_tag import (
    AddTimeEntryTagCommand,
    AddTimeEntryTagHandler,
)
from app.context.timetracking.application.commands.create_manual_time_entry import (
    CreateManualTimeEntryCommand,
    CreateManualTimeEntryHandler,
)
from app.context.timetracking.application.commands.delete_time_entry import (
    DeleteTimeEntryCommand,
    DeleteTimeEntryHandler,
)
from app.context.timetracking.application.commands.pause_timer import (
    PauseTimerCommand,
    PauseTimerHandler,
)
from app.context.timetracking.application.commands.remove_time_entry_tag import (
    RemoveTimeEntryTagCommand,
    RemoveTimeEntryTagHandler,
)
from app.context.timetracking.application.commands.resume_timer import (
    ResumeTimerCommand,
    ResumeTimerHandler,
)
from app.context.timetracking.application.commands.start_timer import (
    StartTimerCommand,
    StartTimerHandler,
)
from app.context.timetracking.application.commands.stop_timer import (
    StopTimerCommand,
    StopTimerHandler,
)
from app.context.timetracking.application.commands.update_time_entry import (
    UpdateTimeEntryCommand,
    UpdateTimeEntryHandler,
)
from app.context.timetracking.application.queries.get_my_time_entries import (
    GetMyTimeEntriesHandler,
    GetMyTimeEntriesQuery,
)
from app.context.timetracking.application.queries.get_running_timer import (
    GetRunningTimerHandler,
    GetRunningTimerQuery,
)
from app.context.timetracking.application.queries.get_time_entry import (
    GetTimeEntryHandler,
    GetTimeEntryQuery,
)
from app.context.timetracking.presentation.dependencies import (
    get_activity_category_repository,
    get_current_user_id,
    get_time_entry_repository,
    get_time_entry_tag_repository,
    get_timetracking_epic_port,
    get_timetracking_event_bus,
    get_timetracking_permission_checker,
    get_timetracking_project_port,
    get_timetracking_task_port,
    get_timetracking_workspace_port,
)
from app.context.timetracking.presentation.schemas.requests.create_manual_time_entry_request import (
    CreateManualTimeEntryRequest,
)
from app.context.timetracking.presentation.schemas.requests.start_timer_request import (
    StartTimerRequest,
)
from app.context.timetracking.presentation.schemas.requests.tag_requests import (
    AddTimeEntryTagRequest,
)
from app.context.timetracking.presentation.schemas.requests.update_time_entry_request import (
    UpdateTimeEntryRequest,
)
from app.context.timetracking.presentation.schemas.responses.time_entry_response import (
    TimeEntryResponse,
)


class TimeEntryController(BaseController):
    """
    Контроллер записей времени и таймера.

    Endpoint'ы:
        POST   /time-entries/timer/start                 — Запустить таймер
        POST   /time-entries/{entry_id}/timer/pause      — Поставить на паузу
        POST   /time-entries/{entry_id}/timer/resume     — Возобновить
        POST   /time-entries/{entry_id}/timer/stop       — Остановить
        GET    /time-entries/timer/current               — Текущий таймер пользователя
        POST   /time-entries                             — Создать запись (ручной ввод)
        GET    /time-entries/me                          — Свои записи (опционально за дату)
        GET    /time-entries/{entry_id}                  — Получить запись
        PATCH  /time-entries/{entry_id}                  — Обновить запись (DRAFT)
        DELETE /time-entries/{entry_id}                  — Удалить запись (DRAFT)
        POST   /time-entries/{entry_id}/tags             — Добавить тег
        DELETE /time-entries/{entry_id}/tags/{tag_id}    — Убрать тег
    """

    def __init__(self) -> None:
        super().__init__(prefix="/time-entries", tags=["TimeTracking"])

    def _register_routes(self) -> None:
        std = {
            401: {"description": "Не аутентифицирован", "model": ErrorResponse},
            403: {"description": "Недостаточно прав", "model": ErrorResponse},
        }
        self._router.add_api_route(
            "/timer/start", self.start_timer, methods=["POST"],
            response_model=SuccessResponse[TimeEntryResponse], status_code=201,
            summary="Запустить таймер",
            responses={201: {"description": "Таймер запущен"}, **std,
                       409: {"description": "Уже есть активный таймер", "model": ErrorResponse}},
        )
        self._router.add_api_route(
            "/{entry_id}/timer/pause", self.pause_timer, methods=["POST"],
            response_model=SuccessResponse[TimeEntryResponse],
            summary="Поставить таймер на паузу",
            responses={200: {"description": "Таймер на паузе"}, 404: {"model": ErrorResponse}, **std},
        )
        self._router.add_api_route(
            "/{entry_id}/timer/resume", self.resume_timer, methods=["POST"],
            response_model=SuccessResponse[TimeEntryResponse],
            summary="Возобновить таймер",
            responses={200: {"description": "Таймер возобновлён"}, 404: {"model": ErrorResponse}, **std},
        )
        self._router.add_api_route(
            "/{entry_id}/timer/stop", self.stop_timer, methods=["POST"],
            response_model=SuccessResponse[TimeEntryResponse],
            summary="Остановить таймер",
            responses={200: {"description": "Таймер остановлен"}, 404: {"model": ErrorResponse}, **std},
        )
        self._router.add_api_route(
            "/timer/current", self.get_current_timer, methods=["GET"],
            response_model=SuccessResponse[TimeEntryResponse | None],
            summary="Текущий запущенный таймер пользователя",
            responses={200: {"description": "Активный таймер или null"}, **std},
        )
        self._router.add_api_route(
            "", self.create_manual, methods=["POST"],
            response_model=SuccessResponse[TimeEntryResponse], status_code=201,
            summary="Создать запись времени вручную",
            responses={201: {"description": "Запись создана"}, **std,
                       422: {"model": ErrorResponse}},
        )
        self._router.add_api_route(
            "/me", self.get_my_entries, methods=["GET"],
            response_model=SuccessResponse[list[TimeEntryResponse]],
            summary="Мои записи времени",
            responses={200: {"description": "Список записей"}, **std},
        )
        self._router.add_api_route(
            "/{entry_id}", self.get_entry, methods=["GET"],
            response_model=SuccessResponse[TimeEntryResponse],
            summary="Получить запись времени",
            responses={200: {"description": "Запись"}, 404: {"model": ErrorResponse}, **std},
        )
        self._router.add_api_route(
            "/{entry_id}", self.update_entry, methods=["PATCH"],
            response_model=SuccessResponse[TimeEntryResponse],
            summary="Обновить запись времени (только DRAFT)",
            responses={200: {"description": "Запись обновлена"}, 404: {"model": ErrorResponse}, **std,
                       409: {"model": ErrorResponse}},
        )
        self._router.add_api_route(
            "/{entry_id}", self.delete_entry, methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить запись времени (только DRAFT)",
            responses={200: {"description": "Запись удалена"}, 404: {"model": ErrorResponse}, **std,
                       409: {"model": ErrorResponse}},
        )
        self._router.add_api_route(
            "/{entry_id}/tags", self.add_tag, methods=["POST"],
            response_model=SuccessResponse[TimeEntryResponse],
            summary="Добавить тег к записи",
            responses={200: {"description": "Тег добавлен"}, 404: {"model": ErrorResponse}, **std},
        )
        self._router.add_api_route(
            "/{entry_id}/tags/{tag_id}", self.remove_tag, methods=["DELETE"],
            response_model=SuccessResponse[TimeEntryResponse],
            summary="Удалить тег из записи",
            responses={200: {"description": "Тег удалён"}, 404: {"model": ErrorResponse}, **std},
        )

    # --- Handlers ---

    async def start_timer(
        self,
        body: StartTimerRequest,
        caller_id: str = Depends(get_current_user_id),
        time_entry_repo=Depends(get_time_entry_repository),
        permission_checker=Depends(get_timetracking_permission_checker),
        workspace_port=Depends(get_timetracking_workspace_port),
        task_port=Depends(get_timetracking_task_port),
        project_port=Depends(get_timetracking_project_port),
        epic_port=Depends(get_timetracking_epic_port),
        event_bus=Depends(get_timetracking_event_bus),
    ) -> SuccessResponse[TimeEntryResponse]:
        handler = StartTimerHandler(
            time_entry_repo=time_entry_repo,
            permission_checker=permission_checker,
            workspace_port=workspace_port,
            task_port=task_port,
            project_port=project_port,
            epic_port=epic_port,
            event_bus=event_bus,
        )
        dto = await handler.handle(StartTimerCommand(
            caller_id=caller_id,
            workspace_id=body.workspace_id,
            task_id=body.task_id,
            project_id=body.project_id,
            epic_id=body.epic_id,
            description=body.description,
        ))
        return SuccessResponse(data=TimeEntryResponse.model_validate(dto.model_dump()))

    async def pause_timer(
        self,
        entry_id: str,
        caller_id: str = Depends(get_current_user_id),
        time_entry_repo=Depends(get_time_entry_repository),
        permission_checker=Depends(get_timetracking_permission_checker),
        event_bus=Depends(get_timetracking_event_bus),
    ) -> SuccessResponse[TimeEntryResponse]:
        handler = PauseTimerHandler(
            time_entry_repo=time_entry_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        dto = await handler.handle(PauseTimerCommand(caller_id=caller_id, entry_id=entry_id))
        return SuccessResponse(data=TimeEntryResponse.model_validate(dto.model_dump()))

    async def resume_timer(
        self,
        entry_id: str,
        caller_id: str = Depends(get_current_user_id),
        time_entry_repo=Depends(get_time_entry_repository),
        permission_checker=Depends(get_timetracking_permission_checker),
        event_bus=Depends(get_timetracking_event_bus),
    ) -> SuccessResponse[TimeEntryResponse]:
        handler = ResumeTimerHandler(
            time_entry_repo=time_entry_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        dto = await handler.handle(ResumeTimerCommand(caller_id=caller_id, entry_id=entry_id))
        return SuccessResponse(data=TimeEntryResponse.model_validate(dto.model_dump()))

    async def stop_timer(
        self,
        entry_id: str,
        caller_id: str = Depends(get_current_user_id),
        time_entry_repo=Depends(get_time_entry_repository),
        permission_checker=Depends(get_timetracking_permission_checker),
        event_bus=Depends(get_timetracking_event_bus),
    ) -> SuccessResponse[TimeEntryResponse]:
        handler = StopTimerHandler(
            time_entry_repo=time_entry_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        dto = await handler.handle(StopTimerCommand(caller_id=caller_id, entry_id=entry_id))
        return SuccessResponse(data=TimeEntryResponse.model_validate(dto.model_dump()))

    async def get_current_timer(
        self,
        caller_id: str = Depends(get_current_user_id),
        time_entry_repo=Depends(get_time_entry_repository),
    ) -> SuccessResponse[TimeEntryResponse | None]:
        handler = GetRunningTimerHandler(time_entry_repo=time_entry_repo)
        dto = await handler.handle(GetRunningTimerQuery(caller_id=caller_id))
        if dto is None:
            return SuccessResponse(data=None)
        return SuccessResponse(data=TimeEntryResponse.model_validate(dto.model_dump()))

    async def create_manual(
        self,
        body: CreateManualTimeEntryRequest,
        caller_id: str = Depends(get_current_user_id),
        time_entry_repo=Depends(get_time_entry_repository),
        permission_checker=Depends(get_timetracking_permission_checker),
        workspace_port=Depends(get_timetracking_workspace_port),
        task_port=Depends(get_timetracking_task_port),
        project_port=Depends(get_timetracking_project_port),
        epic_port=Depends(get_timetracking_epic_port),
        event_bus=Depends(get_timetracking_event_bus),
    ) -> SuccessResponse[TimeEntryResponse]:
        handler = CreateManualTimeEntryHandler(
            time_entry_repo=time_entry_repo,
            permission_checker=permission_checker,
            workspace_port=workspace_port,
            task_port=task_port,
            project_port=project_port,
            epic_port=epic_port,
            event_bus=event_bus,
        )
        dto = await handler.handle(CreateManualTimeEntryCommand(
            caller_id=caller_id,
            workspace_id=body.workspace_id,
            duration_seconds=body.duration_seconds,
            entry_date=body.entry_date,
            task_id=body.task_id,
            project_id=body.project_id,
            epic_id=body.epic_id,
            description=body.description,
            is_billable=body.is_billable,
            hourly_rate_amount=body.hourly_rate_amount,
            hourly_rate_currency=body.hourly_rate_currency,
            category_id=body.category_id,
        ))
        return SuccessResponse(data=TimeEntryResponse.model_validate(dto.model_dump()))

    async def get_my_entries(
        self,
        entry_date: str | None = Query(default=None, description="ISO дата (YYYY-MM-DD)"),
        caller_id: str = Depends(get_current_user_id),
        time_entry_repo=Depends(get_time_entry_repository),
    ) -> SuccessResponse[list[TimeEntryResponse]]:
        handler = GetMyTimeEntriesHandler(time_entry_repo=time_entry_repo)
        dto = await handler.handle(GetMyTimeEntriesQuery(caller_id=caller_id, entry_date=entry_date))
        items = [TimeEntryResponse.model_validate(e.model_dump()) for e in dto.items]
        return SuccessResponse(data=items)

    async def get_entry(
        self,
        entry_id: str,
        caller_id: str = Depends(get_current_user_id),
        time_entry_repo=Depends(get_time_entry_repository),
        permission_checker=Depends(get_timetracking_permission_checker),
    ) -> SuccessResponse[TimeEntryResponse]:
        handler = GetTimeEntryHandler(
            time_entry_repo=time_entry_repo,
            permission_checker=permission_checker,
        )
        dto = await handler.handle(GetTimeEntryQuery(caller_id=caller_id, entry_id=entry_id))
        return SuccessResponse(data=TimeEntryResponse.model_validate(dto.model_dump()))

    async def update_entry(
        self,
        entry_id: str,
        body: UpdateTimeEntryRequest,
        caller_id: str = Depends(get_current_user_id),
        time_entry_repo=Depends(get_time_entry_repository),
        permission_checker=Depends(get_timetracking_permission_checker),
        event_bus=Depends(get_timetracking_event_bus),
    ) -> SuccessResponse[TimeEntryResponse]:
        handler = UpdateTimeEntryHandler(
            time_entry_repo=time_entry_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        dto = await handler.handle(UpdateTimeEntryCommand(
            caller_id=caller_id,
            entry_id=entry_id,
            description=body.description,
            is_billable=body.is_billable,
            hourly_rate_amount=body.hourly_rate_amount,
            hourly_rate_currency=body.hourly_rate_currency,
            category_id=body.category_id,
        ))
        return SuccessResponse(data=TimeEntryResponse.model_validate(dto.model_dump()))

    async def delete_entry(
        self,
        entry_id: str,
        caller_id: str = Depends(get_current_user_id),
        time_entry_repo=Depends(get_time_entry_repository),
        permission_checker=Depends(get_timetracking_permission_checker),
        event_bus=Depends(get_timetracking_event_bus),
    ) -> MessageResponse:
        handler = DeleteTimeEntryHandler(
            time_entry_repo=time_entry_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        await handler.handle(DeleteTimeEntryCommand(caller_id=caller_id, entry_id=entry_id))
        return SuccessResponse(data=MessageData(message="Запись удалена"))

    async def add_tag(
        self,
        entry_id: str,
        body: AddTimeEntryTagRequest,
        caller_id: str = Depends(get_current_user_id),
        time_entry_repo=Depends(get_time_entry_repository),
        tag_repo=Depends(get_time_entry_tag_repository),
        permission_checker=Depends(get_timetracking_permission_checker),
        event_bus=Depends(get_timetracking_event_bus),
    ) -> SuccessResponse[TimeEntryResponse]:
        handler = AddTimeEntryTagHandler(
            time_entry_repo=time_entry_repo,
            tag_repo=tag_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        dto = await handler.handle(AddTimeEntryTagCommand(
            caller_id=caller_id, entry_id=entry_id, tag_id=body.tag_id,
        ))
        return SuccessResponse(data=TimeEntryResponse.model_validate(dto.model_dump()))

    async def remove_tag(
        self,
        entry_id: str,
        tag_id: str,
        caller_id: str = Depends(get_current_user_id),
        time_entry_repo=Depends(get_time_entry_repository),
        permission_checker=Depends(get_timetracking_permission_checker),
        event_bus=Depends(get_timetracking_event_bus),
    ) -> SuccessResponse[TimeEntryResponse]:
        handler = RemoveTimeEntryTagHandler(
            time_entry_repo=time_entry_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        dto = await handler.handle(RemoveTimeEntryTagCommand(
            caller_id=caller_id, entry_id=entry_id, tag_id=tag_id,
        ))
        return SuccessResponse(data=TimeEntryResponse.model_validate(dto.model_dump()))
