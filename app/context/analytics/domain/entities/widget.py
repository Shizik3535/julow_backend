from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_entity import BaseEntity
from app.context.analytics.domain.value_objects.widget_type import WidgetType
from app.context.analytics.domain.value_objects.widget_config import WidgetConfig
from app.context.analytics.domain.value_objects.widget_size import WidgetSize
from app.context.analytics.domain.value_objects.widget_position import WidgetPosition


@dataclass
class Widget(BaseEntity):
    """Сущность виджета дашборда."""

    title: str = ""
    widget_type: WidgetType = WidgetType.NUMBER
    config: WidgetConfig | None = None
    order: int = 0
    size: WidgetSize = field(default_factory=WidgetSize)
    position: WidgetPosition | None = None
