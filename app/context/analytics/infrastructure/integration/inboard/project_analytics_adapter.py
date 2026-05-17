from __future__ import annotations

from datetime import date
from typing import Any

from app.context.analytics.application.ports.integration.inboard.project_analytics_port import (
    ProjectAnalyticsPort,
)
from app.context.project.application.ports.integration.outboard.project_analytics_provider import (
    ProjectAnalyticsProvider,
)


class ProjectAnalyticsAdapter(ProjectAnalyticsPort):
    """Inboard ``ProjectAnalyticsPort``: тонкое делегирование в outboard Project BC."""

    def __init__(self, provider: ProjectAnalyticsProvider) -> None:
        self._provider = provider

    async def list_projects(
        self,
        *,
        workspace_id: str,
        project_ids: list[str] | None = None,
        statuses: list[str] | None = None,
        visibilities: list[str] | None = None,
        methodologies: list[str] | None = None,
        date_field: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        granularity: str | None = None,
        group_by: list[str] | None = None,
        sort: list[tuple[str, str]] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        return await self._provider.list_projects(
            workspace_id=workspace_id,
            project_ids=project_ids,
            statuses=statuses,
            visibilities=visibilities,
            methodologies=methodologies,
            date_field=date_field,
            date_from=date_from,
            date_to=date_to,
            granularity=granularity,
            group_by=group_by,
            sort=sort,
            limit=limit,
        )

    async def project_summaries(
        self,
        *,
        workspace_id: str,
        project_ids: list[str] | None = None,
        statuses: list[str] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        return await self._provider.project_summaries(
            workspace_id=workspace_id,
            project_ids=project_ids,
            statuses=statuses,
            limit=limit,
        )
