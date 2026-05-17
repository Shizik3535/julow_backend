from __future__ import annotations

from app.context.analytics.application.dto.analytics_query_dto import AnalyticsResultDTO
from app.context.analytics.application.exceptions.analytics_app_exceptions import (
    UnsupportedDataSourceException,
)
from app.context.analytics.application.ports.integration.inboard.workspace_analytics_port import (
    WorkspaceAnalyticsPort,
)
from app.context.analytics.domain.value_objects.analytics_query import AnalyticsQuery
from app.context.analytics.domain.value_objects.bounded_context_ref import BoundedContextRef
from app.context.analytics.domain.value_objects.data_source import DataSource
from app.context.analytics.infrastructure.query_execution.analytics_bc_resolver import (
    AnalyticsBCResolver,
)
from app.context.analytics.infrastructure.query_execution.resolvers import _query_translation as qt


class WorkspaceAnalyticsResolver(AnalyticsBCResolver):
    """Резолвер Workspace BC. Поддерживает ``DataSource.WORKSPACES``."""

    def __init__(self, workspace_port: WorkspaceAnalyticsPort) -> None:
        self._port = workspace_port

    @property
    def bounded_context(self) -> BoundedContextRef:
        return BoundedContextRef.WORKSPACE

    async def execute(self, query: AnalyticsQuery, workspace_id: str) -> AnalyticsResultDTO:
        if query.data_source == DataSource.WORKSPACES:
            return await self._handle_workspaces(query, workspace_id)
        raise UnsupportedDataSourceException(data_source=query.data_source.value)

    async def _handle_workspaces(
        self, query: AnalyticsQuery, workspace_id: str
    ) -> AnalyticsResultDTO:
        # Фильтры
        ws_ids_filter = qt.filter_values(query.filters, "workspace_id") or qt.filter_values(
            query.filters, "id"
        )
        # Если вызывающий слой передал явный workspace — сужаемся к нему,
        # чтобы дашборд не утёк за границы своего пространства.
        if workspace_id and not ws_ids_filter:
            ws_ids_filter = [workspace_id]

        org_id = qt.filter_first(query.filters, "organization_id")
        statuses = qt.filter_values(query.filters, "status")
        types = qt.filter_values(query.filters, "workspace_type")

        # Группировка: workspace не поддерживает time-series —
        # если измерение с time_granularity задано, сразу отказываем.
        if any(d.time_granularity is not None for d in query.dimensions):
            raise UnsupportedDataSourceException(
                data_source=f"{query.data_source.value}+time_granularity"
            )
        group_by = [d.field for d in query.dimensions]
        limit = query.limit

        rows = await self._port.list_workspaces(
            workspace_ids=ws_ids_filter,
            organization_id=org_id,
            statuses=statuses,
            types=types,
            group_by=group_by or None,
            sort=qt.sort_pairs(query) or None,
            limit=limit,
        )

        if group_by:
            return qt.build_result(
                query=query,
                rows=rows,
                dimension_source_keys=group_by,
                metric_source_key="count",
            )

        # Без group_by — «сырой» табличный результат.
        columns = ["id", "name", "status", "workspace_type", "organization_id", "created_at"]
        return qt.build_raw_result(query=query, rows=rows, columns=columns)
