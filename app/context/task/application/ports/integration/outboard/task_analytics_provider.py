from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Any


class TaskAnalyticsProvider(ABC):
    """
    Outboard-порт: агрегационные данные задач и спринт-метрики для Analytics BC.

    Реализуется в infrastructure-слое Task BC. Возвращает плоские
    табличные строки (``list[dict[str, Any]]``); резолвер Analytics
    переименовывает ключи в alias-ы из ``AnalyticsQuery``.

    Покрывает DataSource'ы Task BC из spec:
    ``TASKS``, ``TASK_STATUS_HISTORY``, ``SPRINTS``, ``SPRINT_BURNDOWN``,
    ``SPRINT_VELOCITY``.

    Замечание: ``TASK_STATUS_HISTORY`` и ``SPRINT_BURNDOWN`` в текущей
    реализации **аппроксимируются** по ``created_at``/``completed_at``
    (отдельной таблицы-истории нет — точные значения требуют ввода
    ``task_status_history`` в отдельной итерации).
    """

    # ---- TASKS / TASK_STATUS_HISTORY ----

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
        statuses: list[str] | None = None,  # lifecycle status (active/archived/...)
        completed: bool | None = None,  # True=completed_at IS NOT NULL, False=IS NULL
        date_field: str | None = None,  # created_at / completed_at / due_date / start_date
        date_from: date | None = None,
        date_to: date | None = None,
        granularity: str | None = None,  # day/week/month/quarter/year
        group_by: list[str] | None = None,
        sort: list[tuple[str, str]] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Агрегация задач: ``COUNT(*)`` с произвольной группировкой/фильтрацией.

        ``workspace_id`` участвует косвенно: фильтр по проектам workspace.
        Если ``project_ids`` не задан, провайдер сам отрезолвит проекты
        workspace (по реляции в Project BC через AsyncSession в одной
        транзакции) — для MVP считаем, что вызывающий резолвер всегда
        передаёт ``project_ids`` (он знает workspace_id и идёт через
        ProjectAnalyticsPort).

        Поддерживаемые поля группировки: ``status_id``, ``priority``,
        ``task_type``, ``status``, ``assignee_id``, ``project_id``,
        ``sprint_id``, ``epic_id``, ``date_bucket`` (при ``granularity``).
        Поддерживаемые поля сортировки: те же + ``count``.

        Возвращает строки: ключи из ``group_by`` + ``count``.
        Если ``group_by`` пуст — одна строка с ``count``.
        """

    # ---- SPRINTS ----

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
        """
        Список/агрегация спринтов проектов.

        Возвращает строки:
            - без ``group_by`` — ``id``, ``project_id``, ``name``, ``status``,
              ``start_date``, ``end_date``, ``goal``;
            - с ``group_by`` — ключи из ``group_by`` + ``count``.
        """

    # ---- SPRINT_BURNDOWN ----

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
        """
        Точки burndown за период спринта.

        Approximate: точное «сколько задач было открыто на день D»
        требует ``task_status_history``. В MVP считаем по ``completed_at``:
        ``remaining(D) = total - count(completed_at <= D)``.

        Возвращает строки по дням ``[start..end]`` (включительно):
        ``date``, ``remaining_count``, ``ideal_count``.
        """

    # ---- SPRINT_VELOCITY ----

    @abstractmethod
    async def sprint_velocity(
        self,
        *,
        workspace_id: str,
        project_id: str,
        last_n_sprints: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Скорость по последним закрытым спринтам проекта.

        Approximate: считаем количество завершённых задач в каждом
        спринте (``completed_at`` в диапазоне ``[sprint_start..sprint_end]``).

        Возвращает строки (хронологически по ``sprint_end``):
        ``sprint_id``, ``sprint_name``, ``sprint_end``, ``completed_count``,
        ``total_count``.
        """

    # ---- PROJECT_PROGRESS ----

    @abstractmethod
    async def project_progress_counts(
        self,
        *,
        workspace_id: str,
        project_ids: list[str],
        overdue_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """
        Условная агрегация задач по проектам: total / completed / overdue.

        Выполняет один SQL-запрос с ``CASE WHEN`` вместо трёх отдельных
        ``count_tasks`` вызовов. Используется ``ProjectAnalyticsResolver``
        для ``PROJECT_PROGRESS``.

        ``overdue_date``: задачи с ``completed_at IS NULL`` и
        ``due_date < overdue_date`` считаются просроченными. Если не
        задано — просроченные не считаются (возвращает 0).

        Возвращает строки:
        ``project_id``, ``total_count``, ``completed_count``, ``overdue_count``.
        """
