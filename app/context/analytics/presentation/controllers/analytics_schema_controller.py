"""Endpoint'ы метаданных Analytics-схемы.

Позволяют клиенту программно узнать:
    - какие ``DataSource`` доступны;
    - какие поля у каждого источника (для фильтров/группировки/сортировки);
    - какие операторы / агрегации / гранулярности существуют.

Авторизация: достаточно факта аутентификации — это публичные
метаданные движка, не клиентские данные.
"""
from __future__ import annotations

from fastapi import Depends

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import ErrorResponse, SuccessResponse

from app.context.analytics.application.ports.schema.analytics_schema_port import (
    AnalyticsSchemaPort,
)
from app.context.analytics.application.queries.get_analytics_schema import (
    GetDataSourceSchemaHandler,
    GetDataSourceSchemaQuery,
    GetFullSchemaHandler,
    GetFullSchemaQuery,
    ListDataSourcesHandler,
    ListDataSourcesQuery,
)

from app.context.analytics.presentation.dependencies import (
    get_analytics_schema_port,
    get_current_user_id,
)
from app.context.analytics.application.dto.analytics_schema_dto import (
    AnalyticsSchemaDTO,
    DataSourceSchemaDTO,
    DataSourceSummaryDTO,
)
from app.context.analytics.presentation.schemas.responses.analytics_schema_responses import (
    AnalyticsSchemaResponse,
    DataSourceSchemaResponse,
    DataSourceSummaryResponse,
)


class AnalyticsSchemaController(BaseController):
    """Контроллер метаданных Analytics-схемы.

    Endpoint'ы:
        GET /analytics/schema                      — Полный реестр
        GET /analytics/data-sources                — Краткий список DataSource
        GET /analytics/data-sources/{data_source}  — Полная схема одного источника
    """

    def __init__(self) -> None:
        super().__init__(prefix="/analytics", tags=["Analytics — Schema"])

    def _register_routes(self) -> None:
        std = {
            401: {"description": "Не аутентифицирован", "model": ErrorResponse},
        }
        self._router.add_api_route(
            "/schema",
            self.get_schema,
            methods=["GET"],
            response_model=SuccessResponse[AnalyticsSchemaResponse],
            summary="Полный реестр Analytics-схемы",
            description=(
                "Возвращает все поддерживаемые DataSource (с описанием полей)"
                " плюс глобальные enum'ы: filter_operators, aggregations,"
                " time_granularities, sort_orders, widget_types."
            ),
            responses={200: {"description": "Реестр"}, **std},
        )
        self._router.add_api_route(
            "/data-sources",
            self.list_data_sources,
            methods=["GET"],
            response_model=SuccessResponse[list[DataSourceSummaryResponse]],
            summary="Список поддерживаемых DataSource",
            description="Краткое описание каждого источника без детализации полей.",
            responses={200: {"description": "Список"}, **std},
        )
        self._router.add_api_route(
            "/data-sources/{data_source}",
            self.get_data_source_schema,
            methods=["GET"],
            response_model=SuccessResponse[DataSourceSchemaResponse],
            summary="Схема одного DataSource",
            description=(
                "Поля, поддерживаемые агрегации и шаблонные метрики для"
                " указанного источника."
            ),
            responses={
                200: {"description": "Схема DataSource"},
                404: {"description": "DataSource не поддержан", "model": ErrorResponse},
                **std,
            },
        )

    async def get_schema(
        self,
        _caller_id: str = Depends(get_current_user_id),
        schema_port: AnalyticsSchemaPort = Depends(get_analytics_schema_port),
    ) -> SuccessResponse[AnalyticsSchemaResponse]:
        handler = GetFullSchemaHandler(schema_port=schema_port)
        query = GetFullSchemaQuery()
        dto = await handler.handle(query)
        return SuccessResponse(
            data=AnalyticsSchemaResponse.model_validate(dto.model_dump())
        )

    async def list_data_sources(
        self,
        _caller_id: str = Depends(get_current_user_id),
        schema_port: AnalyticsSchemaPort = Depends(get_analytics_schema_port),
    ) -> SuccessResponse[list[DataSourceSummaryResponse]]:
        handler = ListDataSourcesHandler(schema_port=schema_port)
        query = ListDataSourcesQuery()
        dto = await handler.handle(query)
        return SuccessResponse(
            data=[
                DataSourceSummaryResponse.model_validate(item.model_dump())
                for item in dto.items
            ]
        )

    async def get_data_source_schema(
        self,
        data_source: str,
        _caller_id: str = Depends(get_current_user_id),
        schema_port: AnalyticsSchemaPort = Depends(get_analytics_schema_port),
    ) -> SuccessResponse[DataSourceSchemaResponse]:
        handler = GetDataSourceSchemaHandler(schema_port=schema_port)
        query = GetDataSourceSchemaQuery(data_source=data_source)
        dto = await handler.handle(query)
        return SuccessResponse(
            data=DataSourceSchemaResponse.model_validate(dto.model_dump())
        )
