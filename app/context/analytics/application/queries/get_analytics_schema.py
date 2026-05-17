"""Queries: получить метаданные Analytics-схемы.

Endpoint'ы ``/analytics/schema``, ``/analytics/data-sources`` и
``/analytics/data-sources/{source}`` отвечают на разные части одного
реестра. Каждый endpoint — отдельный query/handler для типобезопасности.
"""
from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler

from app.context.analytics.application.dto.analytics_schema_dto import (
    AnalyticsSchemaDTO,
    DataSourceListDTO,
    DataSourceSchemaDTO,
)
from app.context.analytics.application.ports.schema.analytics_schema_port import (
    AnalyticsSchemaPort,
)
from app.shared.domain.exceptions.entity_not_found_exception import (
    EntityNotFoundException,
)


# ---------------------------------------------------------------------------
# GET /analytics/schema — полный реестр
# ---------------------------------------------------------------------------


class GetFullSchemaQuery(BaseQuery):
    """Запрос полного реестра Analytics-схемы."""


class GetFullSchemaHandler(BaseQueryHandler[GetFullSchemaQuery, AnalyticsSchemaDTO]):
    """Возвращает полный реестр Analytics-схемы через ``AnalyticsSchemaPort``."""

    def __init__(self, schema_port: AnalyticsSchemaPort) -> None:
        super().__init__()
        self._port = schema_port

    async def handle(self, query: GetFullSchemaQuery) -> AnalyticsSchemaDTO:
        return self._port.get_full_schema()


# ---------------------------------------------------------------------------
# GET /analytics/data-sources — краткий список DataSource
# ---------------------------------------------------------------------------


class ListDataSourcesQuery(BaseQuery):
    """Запрос краткого списка DataSource."""


class ListDataSourcesHandler(BaseQueryHandler[ListDataSourcesQuery, DataSourceListDTO]):
    """Возвращает краткий список DataSource через ``AnalyticsSchemaPort``."""

    def __init__(self, schema_port: AnalyticsSchemaPort) -> None:
        super().__init__()
        self._port = schema_port

    async def handle(self, query: ListDataSourcesQuery) -> DataSourceListDTO:
        return DataSourceListDTO(items=self._port.list_data_sources())


# ---------------------------------------------------------------------------
# GET /analytics/data-sources/{data_source} — схема одного DataSource
# ---------------------------------------------------------------------------


class GetDataSourceSchemaQuery(BaseQuery):
    """Запрос схемы одного DataSource.

    Атрибуты:
        data_source: ``DataSource.value`` для поиска.
    """

    data_source: str


class GetDataSourceSchemaHandler(
    BaseQueryHandler[GetDataSourceSchemaQuery, DataSourceSchemaDTO]
):
    """Возвращает схему одного DataSource через ``AnalyticsSchemaPort``."""

    def __init__(self, schema_port: AnalyticsSchemaPort) -> None:
        super().__init__()
        self._port = schema_port

    async def handle(self, query: GetDataSourceSchemaQuery) -> DataSourceSchemaDTO:
        dto = self._port.get_data_source_schema(query.data_source)
        if dto is None:
            raise EntityNotFoundException(
                entity_type="DataSourceSchema", id=query.data_source
            )
        return dto
