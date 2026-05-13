from __future__ import annotations

from fastapi import Depends

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import ErrorResponse, SuccessResponse

from app.context.timetracking.application.commands.approve_time_entry import (
    ApproveTimeEntryCommand,
    ApproveTimeEntryHandler,
)
from app.context.timetracking.application.commands.reject_time_entry import (
    RejectTimeEntryCommand,
    RejectTimeEntryHandler,
)
from app.context.timetracking.application.commands.resubmit_time_entry import (
    ResubmitTimeEntryCommand,
    ResubmitTimeEntryHandler,
)
from app.context.timetracking.application.commands.submit_time_entry import (
    SubmitTimeEntryCommand,
    SubmitTimeEntryHandler,
)
from app.context.timetracking.application.queries.get_submitted_for_approval import (
    GetSubmittedForApprovalHandler,
    GetSubmittedForApprovalQuery,
)
from app.context.timetracking.presentation.dependencies import (
    get_current_user_id,
    get_time_entry_repository,
    get_timetracking_event_bus,
    get_timetracking_permission_checker,
)
from app.context.timetracking.presentation.schemas.requests.reject_time_entry_request import (
    RejectTimeEntryRequest,
)
from app.context.timetracking.presentation.schemas.responses.time_entry_response import (
    TimeEntryResponse,
)


class TimeEntryApprovalController(BaseController):
    """
    Контроллер workflow утверждения записей времени.

    Endpoint'ы:
        POST /time-entries/{entry_id}/submit                 — Отправить на утверждение
        POST /time-entries/{entry_id}/resubmit               — Отправить повторно после отклонения
        POST /time-entries/{entry_id}/approve                — Утвердить (менеджер)
        POST /time-entries/{entry_id}/reject                 — Отклонить (менеджер)
        GET  /workspaces/{ws_id}/time-entries/pending        — Список ожидающих утверждения
    """

    def __init__(self) -> None:
        super().__init__(prefix="", tags=["TimeTracking — Approval"])

    def _register_routes(self) -> None:
        std = {
            401: {"description": "Не аутентифицирован", "model": ErrorResponse},
            403: {"description": "Недостаточно прав", "model": ErrorResponse},
            404: {"description": "Запись не найдена", "model": ErrorResponse},
        }
        self._router.add_api_route(
            "/time-entries/{entry_id}/submit", self.submit, methods=["POST"],
            response_model=SuccessResponse[TimeEntryResponse],
            summary="Отправить запись на утверждение", responses={200: {}, **std},
        )
        self._router.add_api_route(
            "/time-entries/{entry_id}/resubmit", self.resubmit, methods=["POST"],
            response_model=SuccessResponse[TimeEntryResponse],
            summary="Повторно отправить отклонённую запись", responses={200: {}, **std},
        )
        self._router.add_api_route(
            "/time-entries/{entry_id}/approve", self.approve, methods=["POST"],
            response_model=SuccessResponse[TimeEntryResponse],
            summary="Утвердить запись (менеджер)",
            responses={200: {}, 409: {"description": "Нельзя утвердить свою же запись",
                                      "model": ErrorResponse}, **std},
        )
        self._router.add_api_route(
            "/time-entries/{entry_id}/reject", self.reject, methods=["POST"],
            response_model=SuccessResponse[TimeEntryResponse],
            summary="Отклонить запись (менеджер)", responses={200: {}, **std},
        )
        self._router.add_api_route(
            "/workspaces/{workspace_id}/time-entries/pending",
            self.get_pending, methods=["GET"],
            response_model=SuccessResponse[list[TimeEntryResponse]],
            summary="Записи, ожидающие утверждения",
            responses={200: {}, **{k: v for k, v in std.items() if k != 404}},
        )

    async def submit(
        self,
        entry_id: str,
        caller_id: str = Depends(get_current_user_id),
        time_entry_repo=Depends(get_time_entry_repository),
        permission_checker=Depends(get_timetracking_permission_checker),
        event_bus=Depends(get_timetracking_event_bus),
    ) -> SuccessResponse[TimeEntryResponse]:
        handler = SubmitTimeEntryHandler(
            time_entry_repo=time_entry_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        dto = await handler.handle(SubmitTimeEntryCommand(caller_id=caller_id, entry_id=entry_id))
        return SuccessResponse(data=TimeEntryResponse.model_validate(dto.model_dump()))

    async def resubmit(
        self,
        entry_id: str,
        caller_id: str = Depends(get_current_user_id),
        time_entry_repo=Depends(get_time_entry_repository),
        permission_checker=Depends(get_timetracking_permission_checker),
        event_bus=Depends(get_timetracking_event_bus),
    ) -> SuccessResponse[TimeEntryResponse]:
        handler = ResubmitTimeEntryHandler(
            time_entry_repo=time_entry_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        dto = await handler.handle(ResubmitTimeEntryCommand(caller_id=caller_id, entry_id=entry_id))
        return SuccessResponse(data=TimeEntryResponse.model_validate(dto.model_dump()))

    async def approve(
        self,
        entry_id: str,
        caller_id: str = Depends(get_current_user_id),
        time_entry_repo=Depends(get_time_entry_repository),
        permission_checker=Depends(get_timetracking_permission_checker),
        event_bus=Depends(get_timetracking_event_bus),
    ) -> SuccessResponse[TimeEntryResponse]:
        handler = ApproveTimeEntryHandler(
            time_entry_repo=time_entry_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        dto = await handler.handle(ApproveTimeEntryCommand(caller_id=caller_id, entry_id=entry_id))
        return SuccessResponse(data=TimeEntryResponse.model_validate(dto.model_dump()))

    async def reject(
        self,
        entry_id: str,
        body: RejectTimeEntryRequest,
        caller_id: str = Depends(get_current_user_id),
        time_entry_repo=Depends(get_time_entry_repository),
        permission_checker=Depends(get_timetracking_permission_checker),
        event_bus=Depends(get_timetracking_event_bus),
    ) -> SuccessResponse[TimeEntryResponse]:
        handler = RejectTimeEntryHandler(
            time_entry_repo=time_entry_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        dto = await handler.handle(RejectTimeEntryCommand(
            caller_id=caller_id, entry_id=entry_id, reason=body.reason,
        ))
        return SuccessResponse(data=TimeEntryResponse.model_validate(dto.model_dump()))

    async def get_pending(
        self,
        workspace_id: str,
        caller_id: str = Depends(get_current_user_id),
        time_entry_repo=Depends(get_time_entry_repository),
        permission_checker=Depends(get_timetracking_permission_checker),
    ) -> SuccessResponse[list[TimeEntryResponse]]:
        handler = GetSubmittedForApprovalHandler(
            time_entry_repo=time_entry_repo,
            permission_checker=permission_checker,
        )
        dto = await handler.handle(GetSubmittedForApprovalQuery(
            caller_id=caller_id, workspace_id=workspace_id,
        ))
        items = [TimeEntryResponse.model_validate(e.model_dump()) for e in dto.items]
        return SuccessResponse(data=items)
