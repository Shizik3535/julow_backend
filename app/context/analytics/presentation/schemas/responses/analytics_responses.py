from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class FilterConfigResponse(BaseModel):
    field: str
    operator: str
    value: str
    value_to: str | None = None


class MetricDefinitionResponse(BaseModel):
    field: str = "*"
    aggregation: str = "count"
    alias: str | None = None


class DimensionResponse(BaseModel):
    field: str
    time_granularity: str | None = None
    alias: str | None = None


class SortConfigResponse(BaseModel):
    field: str
    order: str = "desc"


class DateRangeResponse(BaseModel):
    start: str | None = None
    end: str | None = None


class AnalyticsQueryResponse(BaseModel):
    data_source: str
    metrics: list[MetricDefinitionResponse] = []
    dimensions: list[DimensionResponse] = []
    filters: list[FilterConfigResponse] = []
    date_range: DateRangeResponse | None = None
    sort: list[SortConfigResponse] = []
    limit: int | None = None
    raw: bool = False


class AnalyticsResultRowResponse(BaseModel):
    values: dict[str, Any] = {}


class AnalyticsResultResponse(BaseModel):
    data_source: str
    bounded_context: str
    columns: list[str] = []
    rows: list[AnalyticsResultRowResponse] = []
    total: int = 0
    generated_at: str = ""


class WidgetResponse(BaseModel):
    id: str
    title: str
    widget_type: str
    order: int
    size: dict[str, int]
    position: dict[str, int] | None = None
    query: AnalyticsQueryResponse | None = None
    display_params: dict[str, Any] = {}


class DashboardShareResponse(BaseModel):
    user_id: str
    access_level: str
    shared_at: datetime


class DashboardResponse(BaseModel):
    id: str
    owner_id: str
    workspace_id: str | None = None
    name: str
    description: str | None = None
    widgets: list[WidgetResponse] = []
    shares: list[DashboardShareResponse] = []
    is_auto_refresh: bool = False
    refresh_interval_seconds: int | None = None
    is_default: bool = False
    created_at: datetime
    updated_at: datetime


class DashboardTemplateResponse(BaseModel):
    id: str
    workspace_id: str | None = None
    name: str
    description: str | None = None
    widgets: list[WidgetResponse] = []
    is_system: bool = False
    created_at: datetime
    updated_at: datetime


class ReportScheduleResponse(BaseModel):
    frequency: str
    recipients: list[str] = []
    is_active: bool = True
    next_run_at: datetime | None = None
    last_run_at: datetime | None = None


class ReportShareResponse(BaseModel):
    user_id: str
    access_level: str
    shared_at: datetime


class ReportResponse(BaseModel):
    id: str
    owner_id: str
    workspace_id: str | None = None
    name: str
    description: str | None = None
    report_type: str
    query: AnalyticsQueryResponse
    schedule: ReportScheduleResponse | None = None
    shares: list[ReportShareResponse] = []
    last_generated_at: datetime | None = None
    last_export_format: str | None = None
    created_at: datetime
    updated_at: datetime


class ReportJobResponse(BaseModel):
    id: str
    report_id: str | None = None
    report_type: str
    format: str
    status: str
    download_url: str | None = None
    expires_at: datetime | None = None
    error_message: str | None = None
    requested_by: str
    requested_at: datetime
    completed_at: datetime | None = None
    estimated_seconds: int | None = None
