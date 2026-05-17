from __future__ import annotations

from typing import Any

from app.context.analytics.application.ports.integration.inboard.workspace_analytics_port import (
    WorkspaceAnalyticsPort,
)
from app.context.workspace.application.ports.integration.outboard.workspace_analytics_provider import (
    WorkspaceAnalyticsProvider,
)


class WorkspaceAnalyticsAdapter(WorkspaceAnalyticsPort):
    """Inboard ``WorkspaceAnalyticsPort``: тонкое делегирование в outboard Workspace BC."""

    def __init__(self, provider: WorkspaceAnalyticsProvider) -> None:
        self._provider = provider

    async def list_workspaces(
        self,
        *,
        workspace_ids: list[str] | None = None,
        organization_id: str | None = None,
        statuses: list[str] | None = None,
        types: list[str] | None = None,
        group_by: list[str] | None = None,
        sort: list[tuple[str, str]] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        return await self._provider.list_workspaces(
            workspace_ids=workspace_ids,
            organization_id=organization_id,
            statuses=statuses,
            types=types,
            group_by=group_by,
            sort=sort,
            limit=limit,
        )
