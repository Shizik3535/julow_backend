"""DTO для метаданных Analytics-схемы (``/analytics/schema``).

Поля — только примитивы. Доменные enum'ы (``DataSource``,
``FilterOperator``, ...) маппятся в строки на границе application слоя.
"""
from __future__ import annotations

from pydantic import ConfigDict

from app.shared.application.base_dto import BaseDTO


class FieldDescriptorDTO(BaseDTO):
    """Описание одного поля ``DataSource``.

    Атрибуты:
        name: Канонический ключ поля (как клиент пишет ``field`` в
            ``FilterConfig`` / ``Dimension`` / ``SortConfig``).
        type: Условный тип ('string' | 'uuid' | 'enum' | 'datetime' |
            'date' | 'integer' | 'float' | 'boolean').
        description: Краткое описание для клиента.
        filterable: Поле допустимо в ``filters``.
        groupable: Поле допустимо в ``dimensions`` (``group_by``).
        sortable: Поле допустимо в ``sort``.
        time_granularity_supported: Поле — datetime/date-измерение,
            допустимо использовать ``time_granularity``.
        allowed_values: Для ``type='enum'`` — список валидных значений.
        notes: Дополнительные пояснения.
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        frozen=True,
    )

    name: str
    type: str
    description: str
    filterable: bool = True
    groupable: bool = False
    sortable: bool = False
    time_granularity_supported: bool = False
    allowed_values: list[str] | None = None
    notes: str | None = None


class MetricTemplateDTO(BaseDTO):
    """Шаблон метрики (готовый к подстановке в ``AnalyticsQuery.metrics``)."""

    field: str = "*"
    aggregation: str = "count"
    alias: str | None = None


class DataSourceSummaryDTO(BaseDTO):
    """Краткое описание одного ``DataSource`` для списка."""

    data_source: str
    bounded_context: str
    description: str | None = None


class DataSourceSchemaDTO(BaseDTO):
    """Полная схема одного ``DataSource``."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        frozen=True,
    )

    data_source: str
    bounded_context: str
    description: str | None = None
    fields: list[FieldDescriptorDTO] = []
    supported_aggregations: list[str] = []
    default_metrics: list[MetricTemplateDTO] = []
    notes: str | None = None


class DataSourceListDTO(BaseDTO):
    """Обёртка для списка DataSource (для совместимости с BaseQueryHandler)."""

    items: list[DataSourceSummaryDTO] = []


class AnalyticsSchemaDTO(BaseDTO):
    """Полный реестр метаданных Analytics-схемы.

    Атрибуты:
        data_sources: Схемы всех поддерживаемых источников.
        filter_operators: Допустимые значения ``FilterConfig.operator``.
        aggregations: Допустимые значения ``MetricDefinition.aggregation``.
        time_granularities: Допустимые значения ``Dimension.time_granularity``.
        sort_orders: Допустимые значения ``SortConfig.order``.
        widget_types: Допустимые значения ``WidgetType`` (для дашбордов).
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        frozen=True,
    )

    data_sources: list[DataSourceSchemaDTO] = []
    filter_operators: list[str] = []
    aggregations: list[str] = []
    time_granularities: list[str] = []
    sort_orders: list[str] = []
    widget_types: list[str] = []
