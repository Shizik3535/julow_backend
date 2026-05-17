from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Any


class ProjectAnalyticsProvider(ABC):
    """
    Outboard-порт: агрегационные данные проектов для Analytics BC.

    Реализуется в infrastructure-слое Project BC. Возвращает плоские
    табличные строки (``list[dict[str, Any]]``). Резолвер Analytics BC
    переименовывает ключи в alias-ы из ``AnalyticsQuery``.

    PROJECT_PROGRESS требует кросс-BC композиции (project meta + task
    counts) — здесь отдаётся только ``project meta``, а агрегация задач
    подмешивается в ``ProjectAnalyticsResolver`` через ``TaskAnalyticsPort``.
    """

    # ---- PROJECTS ----

    @abstractmethod
    async def list_projects(
        self,
        *,
        workspace_id: str,
        project_ids: list[str] | None = None,
        statuses: list[str] | None = None,
        visibilities: list[str] | None = None,
        methodologies: list[str] | None = None,
        date_field: str | None = None,  # created_at / start_date / deadline
        date_from: date | None = None,
        date_to: date | None = None,
        granularity: str | None = None,  # day/week/month/quarter/year
        group_by: list[str] | None = None,
        sort: list[tuple[str, str]] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Вернуть список/агрегацию проектов в рамках workspace.

        Поддерживаемые поля группировки: ``status``, ``visibility``,
        ``methodology``, ``category_name``, ``date_bucket`` (при заданном
        ``granularity``+``date_field``).
        Поддерживаемые поля сортировки: те же, что у группировки, плюс
        ``count``.

        Возвращает строки с фиксированными ключами:
            - без ``group_by`` — ``id``, ``name``, ``status``, ``visibility``,
              ``methodology``, ``start_date``, ``deadline``, ``created_at``,
              ``workspace_id``;
            - с ``group_by`` — ключи из ``group_by`` + ``count``.
        """

    # ---- PROJECT_PROGRESS ----

    @abstractmethod
    async def project_summaries(
        self,
        *,
        workspace_id: str,
        project_ids: list[str] | None = None,
        statuses: list[str] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Вернуть метаданные проектов для построения PROJECT_PROGRESS.

        Резолвер дополнит результат счётчиками задач через
        ``TaskAnalyticsPort``.

        Возвращает строки с ключами: ``project_id``, ``name``, ``status``,
        ``start_date``, ``deadline``, ``methodology``.
        """
