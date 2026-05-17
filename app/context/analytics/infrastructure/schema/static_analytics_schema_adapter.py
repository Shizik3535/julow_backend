"""Статический провайдер Analytics-схемы.

Зеркалит знание резолверов (``infrastructure/query_execution/resolvers``)
о том, какие поля каждый ``DataSource`` принимает в фильтрах /
группировке. Это знание уже легитимно живёт на infrastructure-слое
Analytics BC (резолверы знают cross-BC поля), поэтому реестр размещён
рядом с резолверами, а не в application/domain.

Расхождения с реальными резолверами ловятся unit-тестами
(см. ``tests/unit/analytics/test_static_analytics_schema_adapter.py``).
"""
from __future__ import annotations

from app.context.analytics.application.dto.analytics_schema_dto import (
    AnalyticsSchemaDTO,
    DataSourceSchemaDTO,
    DataSourceSummaryDTO,
    FieldDescriptorDTO,
    MetricTemplateDTO,
)
from app.context.analytics.application.ports.schema.analytics_schema_port import (
    AnalyticsSchemaPort,
)
from app.context.analytics.domain.value_objects.data_source import DataSource
from app.context.analytics.domain.value_objects.filter_operator import FilterOperator
from app.context.analytics.domain.value_objects.metric_aggregation import (
    MetricAggregation,
)
from app.context.analytics.domain.value_objects.sort_order import SortOrder
from app.context.analytics.domain.value_objects.time_granularity import TimeGranularity
from app.context.analytics.domain.value_objects.widget_type import WidgetType


# ---------------------------------------------------------------------------
# Общие field-блоки (повторно используемые между источниками)
# ---------------------------------------------------------------------------

_PROJECT_ID = FieldDescriptorDTO(
    name="project_id",
    type="uuid",
    description="ID проекта",
    filterable=True,
    groupable=True,
    sortable=True,
)
_USER_ID = FieldDescriptorDTO(
    name="user_id",
    type="uuid",
    description="ID пользователя",
    filterable=True,
    groupable=True,
    sortable=True,
)
_ASSIGNEE_ID = FieldDescriptorDTO(
    name="assignee_id",
    type="uuid",
    description="ID исполнителя задачи",
    filterable=True,
    groupable=True,
    sortable=True,
)


# ---------------------------------------------------------------------------
# Схемы по DataSource (зеркалят резолверы)
# ---------------------------------------------------------------------------

_TASKS_SCHEMA = DataSourceSchemaDTO(
    data_source=DataSource.TASKS.value,
    bounded_context=DataSource.TASKS.bounded_context.value,
    description="Агрегация задач Task BC (count по фильтрам и группировкам).",
    fields=[
        FieldDescriptorDTO(name="id", type="uuid", description="ID задачи", sortable=True),
        _PROJECT_ID,
        FieldDescriptorDTO(name="sprint_id", type="uuid", description="ID спринта", groupable=True),
        FieldDescriptorDTO(name="epic_id", type="uuid", description="ID эпика", groupable=True),
        _ASSIGNEE_ID,
        FieldDescriptorDTO(
            name="status_id", type="uuid", description="ID статуса задачи", groupable=True
        ),
        FieldDescriptorDTO(
            name="status",
            type="enum",
            description="Жизненный цикл (active/archived)",
            groupable=True,
            allowed_values=["active", "archived"],
        ),
        FieldDescriptorDTO(
            name="priority",
            type="enum",
            description="Приоритет задачи",
            groupable=True,
            allowed_values=["low", "medium", "high", "critical"],
        ),
        FieldDescriptorDTO(
            name="task_type", type="string", description="Тип задачи", groupable=True
        ),
        FieldDescriptorDTO(
            name="completed", type="boolean", description="Завершена ли задача"
        ),
        FieldDescriptorDTO(
            name="date_field",
            type="enum",
            description="Поле для применения date_range",
            filterable=False,
            allowed_values=["created_at", "updated_at", "due_date"],
            notes="Управляет колонкой, по которой применяется date_range.",
        ),
        FieldDescriptorDTO(
            name="created_at",
            type="datetime",
            description="Дата создания (для time-series)",
            groupable=True,
            sortable=True,
            time_granularity_supported=True,
        ),
    ],
    supported_aggregations=[MetricAggregation.COUNT.value, MetricAggregation.COUNT_DISTINCT.value],
    default_metrics=[MetricTemplateDTO(field="*", aggregation="count", alias="count")],
    notes="Базовая агрегация — count. Для time-series укажите dimension 'created_at' + time_granularity.",
)

_TASK_STATUS_HISTORY_SCHEMA = DataSourceSchemaDTO(
    data_source=DataSource.TASK_STATUS_HISTORY.value,
    bounded_context=DataSource.TASK_STATUS_HISTORY.bounded_context.value,
    description="Approx: текущее распределение задач по статусам.",
    fields=[
        _PROJECT_ID,
        FieldDescriptorDTO(name="sprint_id", type="uuid", description="ID спринта", groupable=True),
        FieldDescriptorDTO(
            name="status_id", type="uuid", description="ID статуса", groupable=True
        ),
    ],
    supported_aggregations=[MetricAggregation.COUNT.value],
    default_metrics=[MetricTemplateDTO(field="*", aggregation="count", alias="count")],
    notes="Approx-источник: текущий снапшот, не история переходов.",
)

_SPRINTS_SCHEMA = DataSourceSchemaDTO(
    data_source=DataSource.SPRINTS.value,
    bounded_context=DataSource.SPRINTS.bounded_context.value,
    description="Список спринтов проекта. Требует фильтр project_id.",
    fields=[
        _PROJECT_ID,
        FieldDescriptorDTO(name="sprint_id", type="uuid", description="Конкретный спринт"),
        FieldDescriptorDTO(
            name="status",
            type="enum",
            description="Статус спринта",
            groupable=True,
            allowed_values=["planned", "active", "completed"],
        ),
    ],
    supported_aggregations=[MetricAggregation.COUNT.value],
    default_metrics=[],
)

_SPRINT_BURNDOWN_SCHEMA = DataSourceSchemaDTO(
    data_source=DataSource.SPRINT_BURNDOWN.value,
    bounded_context=DataSource.SPRINT_BURNDOWN.bounded_context.value,
    description="Точки burndown по дням спринта.",
    fields=[
        FieldDescriptorDTO(
            name="sprint_id",
            type="uuid",
            description="ID спринта (обязательный фильтр)",
        ),
    ],
    supported_aggregations=[],
    default_metrics=[],
    notes="Метрики/измерения игнорируются; нужно только sprint_id.",
)

_SPRINT_VELOCITY_SCHEMA = DataSourceSchemaDTO(
    data_source=DataSource.SPRINT_VELOCITY.value,
    bounded_context=DataSource.SPRINT_VELOCITY.bounded_context.value,
    description="Velocity последних N спринтов проекта.",
    fields=[
        _PROJECT_ID,
        FieldDescriptorDTO(
            name="last_n_sprints",
            type="integer",
            description="Сколько последних спринтов учитывать (по умолчанию 5)",
            filterable=False,
        ),
    ],
    supported_aggregations=[],
    default_metrics=[],
)

_PROJECTS_SCHEMA = DataSourceSchemaDTO(
    data_source=DataSource.PROJECTS.value,
    bounded_context=DataSource.PROJECTS.bounded_context.value,
    description="Список / агрегация проектов workspace.",
    fields=[
        _PROJECT_ID,
        FieldDescriptorDTO(
            name="status",
            type="enum",
            description="Статус проекта",
            groupable=True,
            allowed_values=["planning", "active", "on_hold", "completed", "cancelled"],
        ),
        FieldDescriptorDTO(
            name="visibility",
            type="enum",
            description="Видимость",
            groupable=True,
            allowed_values=["private", "workspace", "public"],
        ),
        FieldDescriptorDTO(
            name="methodology", type="string", description="Методология", groupable=True
        ),
        FieldDescriptorDTO(
            name="date_field",
            type="enum",
            description="Поле для применения date_range",
            filterable=False,
            allowed_values=["created_at", "updated_at", "start_date", "deadline"],
            notes="Управляет колонкой, по которой применяется date_range.",
        ),
        FieldDescriptorDTO(
            name="created_at",
            type="datetime",
            description="Дата создания (для time-series)",
            groupable=True,
            sortable=True,
            time_granularity_supported=True,
        ),
    ],
    supported_aggregations=[MetricAggregation.COUNT.value, MetricAggregation.COUNT_DISTINCT.value],
    default_metrics=[MetricTemplateDTO(field="*", aggregation="count", alias="count")],
)

_PROJECT_PROGRESS_SCHEMA = DataSourceSchemaDTO(
    data_source=DataSource.PROJECT_PROGRESS.value,
    bounded_context=DataSource.PROJECT_PROGRESS.bounded_context.value,
    description="Снапшот прогресса проектов (total/completed/overdue + percent).",
    fields=[
        _PROJECT_ID,
        FieldDescriptorDTO(
            name="status",
            type="enum",
            description="Фильтр по статусу проекта",
            allowed_values=["planning", "active", "on_hold", "completed", "cancelled"],
        ),
    ],
    supported_aggregations=[],
    default_metrics=[],
    notes="date_range игнорируется — это снапшот, не временной ряд.",
)

_TIME_ENTRIES_SCHEMA = DataSourceSchemaDTO(
    data_source=DataSource.TIME_ENTRIES.value,
    bounded_context=DataSource.TIME_ENTRIES.bounded_context.value,
    description="Записи учёта времени (TimeTracking BC).",
    fields=[
        _USER_ID,
        _PROJECT_ID,
        FieldDescriptorDTO(name="task_id", type="uuid", description="ID задачи", groupable=True),
        FieldDescriptorDTO(name="epic_id", type="uuid", description="ID эпика"),
        FieldDescriptorDTO(
            name="category_id",
            type="uuid",
            description="ID категории активности",
            groupable=True,
        ),
        FieldDescriptorDTO(
            name="is_billable", type="boolean", description="Биллабельная активность"
        ),
        FieldDescriptorDTO(
            name="status",
            type="enum",
            description="Статус записи времени",
            groupable=True,
            allowed_values=["draft", "submitted", "approved", "rejected"],
        ),
        FieldDescriptorDTO(
            name="started_at",
            type="datetime",
            description="Начало активности (для time-series)",
            groupable=True,
            sortable=True,
            time_granularity_supported=True,
        ),
    ],
    supported_aggregations=[
        MetricAggregation.COUNT.value,
        MetricAggregation.SUM.value,
        MetricAggregation.AVG.value,
    ],
    default_metrics=[
        MetricTemplateDTO(field="*", aggregation="count", alias="count"),
        MetricTemplateDTO(
            field="duration_seconds", aggregation="sum", alias="total_duration_seconds"
        ),
    ],
    notes=(
        "SUM/AVG поддержаны для полей duration_seconds, billable_amount,"
        " duration_billable_seconds. Прочие комбинации сводятся к count."
    ),
)

_WORKLOAD_SCHEMA = DataSourceSchemaDTO(
    data_source=DataSource.WORKLOAD.value,
    bounded_context=DataSource.WORKLOAD.bounded_context.value,
    description="Загрузка пользователей по дням/неделям (TimeTracking BC).",
    fields=[
        _USER_ID,
        _PROJECT_ID,
    ],
    supported_aggregations=[MetricAggregation.SUM.value],
    default_metrics=[],
    notes=(
        "Требует date_range. time_granularity управляет шириной бакета"
        " (по умолчанию 'day')."
    ),
)

_WORKSPACES_SCHEMA = DataSourceSchemaDTO(
    data_source=DataSource.WORKSPACES.value,
    bounded_context=DataSource.WORKSPACES.bounded_context.value,
    description="Информация о workspace (Workspace BC).",
    fields=[
        FieldDescriptorDTO(name="workspace_id", type="uuid", description="ID workspace"),
        FieldDescriptorDTO(
            name="organization_id", type="uuid", description="ID организации"
        ),
        FieldDescriptorDTO(
            name="status",
            type="enum",
            description="Статус workspace",
            groupable=True,
            allowed_values=["active", "archived", "suspended"],
        ),
        FieldDescriptorDTO(
            name="workspace_type",
            type="string",
            description="Тип workspace",
            groupable=True,
        ),
    ],
    supported_aggregations=[MetricAggregation.COUNT.value],
    default_metrics=[],
    notes="time_granularity не поддержан (нет временных рядов).",
)


_DATA_SOURCE_SCHEMAS: dict[DataSource, DataSourceSchemaDTO] = {
    DataSource.TASKS: _TASKS_SCHEMA,
    DataSource.TASK_STATUS_HISTORY: _TASK_STATUS_HISTORY_SCHEMA,
    DataSource.SPRINTS: _SPRINTS_SCHEMA,
    DataSource.SPRINT_BURNDOWN: _SPRINT_BURNDOWN_SCHEMA,
    DataSource.SPRINT_VELOCITY: _SPRINT_VELOCITY_SCHEMA,
    DataSource.PROJECTS: _PROJECTS_SCHEMA,
    DataSource.PROJECT_PROGRESS: _PROJECT_PROGRESS_SCHEMA,
    DataSource.TIME_ENTRIES: _TIME_ENTRIES_SCHEMA,
    DataSource.WORKLOAD: _WORKLOAD_SCHEMA,
    DataSource.WORKSPACES: _WORKSPACES_SCHEMA,
}


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------


class StaticAnalyticsSchemaAdapter(AnalyticsSchemaPort):
    """Статическая реализация ``AnalyticsSchemaPort``.

    Возвращает фиксированный реестр (см. ``_DATA_SOURCE_SCHEMAS``),
    зеркалящий поведение резолверов. Без состояния — безопасно
    регистрировать как Singleton.
    """

    def get_full_schema(self) -> AnalyticsSchemaDTO:
        return AnalyticsSchemaDTO(
            data_sources=list(_DATA_SOURCE_SCHEMAS.values()),
            filter_operators=[op.value for op in FilterOperator],
            aggregations=[a.value for a in MetricAggregation],
            time_granularities=[g.value for g in TimeGranularity],
            sort_orders=[o.value for o in SortOrder],
            widget_types=[w.value for w in WidgetType],
        )

    def list_data_sources(self) -> list[DataSourceSummaryDTO]:
        return [
            DataSourceSummaryDTO(
                data_source=schema.data_source,
                bounded_context=schema.bounded_context,
                description=schema.description,
            )
            for schema in _DATA_SOURCE_SCHEMAS.values()
        ]

    def get_data_source_schema(self, data_source: str) -> DataSourceSchemaDTO | None:
        try:
            ds = DataSource(data_source)
        except ValueError:
            return None
        return _DATA_SOURCE_SCHEMAS.get(ds)
