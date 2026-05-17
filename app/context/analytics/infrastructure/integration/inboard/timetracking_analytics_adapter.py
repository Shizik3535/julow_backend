from __future__ import annotations

from datetime import date
from typing import Any

from app.context.analytics.application.ports.integration.inboard.timetracking_analytics_port import (
    TimeTrackingAnalyticsPort,
)
from app.context.timetracking.application.ports.integration.outboard.timetracking_analytics_provider import (
    TimeTrackingAnalyticsProvider,
)


class TimeTrackingAnalyticsAdapter(TimeTrackingAnalyticsPort):
    """Inboard ``TimeTrackingAnalyticsPort``: тонкое делегирование в outboard TimeTracking BC."""

    def __init__(self, provider: TimeTrackingAnalyticsProvider) -> None:
        self._provider = provider

    async def time_entry_aggregates(
        self,
        *,
        workspace_id: str,
        user_ids: list[str] | None = None,
        project_ids: list[str] | None = None,
        task_ids: list[str] | None = None,
        epic_ids: list[str] | None = None,
        category_ids: list[str] | None = None,
        is_billable: bool | None = None,
        statuses: list[str] | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        granularity: str | None = None,
        group_by: list[str] | None = None,
        metric: str = "count",
        sort: list[tuple[str, str]] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        return await self._provider.time_entry_aggregates(
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
            group_by=group_by,
            metric=metric,
            sort=sort,
            limit=limit,
        )

    async def workload_by_user(
        self,
        *,
        workspace_id: str,
        user_ids: list[str] | None = None,
        project_ids: list[str] | None = None,
        date_from: date,
        date_to: date,
        granularity: str = "day",
    ) -> list[dict[str, Any]]:
        return await self._provider.workload_by_user(
            workspace_id=workspace_id,
            user_ids=user_ids,
            project_ids=project_ids,
            date_from=date_from,
            date_to=date_to,
            granularity=granularity,
        )
