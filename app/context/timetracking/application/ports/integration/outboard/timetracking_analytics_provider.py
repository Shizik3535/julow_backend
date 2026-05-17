from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Any


class TimeTrackingAnalyticsProvider(ABC):
    """
    Outboard-порт: агрегационные данные трудозатрат для Analytics BC.

    Реализуется в infrastructure-слое TimeTracking BC. Возвращает плоские
    табличные строки (``list[dict[str, Any]]``); резолвер Analytics
    переименовывает ключи в alias-ы из ``AnalyticsQuery``.

    Покрывает DataSource'ы TimeTracking BC из spec: ``TIME_ENTRIES``,
    ``WORKLOAD``.
    """

    # ---- TIME_ENTRIES ----

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
        granularity: str | None = None,  # day/week/month/quarter/year
        group_by: list[str] | None = None,
        metric: str = "count",  # count / sum_duration / avg_duration / sum_billable
        sort: list[tuple[str, str]] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Агрегация time-entries.

        ``date_from``/``date_to`` фильтруют по ``entry_date``.
        Поддерживаемые поля группировки: ``user_id``, ``project_id``,
        ``task_id``, ``epic_id``, ``category_id``, ``status``,
        ``is_billable``, ``date_bucket``.

        Имя колонки метрики совпадает со значением ``metric``
        (``count``/``sum_duration``/``avg_duration``/``sum_billable``).
        Для ``sum_duration``/``avg_duration`` единицы — секунды.
        Для ``sum_billable`` — секунды × часовая ставка (если задана),
        иначе только ``duration_seconds`` × 1 (без денежной размерности).

        Возвращает строки: ключи из ``group_by`` + ключ-метрика.
        """

    # ---- WORKLOAD ----

    @abstractmethod
    async def workload_by_user(
        self,
        *,
        workspace_id: str,
        user_ids: list[str] | None = None,
        project_ids: list[str] | None = None,
        date_from: date,
        date_to: date,
        granularity: str = "day",  # day/week
    ) -> list[dict[str, Any]]:
        """
        Загрузка пользователей: суммарная продолжительность entries
        с группировкой по ``user_id`` × ``date_bucket``.

        Возвращает строки: ``user_id``, ``date_bucket``,
        ``total_duration_seconds``.
        """
