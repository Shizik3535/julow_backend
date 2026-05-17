from __future__ import annotations

from fastapi import Depends

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageData,
    MessageResponse,
    SuccessResponse,
)

from app.context.analytics.application.commands.create_report import CreateReportCommand, CreateReportHandler
from app.context.analytics.application.commands.delete_report import DeleteReportCommand, DeleteReportHandler
from app.context.analytics.application.commands.generate_report import (
    GenerateReportCommand,
    GenerateReportHandler,
)
from app.context.analytics.application.commands.remove_report_schedule import (
    DeactivateReportScheduleCommand,
    DeactivateReportScheduleHandler,
    RemoveReportScheduleCommand,
    RemoveReportScheduleHandler,
)
from app.context.analytics.application.commands.send_report_now import SendReportNowCommand, SendReportNowHandler
from app.context.analytics.application.commands.set_report_schedule import (
    SetReportScheduleCommand,
    SetReportScheduleHandler,
)
from app.context.analytics.application.commands.share_report import (
    ShareReportCommand,
    ShareReportHandler,
    UnshareReportCommand,
    UnshareReportHandler,
)
from app.context.analytics.application.commands.update_report import UpdateReportCommand, UpdateReportHandler
from app.context.analytics.application.queries.get_report import GetReportHandler, GetReportQuery
from app.context.analytics.application.queries.get_report_job import GetReportJobHandler, GetReportJobQuery
from app.context.analytics.application.queries.list_reports_by_workspace import (
    ListReportsByWorkspaceHandler,
    ListReportsByWorkspaceQuery,
)

from app.context.analytics.presentation.dependencies import (
    get_analytics_event_bus,
    get_analytics_permission_checker,
    get_analytics_workspace_port,
    get_current_user_id,
    get_report_generator_port,
    get_report_repository,
)
from app.context.analytics.presentation.schemas.requests.analytics_requests import (
    CreateReportRequest,
    GenerateReportRequest,
    SetReportScheduleRequest,
    ShareReportRequest,
    UnshareReportRequest,
    UpdateReportRequest,
)
from app.context.analytics.presentation.schemas.requests.query_mapper import query_request_to_dto
from app.context.analytics.presentation.schemas.responses.analytics_responses import (
    ReportJobResponse,
    ReportResponse,
)


class ReportController(BaseController):
    """
    Контроллер отчётов.

    Endpoint'ы:
        POST   /                                           — Создать отчёт
        GET    /                                           — Список отчётов workspace
        GET    /{report_id}                                — Получить отчёт
        PATCH  /{report_id}                                — Обновить отчёт
        DELETE /{report_id}                                — Удалить отчёт
        POST   /{report_id}/generate                       — Сгенерировать отчёт
        POST   /{report_id}/send-now                       — Немедленно отправить
        PATCH  /{report_id}/schedule                       — Установить расписание
        DELETE /{report_id}/schedule                        — Удалить расписание
        POST   /{report_id}/schedule/deactivate            — Деактивировать расписание
        POST   /{report_id}/share                          — Расшарить
        DELETE /{report_id}/share                          — Снять шаринг
        GET    /jobs/{job_id}                              — Статус задания генерации
    """

    def __init__(self) -> None:
        super().__init__(prefix="/reports", tags=["Analytics — Reports"])

    def _register_routes(self) -> None:
        std = {
            401: {"description": "Не аутентифицирован", "model": ErrorResponse},
            403: {"description": "Недостаточно прав", "model": ErrorResponse},
        }
        self._router.add_api_route(
            "",
            self.create_report,
            methods=["POST"],
            response_model=SuccessResponse[ReportResponse],
            status_code=201,
            summary="Создать отчёт",
            description="Создаёт новый отчёт в workspace (без расписания).",
            responses={
                201: {"description": "Отчёт создан"},
                **std,
                404: {"description": "Workspace не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "",
            self.list_reports_by_workspace,
            methods=["GET"],
            response_model=SuccessResponse[list[ReportResponse]],
            summary="Список отчётов workspace",
            description="Возвращает отчёты workspace с опциональным фильтром по типу/BC.",
            responses={200: {"description": "Список отчётов"}, **std},
        )
        self._router.add_api_route(
            "/generate",
            self.generate_report,
            methods=["POST"],
            response_model=SuccessResponse[ReportJobResponse],
            status_code=202,
            summary="Сгенерировать отчёт",
            description="Запрашивает асинхронную генерацию отчёта (ad-hoc или по report_id).",
            responses={
                202: {"description": "Запрос на генерацию принят"},
                **std,
                400: {"description": "Некорректный запрос", "model": ErrorResponse},
                404: {"description": "Отчёт/Workspace не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{report_id}",
            self.get_report,
            methods=["GET"],
            response_model=SuccessResponse[ReportResponse],
            summary="Получить отчёт",
            description="Возвращает данные отчёта по ID.",
            responses={
                200: {"description": "Данные отчёта"},
                **std,
                404: {"description": "Отчёт не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{report_id}",
            self.update_report,
            methods=["PATCH"],
            response_model=SuccessResponse[ReportResponse],
            summary="Обновить отчёт",
            description="Обновляет имя/описание/query отчёта.",
            responses={
                200: {"description": "Отчёт обновлён"},
                **std,
                404: {"description": "Отчёт не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{report_id}",
            self.delete_report,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить отчёт",
            description="Удаляет отчёт. Доступно владельцу или admin.",
            responses={
                200: {"description": "Отчёт удалён"},
                **std,
                404: {"description": "Отчёт не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{report_id}/send-now",
            self.send_report_now,
            methods=["POST"],
            response_model=SuccessResponse[ReportJobResponse],
            summary="Немедленно отправить отчёт",
            description="Немедленная отправка scheduled-отчёта получателям.",
            responses={
                200: {"description": "Отчёт отправлен"},
                **std,
                400: {"description": "Нет расписания/workspace", "model": ErrorResponse},
                404: {"description": "Отчёт не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{report_id}/schedule",
            self.set_schedule,
            methods=["PATCH"],
            response_model=SuccessResponse[ReportResponse],
            summary="Установить расписание отчёта",
            description="Устанавливает/заменяет расписание отчёта.",
            responses={
                200: {"description": "Расписание установлено"},
                **std,
                404: {"description": "Отчёт не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{report_id}/schedule",
            self.remove_schedule,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить расписание отчёта",
            description="Удаляет расписание отчёта (отчёт остаётся).",
            responses={
                200: {"description": "Расписание удалено"},
                **std,
                404: {"description": "Отчёт не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{report_id}/schedule/deactivate",
            self.deactivate_schedule,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Деактивировать расписание",
            description="Деактивирует расписание отчёта без удаления.",
            responses={
                200: {"description": "Расписание деактивировано"},
                **std,
                404: {"description": "Отчёт не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{report_id}/share",
            self.share_report,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Расшарить отчёт",
            description="Расшаривает отчёт с пользователем.",
            responses={
                200: {"description": "Отчёт расшарен"},
                **std,
                404: {"description": "Отчёт не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{report_id}/share",
            self.unshare_report,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Снять шаринг отчёта",
            description="Снимает шаринг отчёта с пользователя.",
            responses={
                200: {"description": "Шаринг снят"},
                **std,
                404: {"description": "Отчёт не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/jobs/{job_id}",
            self.get_report_job,
            methods=["GET"],
            response_model=SuccessResponse[ReportJobResponse],
            summary="Статус задания генерации",
            description="Возвращает статус задания на генерацию отчёта по job_id.",
            responses={
                200: {"description": "Статус задания"},
                **std,
                404: {"description": "Задание не найдено", "model": ErrorResponse},
            },
        )

    # ------------------------------------------------------------------
    # Report CRUD
    # ------------------------------------------------------------------

    async def create_report(
        self,
        body: CreateReportRequest,
        caller_id: str = Depends(get_current_user_id),
        report_repo=Depends(get_report_repository),
        permission_checker=Depends(get_analytics_permission_checker),
        workspace_port=Depends(get_analytics_workspace_port),
        event_bus=Depends(get_analytics_event_bus),
    ) -> SuccessResponse[ReportResponse]:
        query_dto = query_request_to_dto(body.query)
        handler = CreateReportHandler(
            report_repo=report_repo,
            permission_checker=permission_checker,
            workspace_port=workspace_port,
            event_bus=event_bus,
        )
        command = CreateReportCommand(
            caller_id=caller_id,
            workspace_id=body.workspace_id,
            name=body.name,
            report_type=body.report_type.value,
            query=query_dto,
            description=body.description,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=ReportResponse.model_validate(dto.model_dump()))

    async def list_reports_by_workspace(
        self,
        workspace_id: str,
        report_type: str | None = None,
        bounded_context: str | None = None,
        caller_id: str = Depends(get_current_user_id),
        report_repo=Depends(get_report_repository),
        permission_checker=Depends(get_analytics_permission_checker),
    ) -> SuccessResponse[list[ReportResponse]]:
        handler = ListReportsByWorkspaceHandler(
            report_repo=report_repo,
            permission_checker=permission_checker,
        )
        query = ListReportsByWorkspaceQuery(
            caller_id=caller_id,
            workspace_id=workspace_id,
            report_type=report_type,
            bounded_context=bounded_context,
        )
        dto = await handler.handle(query)
        items = [ReportResponse.model_validate(r.model_dump()) for r in dto.items]
        return SuccessResponse(data=items)

    async def get_report(
        self,
        report_id: str,
        caller_id: str = Depends(get_current_user_id),
        report_repo=Depends(get_report_repository),
        permission_checker=Depends(get_analytics_permission_checker),
    ) -> SuccessResponse[ReportResponse]:
        handler = GetReportHandler(
            report_repo=report_repo,
            permission_checker=permission_checker,
        )
        query = GetReportQuery(caller_id=caller_id, report_id=report_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=ReportResponse.model_validate(dto.model_dump()))

    async def update_report(
        self,
        report_id: str,
        body: UpdateReportRequest,
        caller_id: str = Depends(get_current_user_id),
        report_repo=Depends(get_report_repository),
        permission_checker=Depends(get_analytics_permission_checker),
        event_bus=Depends(get_analytics_event_bus),
    ) -> SuccessResponse[ReportResponse]:
        query_dto = query_request_to_dto(body.query) if body.query is not None else None
        handler = UpdateReportHandler(
            report_repo=report_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = UpdateReportCommand(
            caller_id=caller_id,
            report_id=report_id,
            name=body.name,
            description=body.description,
            query=query_dto,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=ReportResponse.model_validate(dto.model_dump()))

    async def delete_report(
        self,
        report_id: str,
        caller_id: str = Depends(get_current_user_id),
        report_repo=Depends(get_report_repository),
        permission_checker=Depends(get_analytics_permission_checker),
        event_bus=Depends(get_analytics_event_bus),
    ) -> MessageResponse:
        handler = DeleteReportHandler(
            report_repo=report_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = DeleteReportCommand(
            caller_id=caller_id,
            report_id=report_id,
        )
        await handler.handle(command)
        return MessageResponse(data=MessageData(message="Отчёт удалён"))

    # ------------------------------------------------------------------
    # Report generation
    # ------------------------------------------------------------------

    async def generate_report(
        self,
        body: GenerateReportRequest,
        caller_id: str = Depends(get_current_user_id),
        report_repo=Depends(get_report_repository),
        report_generator=Depends(get_report_generator_port),
        permission_checker=Depends(get_analytics_permission_checker),
        workspace_port=Depends(get_analytics_workspace_port),
        event_bus=Depends(get_analytics_event_bus),
    ) -> SuccessResponse[ReportJobResponse]:
        query_dto = query_request_to_dto(body.query) if body.query is not None else None
        handler = GenerateReportHandler(
            report_repo=report_repo,
            report_generator=report_generator,
            permission_checker=permission_checker,
            workspace_port=workspace_port,
            event_bus=event_bus,
        )
        command = GenerateReportCommand(
            caller_id=caller_id,
            workspace_id=body.workspace_id,
            format=body.format.value,
            report_id=body.report_id,
            report_type=body.report_type.value if body.report_type is not None else None,
            query=query_dto,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=ReportJobResponse.model_validate(dto.model_dump()))

    async def send_report_now(
        self,
        report_id: str,
        caller_id: str = Depends(get_current_user_id),
        report_repo=Depends(get_report_repository),
        report_generator=Depends(get_report_generator_port),
        permission_checker=Depends(get_analytics_permission_checker),
    ) -> SuccessResponse[ReportJobResponse]:
        handler = SendReportNowHandler(
            report_repo=report_repo,
            report_generator=report_generator,
            permission_checker=permission_checker,
        )
        command = SendReportNowCommand(
            caller_id=caller_id,
            report_id=report_id,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=ReportJobResponse.model_validate(dto.model_dump()))

    # ------------------------------------------------------------------
    # Report schedule
    # ------------------------------------------------------------------

    async def set_schedule(
        self,
        report_id: str,
        body: SetReportScheduleRequest,
        caller_id: str = Depends(get_current_user_id),
        report_repo=Depends(get_report_repository),
        permission_checker=Depends(get_analytics_permission_checker),
        event_bus=Depends(get_analytics_event_bus),
    ) -> SuccessResponse[ReportResponse]:
        handler = SetReportScheduleHandler(
            report_repo=report_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = SetReportScheduleCommand(
            caller_id=caller_id,
            report_id=report_id,
            frequency=body.frequency.value,
            recipients=body.recipients,
            is_active=body.is_active,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=ReportResponse.model_validate(dto.model_dump()))

    async def remove_schedule(
        self,
        report_id: str,
        caller_id: str = Depends(get_current_user_id),
        report_repo=Depends(get_report_repository),
        permission_checker=Depends(get_analytics_permission_checker),
        event_bus=Depends(get_analytics_event_bus),
    ) -> MessageResponse:
        handler = RemoveReportScheduleHandler(
            report_repo=report_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = RemoveReportScheduleCommand(
            caller_id=caller_id,
            report_id=report_id,
        )
        await handler.handle(command)
        return MessageResponse(data=MessageData(message="Расписание удалено"))

    async def deactivate_schedule(
        self,
        report_id: str,
        caller_id: str = Depends(get_current_user_id),
        report_repo=Depends(get_report_repository),
        permission_checker=Depends(get_analytics_permission_checker),
        event_bus=Depends(get_analytics_event_bus),
    ) -> MessageResponse:
        handler = DeactivateReportScheduleHandler(
            report_repo=report_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = DeactivateReportScheduleCommand(
            caller_id=caller_id,
            report_id=report_id,
        )
        await handler.handle(command)
        return MessageResponse(data=MessageData(message="Расписание деактивировано"))

    # ------------------------------------------------------------------
    # Report sharing
    # ------------------------------------------------------------------

    async def share_report(
        self,
        report_id: str,
        body: ShareReportRequest,
        caller_id: str = Depends(get_current_user_id),
        report_repo=Depends(get_report_repository),
        permission_checker=Depends(get_analytics_permission_checker),
        event_bus=Depends(get_analytics_event_bus),
    ) -> MessageResponse:
        handler = ShareReportHandler(
            report_repo=report_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = ShareReportCommand(
            caller_id=caller_id,
            report_id=report_id,
            user_id=body.user_id,
            access_level=body.access_level.value,
        )
        await handler.handle(command)
        return MessageResponse(data=MessageData(message="Отчёт расшарен"))

    async def unshare_report(
        self,
        report_id: str,
        body: UnshareReportRequest,
        caller_id: str = Depends(get_current_user_id),
        report_repo=Depends(get_report_repository),
        permission_checker=Depends(get_analytics_permission_checker),
        event_bus=Depends(get_analytics_event_bus),
    ) -> MessageResponse:
        handler = UnshareReportHandler(
            report_repo=report_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = UnshareReportCommand(
            caller_id=caller_id,
            report_id=report_id,
            user_id=body.user_id,
        )
        await handler.handle(command)
        return MessageResponse(data=MessageData(message="Шаринг снят"))

    # ------------------------------------------------------------------
    # Report job status
    # ------------------------------------------------------------------

    async def get_report_job(
        self,
        job_id: str,
        caller_id: str = Depends(get_current_user_id),
        report_generator=Depends(get_report_generator_port),
    ) -> SuccessResponse[ReportJobResponse]:
        handler = GetReportJobHandler(report_generator=report_generator)
        query = GetReportJobQuery(caller_id=caller_id, job_id=job_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=ReportJobResponse.model_validate(dto.model_dump()))
