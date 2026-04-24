from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_value_object import ValueObject
from app.context.analytics.domain.value_objects.widget_type import WidgetType
from app.context.analytics.domain.value_objects.data_source import DataSource
from app.context.analytics.domain.value_objects.filter_config import FilterConfig


@dataclass(frozen=True)
class WidgetConfig(ValueObject):
    """Конфигурация виджета."""

    widget_type: WidgetType = WidgetType.NUMBER
    data_source: DataSource = DataSource.TASK_SUMMARY
    filters: list[FilterConfig] = field(default_factory=list)
    parameters: dict[str, str] | None = None
