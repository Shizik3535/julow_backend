from __future__ import annotations

from datetime import date
from typing import Any

from app.context.analytics.application.ports.integration.inboard.task_analytics_port import (
    TaskAnalyticsPort,
)
from app.context.task.application.ports.integration.outboard.task_analytics_provider import (
    TaskAnalyticsProvider,
)


class TaskAnalyticsAdapter(TaskAnalyticsPort):
    """Inboard ``TaskAnalyticsPort``: тонкое делегирование в outboard Task BC."""

    def __init__(self, provider: TaskAnalyticsProvider) -> None:
        self._provider = provider

    async def count_tasks(
        self,
        *,
        workspace_id: str,
        project_ids: list[str] | None = None,
        sprint_ids: list[str] | None = None,
        epic_ids: list[str] | None = None,
        assignee_ids: list[str] | None = None,
        status_ids: list[str] | None = None,
        priorities: list[str] | None = None,
        task_types: list[str] | None = None,
        statuses: list[str] | None = None,
        completed: bool | None = None,
        date_field: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        granularity: str | None = None,
        group_by: list[str] | None = None,
        sort: list[tuple[str, str]] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        return await self._provider.count_tasks(
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
            group_by=group_by,
            sort=sort,
            limit=limit,
        )

    async def list_sprints(
        self,
        *,
        project_ids: list[str],
        sprint_ids: list[str] | None = None,
        statuses: list[str] | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        group_by: list[str] | None = None,
        sort: list[tuple[str, str]] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        return await self._provider.list_sprints(
            project_ids=project_ids,
            sprint_ids=sprint_ids,
            statuses=statuses,
            date_from=date_from,
            date_to=date_to,
            group_by=group_by,
            sort=sort,
            limit=limit,
        )

    async def sprint_burndown_points(
        self,
        *,
        sprint_id: str,
        workspace_id: str,
        sprint_start: date,
        sprint_end: date,
        total_tasks: int | None = None,
    ) -> list[dict[str, Any]]:
        return await self._provider.sprint_burndown_points(
            sprint_id=sprint_id,
            workspace_id=workspace_id,
            sprint_start=sprint_start,
            sprint_end=sprint_end,
            total_tasks=total_tasks,
        )

    async def sprint_velocity(
        self,
        *,
        workspace_id: str,
        project_id: str,
        last_n_sprints: int = 5,
    ) -> list[dict[str, Any]]:
        return await self._provider.sprint_velocity(
            workspace_id=workspace_id,
            project_id=project_id,
            last_n_sprints=last_n_sprints,
        )

    async def project_progress_counts(
        self,
        *,
        workspace_id: str,
        project_ids: list[str],
        overdue_date: date | None = None,
    ) -> list[dict[str, Any]]:
        return await self._provider.project_progress_counts(
            workspace_id=workspace_id,
            project_ids=project_ids,
            overdue_date=overdue_date,
        )
