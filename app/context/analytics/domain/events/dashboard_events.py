from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_domain_event import BaseDomainEvent
from app.context.analytics.domain.value_objects.widget_type import WidgetType
from app.context.analytics.domain.value_objects.share_access_level import ShareAccessLevel


@dataclass(frozen=True)
class DashboardCreated(BaseDomainEvent):
    dashboard_id: str = ""
    owner_id: str = ""
    workspace_id: str = ""


@dataclass(frozen=True)
class DashboardCreatedFromTemplate(BaseDomainEvent):
    dashboard_id: str = ""
    template_id: str = ""


@dataclass(frozen=True)
class DashboardUpdated(BaseDomainEvent):
    dashboard_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DashboardDeleted(BaseDomainEvent):
    dashboard_id: str = ""


@dataclass(frozen=True)
class DashboardShared(BaseDomainEvent):
    dashboard_id: str = ""
    user_id: str = ""
    access_level: ShareAccessLevel = ShareAccessLevel.VIEW


@dataclass(frozen=True)
class DashboardUnshared(BaseDomainEvent):
    dashboard_id: str = ""
    user_id: str = ""


@dataclass(frozen=True)
class WidgetAdded(BaseDomainEvent):
    dashboard_id: str = ""
    widget_id: str = ""
    widget_type: WidgetType = WidgetType.NUMBER


@dataclass(frozen=True)
class WidgetUpdated(BaseDomainEvent):
    dashboard_id: str = ""
    widget_id: str = ""


@dataclass(frozen=True)
class WidgetRemoved(BaseDomainEvent):
    dashboard_id: str = ""
    widget_id: str = ""


@dataclass(frozen=True)
class WidgetReordered(BaseDomainEvent):
    dashboard_id: str = ""
