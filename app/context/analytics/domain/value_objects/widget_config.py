from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.shared.domain.base_value_object import ValueObject
from app.context.analytics.domain.value_objects.analytics_query import AnalyticsQuery
from app.context.analytics.domain.value_objects.widget_type import WidgetType


@dataclass(frozen=True)
class WidgetConfig(ValueObject):
    """Конфигурация виджета: тип отображения + аналитический запрос.

    `query` — что и как считать (кросс-BC через DataSource → BoundedContextRef).
    `display_params` — параметры отображения (цвета, легенда, формат и т.д.),
    не влияют на данные.
    """

    widget_type: WidgetType = WidgetType.NUMBER
    query: AnalyticsQuery = field(default_factory=lambda: AnalyticsQuery(raw=True))
    display_params: dict[str, Any] = field(default_factory=dict)
