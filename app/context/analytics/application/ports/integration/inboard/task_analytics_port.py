from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Any


class TaskAnalyticsPort(ABC):
    """
    Inboard-порт Analytics BC: агрегационные данные задач и спринт-метрики.

    Зеркало ``TaskAnalyticsProvider`` (outboard Task BC).
    """

    @abstractmethod
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
        """См. ``TaskAnalyticsProvider.count_tasks``."""

    @abstractmethod
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
        """См. ``TaskAnalyticsProvider.list_sprints``."""

    @abstractmethod
    async def sprint_burndown_points(
        self,
        *,
        sprint_id: str,
        workspace_id: str,
        sprint_start: date,
        sprint_end: date,
        total_tasks: int | None = None,
    ) -> list[dict[str, Any]]:
        """См. ``TaskAnalyticsProvider.sprint_burndown_points``."""

    @abstractmethod
    async def sprint_velocity(
        self,
        *,
        workspace_id: str,
        project_id: str,
        last_n_sprints: int = 5,
    ) -> list[dict[str, Any]]:
        """См. ``TaskAnalyticsProvider.sprint_velocity``."""

    @abstractmethod
    async def project_progress_counts(
        self,
        *,
        workspace_id: str,
        project_ids: list[str],
        overdue_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """См. ``TaskAnalyticsProvider.project_progress_counts``."""
