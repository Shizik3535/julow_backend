from __future__ import annotations

from datetime import datetime
from typing import Any

from app.shared.application.base_dto import BaseDTO

from app.context.analytics.application.dto.analytics_query_dto import AnalyticsQueryDTO


class WidgetDTO(BaseDTO):
    """DTO виджета дашборда."""

    id: str
    title: str
    widget_type: str
    order: int
    size: dict[str, int]  # {"cols": int, "rows": int}
    position: dict[str, int] | None = None  # {"row": int, "col": int}
    query: AnalyticsQueryDTO | None = None
    display_params: dict[str, Any] = {}


class DashboardShareDTO(BaseDTO):
    """DTO шаринга дашборда с пользователем."""

    user_id: str
    access_level: str
    shared_at: datetime


class DashboardDTO(BaseDTO):
    """DTO дашборда (Analytics BC)."""

    id: str
    owner_id: str
    workspace_id: str | None = None
    name: str
    description: str | None = None
    widgets: list[WidgetDTO] = []
    shares: list[DashboardShareDTO] = []
    is_auto_refresh: bool = False
    refresh_interval_seconds: int | None = None
    is_default: bool = False
    created_at: datetime
    updated_at: datetime


class DashboardListDTO(BaseDTO):
    """Список дашбордов."""

    items: list[DashboardDTO]
    total: int


class WidgetLayoutItemDTO(BaseDTO):
    """Один элемент массового обновления layout: id виджета + позиция/размер."""

    widget_id: str
    position: dict[str, int] | None = None
    size: dict[str, int] | None = None
