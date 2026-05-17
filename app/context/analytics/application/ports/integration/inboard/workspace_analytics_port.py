from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class WorkspaceAnalyticsPort(ABC):
    """
    Inboard-порт Analytics BC: агрегационные данные workspace.

    Контракт зеркалит ``WorkspaceAnalyticsProvider`` (outboard Workspace BC).
    Инфраструктурный адаптер Analytics делегирует вызовы напрямую.
    Резолверы Analytics зависят только от этого порта.
    """

    @abstractmethod
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
        """См. ``WorkspaceAnalyticsProvider.list_workspaces``."""
