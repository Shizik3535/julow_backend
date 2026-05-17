from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from app.context.analytics.domain.value_objects.bounded_context_ref import BoundedContextRef
from app.context.analytics.domain.value_objects.data_source import DataSource
from app.context.analytics.domain.value_objects.export_format import ExportFormat
from app.context.analytics.domain.value_objects.filter_operator import FilterOperator
from app.context.analytics.domain.value_objects.metric_aggregation import MetricAggregation
from app.context.analytics.domain.value_objects.report_frequency import ReportFrequency
from app.context.analytics.domain.value_objects.report_type import ReportType
from app.context.analytics.domain.value_objects.share_access_level import ShareAccessLevel
from app.context.analytics.domain.value_objects.sort_order import SortOrder
from app.context.analytics.domain.value_objects.time_granularity import TimeGranularity
from app.context.analytics.domain.value_objects.widget_type import WidgetType


class FilterConfigRequest(BaseModel):
    """Фильтр аналитического запроса."""

    field: str
    operator: FilterOperator
    value: str
    value_to: str | None = None


class MetricDefinitionRequest(BaseModel):
    """Описание метрики."""

    field: str = "*"
    aggregation: MetricAggregation = MetricAggregation.COUNT
    alias: str | None = None


class DimensionRequest(BaseModel):
    """Измерение группировки."""

    field: str
    time_granularity: TimeGranularity | None = None
    alias: str | None = None


class SortConfigRequest(BaseModel):
    """Правило сортировки."""

    field: str
    order: SortOrder = SortOrder.DESC


class DateRangeRequest(BaseModel):
    """Диапазон дат (включительно)."""

    start: date | None = None
    end: date | None = None


class AnalyticsQueryRequest(BaseModel):
    """Аналитический запрос (для виджетов и ad-hoc)."""

    data_source: DataSource
    metrics: list[MetricDefinitionRequest] = []
    dimensions: list[DimensionRequest] = []
    filters: list[FilterConfigRequest] = []
    date_range: DateRangeRequest | None = None
    sort: list[SortConfigRequest] = []
    limit: int | None = None
    raw: bool = False


class ExecuteAnalyticsQueryRequest(BaseModel):
    """Ad-hoc выполнение аналитического запроса."""

    query: AnalyticsQueryRequest


class CreateDashboardRequest(BaseModel):
    """Создать дашборд."""

    workspace_id: str
    name: str
    description: str | None = None


class UpdateDashboardRequest(BaseModel):
    """Обновить имя/описание дашборда."""

    name: str | None = None
    description: str | None = None


class AddWidgetRequest(BaseModel):
    """Добавить виджет на дашборд."""

    title: str
    widget_type: WidgetType
    query: AnalyticsQueryRequest | None = None
    size: dict[str, int] | None = None
    position: dict[str, int] | None = None
    display_params: dict[str, Any] | None = None


class UpdateWidgetRequest(BaseModel):
    """Обновить виджет."""

    title: str | None = None
    query: AnalyticsQueryRequest | None = None
    size: dict[str, int] | None = None
    position: dict[str, int] | None = None
    display_params: dict[str, Any] | None = None


class WidgetLayoutItemRequest(BaseModel):
    """Один элемент массового обновления layout."""

    widget_id: str
    position: dict[str, int] | None = None
    size: dict[str, int] | None = None


class UpdateDashboardLayoutRequest(BaseModel):
    """Массовое обновление позиций/размеров виджетов."""

    widgets: list[WidgetLayoutItemRequest]


class SetDashboardAutoRefreshRequest(BaseModel):
    """Настройка авто-обновления дашборда."""

    enabled: bool
    interval_seconds: int | None = None


class ShareDashboardRequest(BaseModel):
    """Расшарить дашборд."""

    user_id: str
    access_level: ShareAccessLevel = ShareAccessLevel.VIEW


class UnshareDashboardRequest(BaseModel):
    """Снять шаринг дашборда."""

    user_id: str


class CreateDashboardFromTemplateRequest(BaseModel):
    """Создать дашборд из шаблона."""

    workspace_id: str
    template_id: str
    name: str | None = None
    description: str | None = None


class CustomTemplateWidgetRequest(BaseModel):
    """Виджет внутри запроса на создание шаблона."""

    widget_type: WidgetType
    query: AnalyticsQueryRequest
    display_params: dict[str, Any] | None = None


class CreateCustomTemplateRequest(BaseModel):
    """Создать пользовательский шаблон дашборда."""

    workspace_id: str
    name: str
    description: str | None = None
    widgets: list[CustomTemplateWidgetRequest]


class CreateReportRequest(BaseModel):
    """Создать отчёт."""

    workspace_id: str
    name: str
    report_type: ReportType
    query: AnalyticsQueryRequest
    description: str | None = None


class UpdateReportRequest(BaseModel):
    """Обновить отчёт."""

    name: str | None = None
    description: str | None = None
    query: AnalyticsQueryRequest | None = None


class ShareReportRequest(BaseModel):
    """Расшарить отчёт."""

    user_id: str
    access_level: ShareAccessLevel = ShareAccessLevel.VIEW


class UnshareReportRequest(BaseModel):
    """Снять шаринг отчёта."""

    user_id: str


class GenerateReportRequest(BaseModel):
    """Запрос генерации отчёта."""

    workspace_id: str
    format: ExportFormat = ExportFormat.PDF
    report_id: str | None = None
    report_type: ReportType | None = None
    query: AnalyticsQueryRequest | None = None


class SetReportScheduleRequest(BaseModel):
    """Установить расписание отчёта."""

    frequency: ReportFrequency
    recipients: list[str]
    is_active: bool = True
