from __future__ import annotations

from datetime import datetime
from typing import Any

from app.shared.application.base_dto import BaseDTO

from app.context.analytics.application.dto.analytics_query_dto import AnalyticsQueryDTO
from app.context.analytics.application.dto.dashboard_dto import WidgetDTO


class DashboardTemplateDTO(BaseDTO):
    """DTO шаблона дашборда."""

    id: str
    workspace_id: str | None = None
    name: str
    description: str | None = None
    widgets: list[WidgetDTO] = []
    is_system: bool = False
    created_at: datetime
    updated_at: datetime


class DashboardTemplateListDTO(BaseDTO):
    items: list[DashboardTemplateDTO]
    total: int


class CustomTemplateWidgetDTO(BaseDTO):
    """DTO одного виджета внутри запроса на создание пользовательского шаблона."""

    widget_type: str  # WidgetType.value
    query: AnalyticsQueryDTO
    display_params: dict[str, Any] | None = None
