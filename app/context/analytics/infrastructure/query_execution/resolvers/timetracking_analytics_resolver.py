from __future__ import annotations

from app.context.analytics.application.dto.analytics_query_dto import AnalyticsResultDTO
from app.context.analytics.application.exceptions.analytics_app_exceptions import (
    UnsupportedDataSourceException,
)
from app.context.analytics.application.ports.integration.inboard.timetracking_analytics_port import (
    TimeTrackingAnalyticsPort,
)
from app.context.analytics.domain.value_objects.analytics_query import AnalyticsQuery
from app.context.analytics.domain.value_objects.bounded_context_ref import BoundedContextRef
from app.context.analytics.domain.value_objects.data_source import DataSource
from app.context.analytics.domain.value_objects.metric_aggregation import MetricAggregation
from app.context.analytics.infrastructure.query_execution.analytics_bc_resolver import (
    AnalyticsBCResolver,
)
from app.context.analytics.infrastructure.query_execution.resolvers import _query_translation as qt


class TimeTrackingAnalyticsResolver(AnalyticsBCResolver):
    """Резолвер TimeTracking BC. Поддерживает ``TIME_ENTRIES`` и ``WORKLOAD``."""

    def __init__(self, timetracking_port: TimeTrackingAnalyticsPort) -> None:
        self._port = timetracking_port

    @property
    def bounded_context(self) -> BoundedContextRef:
        return BoundedContextRef.TIMETRACKING

    async def execute(self, query: AnalyticsQuery, workspace_id: str) -> AnalyticsResultDTO:
        if query.data_source == DataSource.TIME_ENTRIES:
            return await self._handle_time_entries(query, workspace_id)
        if query.data_source == DataSource.WORKLOAD:
            return await self._handle_workload(query, workspace_id)
        raise UnsupportedDataSourceException(data_source=query.data_source.value)

    async def _handle_time_entries(
        self, query: AnalyticsQuery, workspace_id: str
    ) -> AnalyticsResultDTO:
        user_ids = qt.filter_values(query.filters, "user_id")
        project_ids = qt.filter_values(query.filters, "project_id")
        task_ids = qt.filter_values(query.filters, "task_id")
        epic_ids = qt.filter_values(query.filters, "epic_id")
        category_ids = qt.filter_values(query.filters, "category_id")
        is_billable = qt.filter_bool(query.filters, "is_billable")
        statuses = qt.filter_values(query.filters, "status")

        date_from = query.date_range.start if query.date_range else None
        date_to = query.date_range.end if query.date_range else None
        granularity = qt.time_granularity_value(query)
        group_by = qt.group_by_fields(query)

        # Метрика → имя метода провайдера.
        metric_name = "count"
        if query.metrics:
            m = query.metrics[0]
            if m.aggregation == MetricAggregation.SUM and m.field == "duration_seconds":
                metric_name = "sum_duration"
            elif m.aggregation == MetricAggregation.AVG and m.field == "duration_seconds":
                metric_name = "avg_duration"
            elif m.aggregation == MetricAggregation.SUM and m.field in (
                "billable_amount",
                "duration_billable_seconds",
            ):
                metric_name = "sum_billable"
            else:
                metric_name = "count"

        rows = await self._port.time_entry_aggregates(
            workspace_id=workspace_id,
            user_ids=user_ids,
            project_ids=project_ids,
            task_ids=task_ids,
            epic_ids=epic_ids,
            category_ids=category_ids,
            is_billable=is_billable,
            statuses=statuses,
            date_from=date_from,
            date_to=date_to,
            granularity=granularity,
            group_by=group_by or None,
            metric=metric_name,
            sort=qt.sort_pairs(query) or None,
            limit=query.limit,
        )

        if group_by:
            return qt.build_result(
                query=query,
                rows=rows,
                dimension_source_keys=group_by,
                metric_source_key=metric_name,
            )
        return qt.build_raw_result(
            query=query,
            rows=rows,
            columns=[metric_name],
        )

    async def _handle_workload(
        self, query: AnalyticsQuery, workspace_id: str
    ) -> AnalyticsResultDTO:
        if query.date_range is None:
            # Без диапазона WORKLOAD считать нельзя (нужно для GENERATE_SERIES
            # дат на стороне SQL). Возвращаем пустой результат.
            return qt.build_raw_result(
                query=query,
                rows=[],
                columns=["user_id", "date_bucket", "total_duration_seconds"],
            )

        granularity = qt.time_granularity_value(query) or "day"
        user_ids = qt.filter_values(query.filters, "user_id")
        project_ids = qt.filter_values(query.filters, "project_id")

        rows = await self._port.workload_by_user(
            workspace_id=workspace_id,
            user_ids=user_ids,
            project_ids=project_ids,
            date_from=query.date_range.start,
            date_to=query.date_range.end,
            granularity=granularity,
        )
        return qt.build_raw_result(
            query=query,
            rows=rows,
            columns=["user_id", "date_bucket", "total_duration_seconds"],
        )
