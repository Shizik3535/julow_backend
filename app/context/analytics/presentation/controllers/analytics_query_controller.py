from __future__ import annotations

from fastapi import Depends

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import (
    ErrorResponse,
    SuccessResponse,
)

from app.context.analytics.application.queries.execute_analytics_query import (
    ExecuteAnalyticsQueryHandler,
    ExecuteAnalyticsQueryQuery,
)

from app.context.analytics.presentation.dependencies import (
    get_analytics_permission_checker,
    get_analytics_query_executor_port,
    get_analytics_workspace_port,
    get_current_user_id,
)
from app.context.analytics.presentation.schemas.requests.analytics_requests import (
    ExecuteAnalyticsQueryRequest,
)
from app.context.analytics.presentation.schemas.requests.query_mapper import query_request_to_dto
from app.context.analytics.presentation.schemas.responses.analytics_responses import (
    AnalyticsResultResponse,
)


class AnalyticsQueryController(BaseController):
    """
    Контроллер ad-hoc аналитических запросов.

    Endpoint'ы:
        POST /execute  — Выполнить аналитический запрос
    """

    def __init__(self) -> None:
        super().__init__(prefix="/analytics", tags=["Analytics — Queries"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/execute",
            self.execute_query,
            methods=["POST"],
            response_model=SuccessResponse[AnalyticsResultResponse],
            summary="Выполнить аналитический запрос",
            description="Ad-hoc выполнение AnalyticsQuery (preview / ad-hoc-аналитика).",
            responses={
                200: {"description": "Результат запроса"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                403: {"description": "Недостаточно прав", "model": ErrorResponse},
                404: {"description": "Workspace не найден", "model": ErrorResponse},
                501: {"description": "Источник данных не поддерживается", "model": ErrorResponse},
            },
        )

    async def execute_query(
        self,
        workspace_id: str,
        body: ExecuteAnalyticsQueryRequest,
        caller_id: str = Depends(get_current_user_id),
        query_executor=Depends(get_analytics_query_executor_port),
        permission_checker=Depends(get_analytics_permission_checker),
        workspace_port=Depends(get_analytics_workspace_port),
    ) -> SuccessResponse[AnalyticsResultResponse]:
        query_dto = query_request_to_dto(body.query)

        handler = ExecuteAnalyticsQueryHandler(
            query_executor=query_executor,
            permission_checker=permission_checker,
            workspace_port=workspace_port,
        )
        query = ExecuteAnalyticsQueryQuery(
            caller_id=caller_id,
            workspace_id=workspace_id,
            query=query_dto,
        )
        dto = await handler.handle(query)
        return SuccessResponse(
            data=AnalyticsResultResponse.model_validate(dto.model_dump()),
        )
