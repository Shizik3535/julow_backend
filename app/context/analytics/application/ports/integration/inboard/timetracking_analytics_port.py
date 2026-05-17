from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Any


class TimeTrackingAnalyticsPort(ABC):
    """
    Inboard-порт Analytics BC: агрегационные данные трудозатрат.

    Зеркало ``TimeTrackingAnalyticsProvider`` (outboard TimeTracking BC).
    """

    @abstractmethod
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
        """См. ``TimeTrackingAnalyticsProvider.time_entry_aggregates``."""

    @abstractmethod
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
        """См. ``TimeTrackingAnalyticsProvider.workload_by_user``."""
