from __future__ import annotations

from datetime import datetime
from typing import Any

from app.shared.application.base_dto import BaseDTO

from app.context.analytics.application.dto.analytics_query_dto import AnalyticsQueryDTO


class ReportScheduleDTO(BaseDTO):
    """DTO расписания отчёта."""

    frequency: str  # ReportFrequency.value
    recipients: list[str] = []
    is_active: bool = True
    next_run_at: datetime | None = None
    last_run_at: datetime | None = None


class ReportShareDTO(BaseDTO):
    """DTO шаринга отчёта с пользователем."""

    user_id: str
    access_level: str
    shared_at: datetime


class ReportDTO(BaseDTO):
    """DTO отчёта (Analytics BC)."""

    id: str
    owner_id: str
    workspace_id: str | None = None
    name: str
    description: str | None = None
    report_type: str
    query: AnalyticsQueryDTO
    schedule: ReportScheduleDTO | None = None
    shares: list[ReportShareDTO] = []
    last_generated_at: datetime | None = None
    last_export_format: str | None = None
    created_at: datetime
    updated_at: datetime


class ReportListDTO(BaseDTO):
    items: list[ReportDTO]
    total: int


class ReportJobDTO(BaseDTO):
    """DTO задания на генерацию отчёта."""

    id: str
    report_id: str | None = None
    report_type: str
    format: str
    status: str  # pending/processing/completed/failed
    download_url: str | None = None
    expires_at: datetime | None = None
    error_message: str | None = None
    requested_by: str
    requested_at: datetime
    completed_at: datetime | None = None
    estimated_seconds: int | None = None
