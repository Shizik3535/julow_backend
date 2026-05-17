from __future__ import annotations

from fastapi import Depends

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    MessageData,
    MessageResponse,
    SuccessResponse,
)

from app.context.analytics.application.commands.add_widget import AddWidgetCommand, AddWidgetHandler
from app.context.analytics.application.commands.create_dashboard import (
    CreateDashboardCommand,
    CreateDashboardHandler,
)
from app.context.analytics.application.commands.create_dashboard_from_template import (
    CreateDashboardFromTemplateCommand,
    CreateDashboardFromTemplateHandler,
)
from app.context.analytics.application.commands.delete_dashboard import (
    DeleteDashboardCommand,
    DeleteDashboardHandler,
)
from app.context.analytics.application.commands.remove_widget import RemoveWidgetCommand, RemoveWidgetHandler
from app.context.analytics.application.commands.set_dashboard_auto_refresh import (
    SetDashboardAutoRefreshCommand,
    SetDashboardAutoRefreshHandler,
)
from app.context.analytics.application.commands.set_default_dashboard import (
    SetDefaultDashboardCommand,
    SetDefaultDashboardHandler,
)
from app.context.analytics.application.commands.share_dashboard import (
    ShareDashboardCommand,
    ShareDashboardHandler,
    UnshareDashboardCommand,
    UnshareDashboardHandler,
)
from app.context.analytics.application.commands.update_dashboard import (
    UpdateDashboardCommand,
    UpdateDashboardHandler,
)
from app.context.analytics.application.commands.update_dashboard_layout import (
    UpdateDashboardLayoutCommand,
    UpdateDashboardLayoutHandler,
)
from app.context.analytics.application.commands.update_widget import (
    UpdateWidgetCommand,
    UpdateWidgetHandler,
)
from app.context.analytics.application.dto.dashboard_dto import WidgetLayoutItemDTO
from app.context.analytics.application.queries.get_dashboard import GetDashboardHandler, GetDashboardQuery
from app.context.analytics.application.queries.get_widget_data import GetWidgetDataHandler, GetWidgetDataQuery
from app.context.analytics.application.queries.list_dashboards_by_workspace import (
    ListDashboardsByWorkspaceHandler,
    ListDashboardsByWorkspaceQuery,
    ListDashboardsSharedWithMeHandler,
    ListDashboardsSharedWithMeQuery,
)

from app.context.analytics.presentation.dependencies import (
    get_analytics_event_bus,
    get_analytics_permission_checker,
    get_analytics_query_executor_port,
    get_analytics_workspace_port,
    get_current_user_id,
    get_dashboard_repository,
    get_dashboard_template_repository,
)
from app.context.analytics.presentation.schemas.requests.analytics_requests import (
    AddWidgetRequest,
    CreateDashboardFromTemplateRequest,
    CreateDashboardRequest,
    SetDashboardAutoRefreshRequest,
    ShareDashboardRequest,
    UnshareDashboardRequest,
    UpdateDashboardLayoutRequest,
    UpdateDashboardRequest,
    UpdateWidgetRequest,
)
from app.context.analytics.presentation.schemas.requests.query_mapper import query_request_to_dto
from app.context.analytics.presentation.schemas.responses.analytics_responses import (
    AnalyticsResultResponse,
    DashboardResponse,
    WidgetResponse,
)


class DashboardController(BaseController):
    """
    Контроллер дашбордов.

    Endpoint'ы:
        POST   /                                           — Создать дашборд
        GET    /                                           — Список дашбордов workspace
        GET    /shared-with-me                            — Дашборды, расшаренные с пользователем
        GET    /{dashboard_id}                            — Получить дашборд
        PATCH  /{dashboard_id}                            — Обновить имя/описание
        DELETE /{dashboard_id}                            — Удалить дашборд
        PATCH  /{dashboard_id}/layout                     — Обновить layout виджетов
        PATCH  /{dashboard_id}/auto-refresh               — Настроить авто-обновление
        POST   /{dashboard_id}/default                    — Сделать default-дашбордом
        POST   /{dashboard_id}/share                      — Расшарить
        DELETE /{dashboard_id}/share                      — Снять шаринг
        POST   /{dashboard_id}/widgets                    — Добавить виджет
        PATCH  /{dashboard_id}/widgets/{widget_id}        — Обновить виджет
        DELETE /{dashboard_id}/widgets/{widget_id}        — Удалить виджет
        GET    /{dashboard_id}/widgets/{widget_id}/data   — Данные виджета
        POST   /from-template                             — Создать из шаблона
    """

    def __init__(self) -> None:
        super().__init__(prefix="/dashboards", tags=["Analytics — Dashboards"])

    def _register_routes(self) -> None:
        std = {
            401: {"description": "Не аутентифицирован", "model": ErrorResponse},
            403: {"description": "Недостаточно прав", "model": ErrorResponse},
        }
        self._router.add_api_route(
            "",
            self.create_dashboard,
            methods=["POST"],
            response_model=SuccessResponse[DashboardResponse],
            status_code=201,
            summary="Создать дашборд",
            description="Создаёт новый дашборд в workspace.",
            responses={
                201: {"description": "Дашборд создан"},
                **std,
                404: {"description": "Workspace не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "",
            self.list_dashboards_by_workspace,
            methods=["GET"],
            response_model=SuccessResponse[list[DashboardResponse]],
            summary="Список дашбордов workspace",
            description="Возвращает все дашборды workspace, видимые пользователю.",
            responses={200: {"description": "Список дашбордов"}, **std},
        )
        self._router.add_api_route(
            "/shared-with-me",
            self.list_dashboards_shared_with_me,
            methods=["GET"],
            response_model=SuccessResponse[list[DashboardResponse]],
            summary="Расшаренные со мной дашборды",
            description="Возвращает дашборды, расшаренные с текущим пользователем.",
            responses={200: {"description": "Список дашбордов"}, **std},
        )
        self._router.add_api_route(
            "/from-template",
            self.create_from_template,
            methods=["POST"],
            response_model=SuccessResponse[DashboardResponse],
            status_code=201,
            summary="Создать дашборд из шаблона",
            description="Создаёт дашборд на основе шаблона.",
            responses={
                201: {"description": "Дашборд создан из шаблона"},
                **std,
                404: {"description": "Шаблон/Workspace не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{dashboard_id}",
            self.get_dashboard,
            methods=["GET"],
            response_model=SuccessResponse[DashboardResponse],
            summary="Получить дашборд",
            description="Возвращает данные дашборда по ID.",
            responses={
                200: {"description": "Данные дашборда"},
                **std,
                404: {"description": "Дашборд не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{dashboard_id}",
            self.update_dashboard,
            methods=["PATCH"],
            response_model=SuccessResponse[DashboardResponse],
            summary="Обновить имя/описание дашборда",
            description="Обновляет имя и/или описание дашборда.",
            responses={
                200: {"description": "Дашборд обновлён"},
                **std,
                404: {"description": "Дашборд не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{dashboard_id}",
            self.delete_dashboard,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить дашборд",
            description="Удаляет дашборд. Доступно владельцу или admin.",
            responses={
                200: {"description": "Дашборд удалён"},
                **std,
                404: {"description": "Дашборд не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{dashboard_id}/layout",
            self.update_layout,
            methods=["PATCH"],
            response_model=SuccessResponse[DashboardResponse],
            summary="Обновить layout виджетов",
            description="Массовое обновление позиций/размеров виджетов дашборда.",
            responses={
                200: {"description": "Layout обновлён"},
                **std,
                404: {"description": "Дашборд/виджет не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{dashboard_id}/auto-refresh",
            self.set_auto_refresh,
            methods=["PATCH"],
            response_model=SuccessResponse[DashboardResponse],
            summary="Настроить авто-обновление",
            description="Включает/выключает авто-обновление дашборда и задаёт интервал.",
            responses={
                200: {"description": "Настройка обновлена"},
                **std,
                404: {"description": "Дашборд не найден", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{dashboard_id}/default",
            self.set_default,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Сделать default-дашбордом",
            description="Делает дашборд default-ом для workspace (снимает флаг с других).",
            responses={
                200: {"description": "Дашборд установлен как default"},
                **std,
                404: {"description": "Дашборд не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{dashboard_id}/share",
            self.share_dashboard,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Расшарить дашборд",
            description="Расшаривает дашборд с пользователем.",
            responses={
                200: {"description": "Дашборд расшарен"},
                **std,
                404: {"description": "Дашборд не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{dashboard_id}/share",
            self.unshare_dashboard,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Снять шаринг дашборда",
            description="Снимает шаринг дашборда с пользователя.",
            responses={
                200: {"description": "Шаринг снят"},
                **std,
                404: {"description": "Дашборд не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{dashboard_id}/widgets",
            self.add_widget,
            methods=["POST"],
            response_model=SuccessResponse[WidgetResponse],
            status_code=201,
            summary="Добавить виджет",
            description="Добавляет виджет на дашборд.",
            responses={
                201: {"description": "Виджет добавлен"},
                **std,
                404: {"description": "Дашборд не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{dashboard_id}/widgets/{widget_id}",
            self.update_widget,
            methods=["PATCH"],
            response_model=SuccessResponse[WidgetResponse],
            summary="Обновить виджет",
            description="Обновляет виджет: title/query/size/position/display_params.",
            responses={
                200: {"description": "Виджет обновлён"},
                **std,
                404: {"description": "Дашборд/виджет не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{dashboard_id}/widgets/{widget_id}",
            self.remove_widget,
            methods=["DELETE"],
            response_model=MessageResponse,
            summary="Удалить виджет",
            description="Удаляет виджет с дашборда.",
            responses={
                200: {"description": "Виджет удалён"},
                **std,
                404: {"description": "Дашборд/виджет не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/{dashboard_id}/widgets/{widget_id}/data",
            self.get_widget_data,
            methods=["GET"],
            response_model=SuccessResponse[AnalyticsResultResponse],
            summary="Данные виджета",
            description="Выполняет AnalyticsQuery виджета и возвращает результат.",
            responses={
                200: {"description": "Результат запроса"},
                **std,
                404: {"description": "Дашборд/виджет не найден", "model": ErrorResponse},
            },
        )

    # ------------------------------------------------------------------
    # Dashboard CRUD
    # ------------------------------------------------------------------

    async def create_dashboard(
        self,
        body: CreateDashboardRequest,
        caller_id: str = Depends(get_current_user_id),
        dashboard_repo=Depends(get_dashboard_repository),
        permission_checker=Depends(get_analytics_permission_checker),
        workspace_port=Depends(get_analytics_workspace_port),
        event_bus=Depends(get_analytics_event_bus),
    ) -> SuccessResponse[DashboardResponse]:
        handler = CreateDashboardHandler(
            dashboard_repo=dashboard_repo,
            permission_checker=permission_checker,
            workspace_port=workspace_port,
            event_bus=event_bus,
        )
        command = CreateDashboardCommand(
            caller_id=caller_id,
            workspace_id=body.workspace_id,
            name=body.name,
            description=body.description,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=DashboardResponse.model_validate(dto.model_dump()))

    async def list_dashboards_by_workspace(
        self,
        workspace_id: str,
        caller_id: str = Depends(get_current_user_id),
        dashboard_repo=Depends(get_dashboard_repository),
        permission_checker=Depends(get_analytics_permission_checker),
    ) -> SuccessResponse[list[DashboardResponse]]:
        handler = ListDashboardsByWorkspaceHandler(
            dashboard_repo=dashboard_repo,
            permission_checker=permission_checker,
        )
        query = ListDashboardsByWorkspaceQuery(
            caller_id=caller_id,
            workspace_id=workspace_id,
        )
        dto = await handler.handle(query)
        items = [DashboardResponse.model_validate(d.model_dump()) for d in dto.items]
        return SuccessResponse(data=items)

    async def list_dashboards_shared_with_me(
        self,
        caller_id: str = Depends(get_current_user_id),
        dashboard_repo=Depends(get_dashboard_repository),
    ) -> SuccessResponse[list[DashboardResponse]]:
        handler = ListDashboardsSharedWithMeHandler(dashboard_repo=dashboard_repo)
        query = ListDashboardsSharedWithMeQuery(caller_id=caller_id)
        dto = await handler.handle(query)
        items = [DashboardResponse.model_validate(d.model_dump()) for d in dto.items]
        return SuccessResponse(data=items)

    async def get_dashboard(
        self,
        dashboard_id: str,
        caller_id: str = Depends(get_current_user_id),
        dashboard_repo=Depends(get_dashboard_repository),
        permission_checker=Depends(get_analytics_permission_checker),
    ) -> SuccessResponse[DashboardResponse]:
        handler = GetDashboardHandler(
            dashboard_repo=dashboard_repo,
            permission_checker=permission_checker,
        )
        query = GetDashboardQuery(caller_id=caller_id, dashboard_id=dashboard_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=DashboardResponse.model_validate(dto.model_dump()))

    async def update_dashboard(
        self,
        dashboard_id: str,
        body: UpdateDashboardRequest,
        caller_id: str = Depends(get_current_user_id),
        dashboard_repo=Depends(get_dashboard_repository),
        permission_checker=Depends(get_analytics_permission_checker),
        event_bus=Depends(get_analytics_event_bus),
    ) -> SuccessResponse[DashboardResponse]:
        handler = UpdateDashboardHandler(
            dashboard_repo=dashboard_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = UpdateDashboardCommand(
            caller_id=caller_id,
            dashboard_id=dashboard_id,
            name=body.name,
            description=body.description,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=DashboardResponse.model_validate(dto.model_dump()))

    async def delete_dashboard(
        self,
        dashboard_id: str,
        caller_id: str = Depends(get_current_user_id),
        dashboard_repo=Depends(get_dashboard_repository),
        permission_checker=Depends(get_analytics_permission_checker),
        event_bus=Depends(get_analytics_event_bus),
    ) -> MessageResponse:
        handler = DeleteDashboardHandler(
            dashboard_repo=dashboard_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = DeleteDashboardCommand(
            caller_id=caller_id,
            dashboard_id=dashboard_id,
        )
        await handler.handle(command)
        return MessageResponse(data=MessageData(message="Дашборд удалён"))

    # ------------------------------------------------------------------
    # Dashboard layout / settings
    # ------------------------------------------------------------------

    async def update_layout(
        self,
        dashboard_id: str,
        body: UpdateDashboardLayoutRequest,
        caller_id: str = Depends(get_current_user_id),
        dashboard_repo=Depends(get_dashboard_repository),
        permission_checker=Depends(get_analytics_permission_checker),
        event_bus=Depends(get_analytics_event_bus),
    ) -> SuccessResponse[DashboardResponse]:
        handler = UpdateDashboardLayoutHandler(
            dashboard_repo=dashboard_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        widgets = [
            WidgetLayoutItemDTO(
                widget_id=w.widget_id,
                position=w.position,
                size=w.size,
            )
            for w in body.widgets
        ]
        command = UpdateDashboardLayoutCommand(
            caller_id=caller_id,
            dashboard_id=dashboard_id,
            widgets=widgets,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=DashboardResponse.model_validate(dto.model_dump()))

    async def set_auto_refresh(
        self,
        dashboard_id: str,
        body: SetDashboardAutoRefreshRequest,
        caller_id: str = Depends(get_current_user_id),
        dashboard_repo=Depends(get_dashboard_repository),
        permission_checker=Depends(get_analytics_permission_checker),
        event_bus=Depends(get_analytics_event_bus),
    ) -> SuccessResponse[DashboardResponse]:
        handler = SetDashboardAutoRefreshHandler(
            dashboard_repo=dashboard_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = SetDashboardAutoRefreshCommand(
            caller_id=caller_id,
            dashboard_id=dashboard_id,
            enabled=body.enabled,
            interval_seconds=body.interval_seconds,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=DashboardResponse.model_validate(dto.model_dump()))

    async def set_default(
        self,
        dashboard_id: str,
        caller_id: str = Depends(get_current_user_id),
        dashboard_repo=Depends(get_dashboard_repository),
        permission_checker=Depends(get_analytics_permission_checker),
        event_bus=Depends(get_analytics_event_bus),
    ) -> MessageResponse:
        handler = SetDefaultDashboardHandler(
            dashboard_repo=dashboard_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = SetDefaultDashboardCommand(
            caller_id=caller_id,
            dashboard_id=dashboard_id,
        )
        await handler.handle(command)
        return MessageResponse(data=MessageData(message="Дашборд установлен как default"))

    # ------------------------------------------------------------------
    # Dashboard sharing
    # ------------------------------------------------------------------

    async def share_dashboard(
        self,
        dashboard_id: str,
        body: ShareDashboardRequest,
        caller_id: str = Depends(get_current_user_id),
        dashboard_repo=Depends(get_dashboard_repository),
        permission_checker=Depends(get_analytics_permission_checker),
        event_bus=Depends(get_analytics_event_bus),
    ) -> MessageResponse:
        handler = ShareDashboardHandler(
            dashboard_repo=dashboard_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = ShareDashboardCommand(
            caller_id=caller_id,
            dashboard_id=dashboard_id,
            user_id=body.user_id,
            access_level=body.access_level.value,
        )
        await handler.handle(command)
        return MessageResponse(data=MessageData(message="Дашборд расшарен"))

    async def unshare_dashboard(
        self,
        dashboard_id: str,
        body: UnshareDashboardRequest,
        caller_id: str = Depends(get_current_user_id),
        dashboard_repo=Depends(get_dashboard_repository),
        permission_checker=Depends(get_analytics_permission_checker),
        event_bus=Depends(get_analytics_event_bus),
    ) -> MessageResponse:
        handler = UnshareDashboardHandler(
            dashboard_repo=dashboard_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = UnshareDashboardCommand(
            caller_id=caller_id,
            dashboard_id=dashboard_id,
            user_id=body.user_id,
        )
        await handler.handle(command)
        return MessageResponse(data=MessageData(message="Шаринг снят"))

    # ------------------------------------------------------------------
    # Widget CRUD
    # ------------------------------------------------------------------

    async def add_widget(
        self,
        dashboard_id: str,
        body: AddWidgetRequest,
        caller_id: str = Depends(get_current_user_id),
        dashboard_repo=Depends(get_dashboard_repository),
        permission_checker=Depends(get_analytics_permission_checker),
        event_bus=Depends(get_analytics_event_bus),
    ) -> SuccessResponse[WidgetResponse]:
        query_dto = query_request_to_dto(body.query) if body.query is not None else None
        handler = AddWidgetHandler(
            dashboard_repo=dashboard_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = AddWidgetCommand(
            caller_id=caller_id,
            dashboard_id=dashboard_id,
            title=body.title,
            widget_type=body.widget_type.value,
            query=query_dto,
            size=body.size,
            position=body.position,
            display_params=body.display_params,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=WidgetResponse.model_validate(dto.model_dump()))

    async def update_widget(
        self,
        dashboard_id: str,
        widget_id: str,
        body: UpdateWidgetRequest,
        caller_id: str = Depends(get_current_user_id),
        dashboard_repo=Depends(get_dashboard_repository),
        permission_checker=Depends(get_analytics_permission_checker),
        event_bus=Depends(get_analytics_event_bus),
    ) -> SuccessResponse[WidgetResponse]:
        query_dto = query_request_to_dto(body.query) if body.query is not None else None
        handler = UpdateWidgetHandler(
            dashboard_repo=dashboard_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = UpdateWidgetCommand(
            caller_id=caller_id,
            dashboard_id=dashboard_id,
            widget_id=widget_id,
            title=body.title,
            query=query_dto,
            size=body.size,
            position=body.position,
            display_params=body.display_params,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=WidgetResponse.model_validate(dto.model_dump()))

    async def remove_widget(
        self,
        dashboard_id: str,
        widget_id: str,
        caller_id: str = Depends(get_current_user_id),
        dashboard_repo=Depends(get_dashboard_repository),
        permission_checker=Depends(get_analytics_permission_checker),
        event_bus=Depends(get_analytics_event_bus),
    ) -> MessageResponse:
        handler = RemoveWidgetHandler(
            dashboard_repo=dashboard_repo,
            permission_checker=permission_checker,
            event_bus=event_bus,
        )
        command = RemoveWidgetCommand(
            caller_id=caller_id,
            dashboard_id=dashboard_id,
            widget_id=widget_id,
        )
        await handler.handle(command)
        return MessageResponse(data=MessageData(message="Виджет удалён"))

    async def get_widget_data(
        self,
        dashboard_id: str,
        widget_id: str,
        caller_id: str = Depends(get_current_user_id),
        dashboard_repo=Depends(get_dashboard_repository),
        query_executor=Depends(get_analytics_query_executor_port),
        permission_checker=Depends(get_analytics_permission_checker),
    ) -> SuccessResponse[AnalyticsResultResponse]:
        handler = GetWidgetDataHandler(
            dashboard_repo=dashboard_repo,
            query_executor=query_executor,
            permission_checker=permission_checker,
        )
        query = GetWidgetDataQuery(
            caller_id=caller_id,
            dashboard_id=dashboard_id,
            widget_id=widget_id,
        )
        dto = await handler.handle(query)
        return SuccessResponse(
            data=AnalyticsResultResponse.model_validate(dto.model_dump()),
        )

    # ------------------------------------------------------------------
    # Create from template
    # ------------------------------------------------------------------

    async def create_from_template(
        self,
        body: CreateDashboardFromTemplateRequest,
        caller_id: str = Depends(get_current_user_id),
        dashboard_repo=Depends(get_dashboard_repository),
        template_repo=Depends(get_dashboard_template_repository),
        permission_checker=Depends(get_analytics_permission_checker),
        workspace_port=Depends(get_analytics_workspace_port),
        event_bus=Depends(get_analytics_event_bus),
    ) -> SuccessResponse[DashboardResponse]:
        handler = CreateDashboardFromTemplateHandler(
            dashboard_repo=dashboard_repo,
            template_repo=template_repo,
            permission_checker=permission_checker,
            workspace_port=workspace_port,
            event_bus=event_bus,
        )
        command = CreateDashboardFromTemplateCommand(
            caller_id=caller_id,
            workspace_id=body.workspace_id,
            template_id=body.template_id,
            name=body.name,
            description=body.description,
        )
        dto = await handler.handle(command)
        return SuccessResponse(data=DashboardResponse.model_validate(dto.model_dump()))
