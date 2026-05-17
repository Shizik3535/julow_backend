"""Seed-данные системных шаблонов дашбордов (Analytics BC).

Системные шаблоны (``is_system=True``, ``workspace_id=None``) — глобальные
заготовки дашбордов, доступные во всех workspace. Клиент создаёт
персональный дашборд из шаблона через ``POST /dashboards/from-template``.

Source of truth: этот модуль. Используется в:
    - alembic/versions/2026_05_17_2030-seed_system_dashboard_templates.py
    - scripts/seed_dashboard_templates.py
    - tests/integration/analytics/...

Формат каждого виджета совпадает с тем, что пишет
``infrastructure/persistence/mappers/_query_serialization.py`` в JSONB-
поле ``analytics_dashboard_templates.widget_configs``:

.. code-block:: python

    {
        "widget_type": "<WidgetType.value>",
        "query": {  # AnalyticsQueryDTO.model_dump(mode="json")
            "data_source": "<DataSource.value>",
            "metrics": [{"field": "...", "aggregation": "...", "alias": "..."}],
            "dimensions": [...],
            "filters": [...],
            "date_range": None,
            "sort": [...],
            "limit": None,
            "raw": False,
        },
        "display_params": {...},
    }

Идемпотентность сидинга обеспечивается стабильными UUID
(``INSERT ... ON CONFLICT (id) DO NOTHING``).
"""
from __future__ import annotations

from typing import Any
from uuid import UUID

# --- Виджеты Project Overview --------------------------------------------------

_PROJECT_OVERVIEW_WIDGETS: list[dict[str, Any]] = [
    {
        "widget_type": "number",
        "query": {
            "data_source": "tasks",
            "metrics": [
                {"field": "*", "aggregation": "count", "alias": "total_tasks"}
            ],
            "dimensions": [],
            "filters": [],
            "date_range": None,
            "sort": [],
            "limit": None,
            "raw": False,
        },
        "display_params": {"title": "Всего задач"},
    },
    {
        "widget_type": "pie_chart",
        "query": {
            "data_source": "tasks",
            "metrics": [
                {"field": "*", "aggregation": "count", "alias": "count"}
            ],
            "dimensions": [
                {"field": "status_id", "time_granularity": None, "alias": "status"}
            ],
            "filters": [],
            "date_range": None,
            "sort": [{"field": "count", "order": "desc"}],
            "limit": None,
            "raw": False,
        },
        "display_params": {"title": "Задачи по статусу"},
    },
    {
        "widget_type": "bar_chart",
        "query": {
            "data_source": "tasks",
            "metrics": [
                {"field": "*", "aggregation": "count", "alias": "count"}
            ],
            "dimensions": [
                {"field": "assignee_id", "time_granularity": None, "alias": "assignee"}
            ],
            "filters": [],
            "date_range": None,
            "sort": [{"field": "count", "order": "desc"}],
            "limit": 10,
            "raw": False,
        },
        "display_params": {"title": "Топ-10 исполнителей по задачам"},
    },
    {
        "widget_type": "table",
        "query": {
            "data_source": "project_progress",
            "metrics": [],
            "dimensions": [],
            "filters": [],
            "date_range": None,
            "sort": [],
            "limit": None,
            "raw": True,
        },
        "display_params": {"title": "Прогресс проектов"},
    },
]


# --- Виджеты Task Analytics ----------------------------------------------------

_TASK_ANALYTICS_WIDGETS: list[dict[str, Any]] = [
    {
        "widget_type": "number",
        "query": {
            "data_source": "tasks",
            "metrics": [
                {"field": "*", "aggregation": "count", "alias": "open_tasks"}
            ],
            "dimensions": [],
            "filters": [
                {"field": "completed", "operator": "eq", "value": "false", "value_to": None}
            ],
            "date_range": None,
            "sort": [],
            "limit": None,
            "raw": False,
        },
        "display_params": {"title": "Открытые задачи"},
    },
    {
        "widget_type": "pie_chart",
        "query": {
            "data_source": "tasks",
            "metrics": [
                {"field": "*", "aggregation": "count", "alias": "count"}
            ],
            "dimensions": [
                {"field": "priority", "time_granularity": None, "alias": "priority"}
            ],
            "filters": [],
            "date_range": None,
            "sort": [{"field": "count", "order": "desc"}],
            "limit": None,
            "raw": False,
        },
        "display_params": {"title": "Задачи по приоритету"},
    },
    {
        "widget_type": "bar_chart",
        "query": {
            "data_source": "tasks",
            "metrics": [
                {"field": "*", "aggregation": "count", "alias": "count"}
            ],
            "dimensions": [
                {"field": "task_type", "time_granularity": None, "alias": "task_type"}
            ],
            "filters": [],
            "date_range": None,
            "sort": [{"field": "count", "order": "desc"}],
            "limit": None,
            "raw": False,
        },
        "display_params": {"title": "Задачи по типу"},
    },
    {
        "widget_type": "line_chart",
        "query": {
            "data_source": "tasks",
            "metrics": [
                {"field": "*", "aggregation": "count", "alias": "count"}
            ],
            "dimensions": [
                {"field": "created_at", "time_granularity": "day", "alias": "day"}
            ],
            "filters": [
                {"field": "date_field", "operator": "eq", "value": "created_at", "value_to": None}
            ],
            "date_range": None,
            "sort": [{"field": "day", "order": "asc"}],
            "limit": None,
            "raw": False,
        },
        "display_params": {"title": "Создание задач по дням"},
    },
]


# --- Виджеты Time Tracking -----------------------------------------------------

_TIME_TRACKING_WIDGETS: list[dict[str, Any]] = [
    {
        "widget_type": "number",
        "query": {
            "data_source": "time_entries",
            "metrics": [
                {
                    "field": "duration_seconds",
                    "aggregation": "sum",
                    "alias": "total_duration_seconds",
                }
            ],
            "dimensions": [],
            "filters": [],
            "date_range": None,
            "sort": [],
            "limit": None,
            "raw": False,
        },
        "display_params": {"title": "Всего отработано (сек)"},
    },
    {
        "widget_type": "bar_chart",
        "query": {
            "data_source": "time_entries",
            "metrics": [
                {
                    "field": "duration_seconds",
                    "aggregation": "sum",
                    "alias": "duration_seconds",
                }
            ],
            "dimensions": [
                {"field": "user_id", "time_granularity": None, "alias": "user"}
            ],
            "filters": [],
            "date_range": None,
            "sort": [{"field": "duration_seconds", "order": "desc"}],
            "limit": 10,
            "raw": False,
        },
        "display_params": {"title": "Часы по пользователям (топ-10)"},
    },
    {
        "widget_type": "bar_chart",
        "query": {
            "data_source": "time_entries",
            "metrics": [
                {
                    "field": "duration_seconds",
                    "aggregation": "sum",
                    "alias": "duration_seconds",
                }
            ],
            "dimensions": [
                {"field": "category_id", "time_granularity": None, "alias": "category"}
            ],
            "filters": [],
            "date_range": None,
            "sort": [{"field": "duration_seconds", "order": "desc"}],
            "limit": None,
            "raw": False,
        },
        "display_params": {"title": "Часы по категориям активности"},
    },
    {
        "widget_type": "line_chart",
        "query": {
            "data_source": "time_entries",
            "metrics": [
                {
                    "field": "duration_seconds",
                    "aggregation": "sum",
                    "alias": "duration_seconds",
                }
            ],
            "dimensions": [
                {"field": "started_at", "time_granularity": "day", "alias": "day"}
            ],
            "filters": [],
            "date_range": None,
            "sort": [{"field": "day", "order": "asc"}],
            "limit": None,
            "raw": False,
        },
        "display_params": {"title": "Часы по дням"},
    },
]


# --- Полный реестр системных шаблонов -----------------------------------------

SYSTEM_DASHBOARD_TEMPLATES: list[dict[str, Any]] = [
    {
        "id": UUID("00000000-0000-0000-0007-000000000001"),
        "workspace_id": None,
        "name": "Project Overview",
        "description": (
            "Базовый обзор проектов workspace: задачи по статусу, "
            "топ-исполнители и прогресс проектов."
        ),
        "is_system": True,
        "is_deleted": False,
        "widget_configs": _PROJECT_OVERVIEW_WIDGETS,
    },
    {
        "id": UUID("00000000-0000-0000-0007-000000000002"),
        "workspace_id": None,
        "name": "Task Analytics",
        "description": (
            "Аналитика задач: распределение по приоритетам/типам и "
            "динамика создания во времени."
        ),
        "is_system": True,
        "is_deleted": False,
        "widget_configs": _TASK_ANALYTICS_WIDGETS,
    },
    {
        "id": UUID("00000000-0000-0000-0007-000000000003"),
        "workspace_id": None,
        "name": "Time Tracking",
        "description": (
            "Учёт рабочего времени: суммарные часы, разбивка по "
            "пользователям и категориям активности, динамика по дням."
        ),
        "is_system": True,
        "is_deleted": False,
        "widget_configs": _TIME_TRACKING_WIDGETS,
    },
]


__all__ = ["SYSTEM_DASHBOARD_TEMPLATES"]
