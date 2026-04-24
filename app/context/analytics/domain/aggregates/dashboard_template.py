from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.context.analytics.domain.value_objects.widget_config import WidgetConfig
from app.context.analytics.domain.exceptions.dashboard_exceptions import CannotDeleteSystemTemplateException


@dataclass
class DashboardTemplate(AggregateRoot):
    """Корень агрегата шаблона дашборда (Analytics BC)."""

    name: str = ""
    description: str | None = None
    widget_configs: list[WidgetConfig] = field(default_factory=list)
    is_system: bool = False
    is_deleted: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @classmethod
    def create_system(cls, name: str, widget_configs: list[WidgetConfig], description: str | None = None) -> DashboardTemplate:
        return cls(name=name, widget_configs=widget_configs, description=description, is_system=True)

    @classmethod
    def create_custom(cls, name: str, widget_configs: list[WidgetConfig], description: str | None = None) -> DashboardTemplate:
        return cls(name=name, widget_configs=widget_configs, description=description, is_system=False)

    def update(self, name: str | None = None, description: str | None = None, widget_configs: list[WidgetConfig] | None = None) -> None:
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if widget_configs is not None:
            self.widget_configs = widget_configs
        self.updated_at = datetime.now(tz=timezone.utc)

    def assert_deletable(self) -> None:
        if self.is_system:
            raise CannotDeleteSystemTemplateException(name=self.name)

    def mark_deleted(self) -> None:
        self.assert_deletable()
        self.is_deleted = True
        self.updated_at = datetime.now(tz=timezone.utc)
