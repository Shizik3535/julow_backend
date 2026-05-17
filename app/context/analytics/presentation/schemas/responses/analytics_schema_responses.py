"""Pydantic response-схемы для ``/analytics/schema`` endpoint'ов."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class FieldDescriptorResponse(BaseModel):
    """Описание одного поля ``DataSource``."""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., description="Канонический ключ поля")
    type: str = Field(
        ...,
        description="Условный тип ('string'|'uuid'|'enum'|'datetime'|'date'|'integer'|'float'|'boolean')",
    )
    description: str = Field(..., description="Краткое описание")
    filterable: bool = Field(default=True, description="Можно ли использовать в filters")
    groupable: bool = Field(default=False, description="Можно ли использовать в dimensions")
    sortable: bool = Field(default=False, description="Можно ли использовать в sort")
    time_granularity_supported: bool = Field(
        default=False,
        description="Поле — datetime/date-измерение, допустимо time_granularity",
    )
    allowed_values: list[str] | None = Field(
        default=None, description="Для type='enum' — список валидных значений"
    )
    notes: str | None = Field(default=None, description="Дополнительные пояснения")


class MetricTemplateResponse(BaseModel):
    """Шаблон метрики для подстановки в AnalyticsQuery.metrics."""

    model_config = ConfigDict(from_attributes=True)

    field: str = Field(default="*", description="Имя поля или '*' для count(*)")
    aggregation: str = Field(default="count", description="Тип агрегации")
    alias: str | None = Field(default=None, description="Псевдоним колонки")


class DataSourceSummaryResponse(BaseModel):
    """Краткое описание DataSource."""

    model_config = ConfigDict(from_attributes=True)

    data_source: str = Field(..., description="DataSource.value")
    bounded_context: str = Field(..., description="BoundedContextRef.value источника")
    description: str | None = Field(default=None, description="Описание")


class DataSourceSchemaResponse(BaseModel):
    """Полная схема одного DataSource."""

    model_config = ConfigDict(from_attributes=True)

    data_source: str = Field(..., description="DataSource.value")
    bounded_context: str = Field(..., description="BoundedContextRef.value")
    description: str | None = Field(default=None)
    fields: list[FieldDescriptorResponse] = Field(default_factory=list)
    supported_aggregations: list[str] = Field(default_factory=list)
    default_metrics: list[MetricTemplateResponse] = Field(default_factory=list)
    notes: str | None = Field(default=None)


class AnalyticsSchemaResponse(BaseModel):
    """Полный реестр Analytics-схемы."""

    model_config = ConfigDict(from_attributes=True)

    data_sources: list[DataSourceSchemaResponse] = Field(default_factory=list)
    filter_operators: list[str] = Field(default_factory=list)
    aggregations: list[str] = Field(default_factory=list)
    time_granularities: list[str] = Field(default_factory=list)
    sort_orders: list[str] = Field(default_factory=list)
    widget_types: list[str] = Field(default_factory=list)
