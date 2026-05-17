from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Any


class ProjectAnalyticsPort(ABC):
    """
    Inboard-порт Analytics BC: агрегационные данные проектов.

    Зеркало ``ProjectAnalyticsProvider`` (outboard Project BC).
    """

    @abstractmethod
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
        """См. ``ProjectAnalyticsProvider.list_projects``."""

    @abstractmethod
    async def project_summaries(
        self,
        *,
        workspace_id: str,
        project_ids: list[str] | None = None,
        statuses: list[str] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """См. ``ProjectAnalyticsProvider.project_summaries``."""
