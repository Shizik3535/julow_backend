from __future__ import annotations

from app.context.analytics.application.dto.analytics_query_dto import AnalyticsResultDTO
from app.context.analytics.application.exceptions.analytics_app_exceptions import (
    UnsupportedDataSourceException,
)
from app.context.analytics.application.ports.integration.inboard.sprint_port import (
    SprintPort,
)
from app.context.analytics.application.ports.integration.inboard.task_analytics_port import (
    TaskAnalyticsPort,
)
from app.context.analytics.domain.value_objects.analytics_query import AnalyticsQuery
from app.context.analytics.domain.value_objects.bounded_context_ref import BoundedContextRef
from app.context.analytics.domain.value_objects.data_source import DataSource
from app.context.analytics.infrastructure.query_execution.analytics_bc_resolver import (
    AnalyticsBCResolver,
)
from app.context.analytics.infrastructure.query_execution.resolvers import _query_translation as qt


class TaskAnalyticsResolver(AnalyticsBCResolver):
    """Резолвер Task BC.

    Поддерживает ``TASKS``, ``TASK_STATUS_HISTORY`` (approx),
    ``SPRINTS``, ``SPRINT_BURNDOWN`` (approx), ``SPRINT_VELOCITY`` (approx).

    ``SPRINT_BURNDOWN`` — кросс-BC: даты спринта запрашиваются у
    ``SprintPort`` (Project BC), а точки burndown считаются по задачам
    через ``TaskAnalyticsPort``.
    """

    def __init__(
        self,
        task_port: TaskAnalyticsPort,
        sprint_port: SprintPort,
    ) -> None:
        self._tasks = task_port
        self._sprints = sprint_port

    @property
    def bounded_context(self) -> BoundedContextRef:
        return BoundedContextRef.TASK

    async def execute(self, query: AnalyticsQuery, workspace_id: str) -> AnalyticsResultDTO:
        ds = query.data_source
        if ds in (DataSource.TASKS, DataSource.TASK_STATUS_HISTORY):
            return await self._handle_tasks(query, workspace_id)
        if ds == DataSource.SPRINTS:
            return await self._handle_sprints(query, workspace_id)
        if ds == DataSource.SPRINT_BURNDOWN:
            return await self._handle_burndown(query, workspace_id)
        if ds == DataSource.SPRINT_VELOCITY:
            return await self._handle_velocity(query, workspace_id)
        raise UnsupportedDataSourceException(data_source=ds.value)

    # ------------------------------------------------------------------
    # TASKS / TASK_STATUS_HISTORY
    # ------------------------------------------------------------------

    async def _handle_tasks(
        self, query: AnalyticsQuery, workspace_id: str
    ) -> AnalyticsResultDTO:
        """Агрегация задач (TASKS / TASK_STATUS_HISTORY).

        Примечание: ``status_ids`` (UUID колонки статуса) и ``statuses``
        (lifecycle-статус: active/archived) применяются с AND-семантикой —
        задача должна удовлетворить обоим фильтрам одновременно.
        """
        project_ids = qt.filter_values(query.filters, "project_id")
        sprint_ids = qt.filter_values(query.filters, "sprint_id")
        epic_ids = qt.filter_values(query.filters, "epic_id")
        assignee_ids = qt.filter_values(query.filters, "assignee_id")
        status_ids = qt.filter_values(query.filters, "status_id")
        priorities = qt.filter_values(query.filters, "priority")
        task_types = qt.filter_values(query.filters, "task_type")
        statuses = qt.filter_values(query.filters, "status")
        completed = qt.filter_bool(query.filters, "completed")
        date_field = qt.filter_first(query.filters, "date_field") or "created_at"

        date_from = query.date_range.start if query.date_range else None
        date_to = query.date_range.end if query.date_range else None
        granularity = qt.time_granularity_value(query)
        group_by = qt.group_by_fields(query)

        rows = await self._tasks.count_tasks(
            workspace_id=workspace_id,
            project_ids=project_ids,
            sprint_ids=sprint_ids,
            epic_ids=epic_ids,
            assignee_ids=assignee_ids,
            status_ids=status_ids,
            priorities=priorities,
            task_types=task_types,
            statuses=statuses,
            completed=completed,
            date_field=date_field,
            date_from=date_from,
            date_to=date_to,
            granularity=granularity,
            group_by=group_by or None,
            sort=qt.sort_pairs(query) or None,
            limit=query.limit,
        )

        if group_by:
            return qt.build_result(
                query=query,
                rows=rows,
                dimension_source_keys=group_by,
                metric_source_key="count",
            )

        # No grouping: raw count result
        return qt.build_raw_result(
            query=query,
            rows=rows,
            columns=["count"],
        )

    # ------------------------------------------------------------------
    # SPRINTS
    # ------------------------------------------------------------------

    async def _handle_sprints(
        self, query: AnalyticsQuery, workspace_id: str
    ) -> AnalyticsResultDTO:
        project_ids = qt.filter_values(query.filters, "project_id")
        if not project_ids:
            # SPRINTS требует явного project_id фильтра (выйти за пределы
            # workspace мы не можем без обращения к Project BC).
            return AnalyticsResultDTO(
                data_source=query.data_source.value,
                bounded_context=query.bounded_context.value,
                columns=["id", "project_id", "name", "status", "start_date", "end_date"],
                rows=[],
                total=0,
                generated_at=qt.iso_now(),
            )

        sprint_ids = qt.filter_values(query.filters, "sprint_id") or qt.filter_values(
            query.filters, "id"
        )
        statuses = qt.filter_values(query.filters, "status")
        date_from = query.date_range.start if query.date_range else None
        date_to = query.date_range.end if query.date_range else None
        group_by = qt.group_by_fields(query)

        rows = await self._tasks.list_sprints(
            project_ids=project_ids,
            sprint_ids=sprint_ids,
            statuses=statuses,
            date_from=date_from,
            date_to=date_to,
            group_by=group_by or None,
            sort=qt.sort_pairs(query) or None,
            limit=query.limit,
        )

        if group_by:
            return qt.build_result(
                query=query,
                rows=rows,
                dimension_source_keys=group_by,
                metric_source_key="count",
            )
        return qt.build_raw_result(
            query=query,
            rows=rows,
            columns=["id", "project_id", "name", "status", "start_date", "end_date", "goal"],
        )

    # ------------------------------------------------------------------
    # SPRINT_BURNDOWN
    # ------------------------------------------------------------------

    async def _handle_burndown(
        self, query: AnalyticsQuery, workspace_id: str
    ) -> AnalyticsResultDTO:
        sprint_id = qt.filter_first(query.filters, "sprint_id")
        if not sprint_id:
            return _empty_burndown_result(query)

        meta = await self._sprints.get_sprint_meta(sprint_id)
        if meta is None or meta.sprint_start is None or meta.sprint_end is None:
            return _empty_burndown_result(query)

        # Total tasks в спринте — single count.
        total_rows = await self._tasks.count_tasks(
            workspace_id=workspace_id,
            sprint_ids=[sprint_id],
        )
        total_tasks = int(total_rows[0]["count"] or 0) if total_rows else 0

        points = await self._tasks.sprint_burndown_points(
            sprint_id=sprint_id,
            workspace_id=workspace_id,
            sprint_start=meta.sprint_start,
            sprint_end=meta.sprint_end,
            total_tasks=total_tasks,
        )
        return qt.build_raw_result(
            query=query,
            rows=points,
            columns=["date", "remaining_count", "ideal_count"],
        )

    # ------------------------------------------------------------------
    # SPRINT_VELOCITY
    # ------------------------------------------------------------------

    async def _handle_velocity(
        self, query: AnalyticsQuery, workspace_id: str
    ) -> AnalyticsResultDTO:
        project_id = qt.filter_first(query.filters, "project_id")
        if not project_id:
            return AnalyticsResultDTO(
                data_source=query.data_source.value,
                bounded_context=query.bounded_context.value,
                columns=[
                    "sprint_id",
                    "sprint_name",
                    "sprint_end",
                    "completed_count",
                    "total_count",
                ],
                rows=[],
                total=0,
                generated_at=qt.iso_now(),
            )
        last_n_raw = qt.filter_first(query.filters, "last_n_sprints")
        try:
            last_n = int(last_n_raw) if last_n_raw else 5
        except (TypeError, ValueError):
            last_n = 5
        if last_n < 1:
            last_n = 5

        rows = await self._tasks.sprint_velocity(
            workspace_id=workspace_id,
            project_id=project_id,
            last_n_sprints=last_n,
        )
        return qt.build_raw_result(
            query=query,
            rows=rows,
            columns=[
                "sprint_id",
                "sprint_name",
                "sprint_end",
                "completed_count",
                "total_count",
            ],
        )


def _empty_burndown_result(query: AnalyticsQuery) -> AnalyticsResultDTO:
    return AnalyticsResultDTO(
        data_source=query.data_source.value,
        bounded_context=query.bounded_context.value,
        columns=["date", "remaining_count", "ideal_count"],
        rows=[],
        total=0,
        generated_at=qt.iso_now(),
    )
