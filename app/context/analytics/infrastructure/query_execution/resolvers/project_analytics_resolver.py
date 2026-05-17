from __future__ import annotations

from datetime import date as date_type

from app.context.analytics.application.dto.analytics_query_dto import (
    AnalyticsResultDTO,
    AnalyticsResultRowDTO,
)
from app.context.analytics.application.exceptions.analytics_app_exceptions import (
    UnsupportedDataSourceException,
)
from app.context.analytics.application.ports.integration.inboard.project_analytics_port import (
    ProjectAnalyticsPort,
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
from app.core.logging import get_logger

_logger = get_logger(__name__)


class ProjectAnalyticsResolver(AnalyticsBCResolver):
    """Резолвер Project BC. Поддерживает ``PROJECTS`` и ``PROJECT_PROGRESS``.

    ``PROJECT_PROGRESS`` — кросс-BC: project meta берётся из Project BC,
    а task-counts из Task BC через ``TaskAnalyticsPort``.
    """

    def __init__(
        self,
        project_port: ProjectAnalyticsPort,
        task_port: TaskAnalyticsPort,
    ) -> None:
        self._projects = project_port
        self._tasks = task_port

    @property
    def bounded_context(self) -> BoundedContextRef:
        return BoundedContextRef.PROJECT

    async def execute(self, query: AnalyticsQuery, workspace_id: str) -> AnalyticsResultDTO:
        if query.data_source == DataSource.PROJECTS:
            return await self._handle_projects(query, workspace_id)
        if query.data_source == DataSource.PROJECT_PROGRESS:
            return await self._handle_progress(query, workspace_id)
        raise UnsupportedDataSourceException(data_source=query.data_source.value)

    async def _handle_projects(
        self, query: AnalyticsQuery, workspace_id: str
    ) -> AnalyticsResultDTO:
        project_ids = qt.filter_values(query.filters, "project_id") or qt.filter_values(
            query.filters, "id"
        )
        statuses = qt.filter_values(query.filters, "status")
        visibilities = qt.filter_values(query.filters, "visibility")
        methodologies = qt.filter_values(query.filters, "methodology")
        date_field = qt.filter_first(query.filters, "date_field") or "created_at"

        group_by = qt.group_by_fields(query)
        granularity = qt.time_granularity_value(query)

        date_from = query.date_range.start if query.date_range else None
        date_to = query.date_range.end if query.date_range else None

        rows = await self._projects.list_projects(
            workspace_id=workspace_id,
            project_ids=project_ids,
            statuses=statuses,
            visibilities=visibilities,
            methodologies=methodologies,
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

        columns = [
            "id",
            "name",
            "status",
            "visibility",
            "methodology",
            "start_date",
            "deadline",
            "created_at",
            "workspace_id",
        ]
        return qt.build_raw_result(query=query, rows=rows, columns=columns)

    async def _handle_progress(
        self, query: AnalyticsQuery, workspace_id: str
    ) -> AnalyticsResultDTO:
        """Композиция Project meta × Task counts.

        Возвращает по проекту: total / completed / overdue counts +
        progress_percent.

        Примечание: ``query.date_range`` намеренно игнорируется —
        PROJECT_PROGRESS отражает текущий снапшот прогресса, а не
        историческую динамику.
        """
        project_ids_filter = qt.filter_values(query.filters, "project_id")
        statuses = qt.filter_values(query.filters, "status")

        # Предупредить о проигнорированных фильтрах.
        _ignored = [f.field for f in query.filters
                    if f.field not in ("project_id", "status")]
        if _ignored:
            _logger.warning(
                "PROJECT_PROGRESS: filters ignored",
                ignored_fields=_ignored,
            )
        if query.date_range:
            _logger.warning(
                "PROJECT_PROGRESS: date_range ignored — progress is a current snapshot",
            )

        summaries = await self._projects.project_summaries(
            workspace_id=workspace_id,
            project_ids=project_ids_filter,
            statuses=statuses,
            limit=query.limit,
        )
        if not summaries:
            return _empty_progress_result(query)

        project_ids = [s["project_id"] for s in summaries]

        # Один запрос с условной агрегацией вместо трёх отдельных.
        today = date_type.today()
        count_rows = await self._tasks.project_progress_counts(
            workspace_id=workspace_id,
            project_ids=project_ids,
            overdue_date=today,
        )
        counts_by_project: dict[str, dict[str, int]] = {
            r["project_id"]: {
                "total": r["total_count"],
                "completed": r["completed_count"],
                "overdue": r["overdue_count"],
            }
            for r in count_rows
        }

        rows: list[AnalyticsResultRowDTO] = []
        for s in summaries:
            pid = str(s["project_id"])
            counts = counts_by_project.get(pid, {"total": 0, "completed": 0, "overdue": 0})
            total = counts["total"]
            completed = counts["completed"]
            overdue = counts["overdue"]
            progress_percent = round((completed / total) * 100, 1) if total > 0 else 0.0
            rows.append(
                AnalyticsResultRowDTO(
                    values={
                        "project_id": pid,
                        "name": s.get("name"),
                        "status": s.get("status"),
                        "start_date": s.get("start_date"),
                        "deadline": s.get("deadline"),
                        "total_count": total,
                        "completed_count": completed,
                        "overdue_count": overdue,
                        "progress_percent": progress_percent,
                    }
                )
            )

        return AnalyticsResultDTO(
            data_source=query.data_source.value,
            bounded_context=query.bounded_context.value,
            columns=[
                "project_id",
                "name",
                "status",
                "start_date",
                "deadline",
                "total_count",
                "completed_count",
                "overdue_count",
                "progress_percent",
            ],
            rows=rows,
            total=len(rows),
            generated_at=qt.iso_now(),
        )


def _empty_progress_result(query: AnalyticsQuery) -> AnalyticsResultDTO:
    return AnalyticsResultDTO(
        data_source=query.data_source.value,
        bounded_context=query.bounded_context.value,
        columns=[
            "project_id",
            "name",
            "status",
            "start_date",
            "deadline",
            "total_count",
            "completed_count",
            "overdue_count",
            "progress_percent",
        ],
        rows=[],
        total=0,
        generated_at=qt.iso_now(),
    )
