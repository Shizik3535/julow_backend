from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.context.analytics.domain.value_objects.widget_type import WidgetType
from app.context.analytics.domain.value_objects.widget_config import WidgetConfig
from app.context.analytics.domain.value_objects.widget_size import WidgetSize
from app.context.analytics.domain.value_objects.widget_position import WidgetPosition
from app.context.analytics.domain.value_objects.share_access_level import ShareAccessLevel
from app.context.analytics.domain.entities.widget import Widget
from app.context.analytics.domain.entities.dashboard_share import DashboardShare
from app.context.analytics.domain.events.dashboard_events import (
    DashboardCreated,
    DashboardCreatedFromTemplate,
    DashboardUpdated,
    DashboardDeleted,
    DashboardShared,
    DashboardUnshared,
    WidgetAdded,
    WidgetUpdated,
    WidgetRemoved,
    WidgetReordered,
)
from app.context.analytics.domain.exceptions.dashboard_exceptions import (
    WidgetNotFoundException,
    DuplicateShareException,
    CannotShareWithSelfException,
)


@dataclass
class Dashboard(AggregateRoot):
    """Корень агрегата дашборда (Analytics BC)."""

    owner_id: Id = field(default_factory=Id.generate)
    workspace_id: Id | None = None
    name: str = ""
    description: str | None = None
    widgets: list[Widget] = field(default_factory=list)
    shares: list[DashboardShare] = field(default_factory=list)
    is_auto_refresh: bool = False
    refresh_interval_seconds: int | None = None
    is_default: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @classmethod
    def create(cls, name: str, owner_id: Id, workspace_id: Id | None = None) -> Dashboard:
        db = cls(name=name, owner_id=owner_id, workspace_id=workspace_id)
        db._register_event(DashboardCreated(dashboard_id=str(db.id), owner_id=str(owner_id), workspace_id=str(workspace_id) if workspace_id else ""))
        return db

    @classmethod
    def create_from_template(cls, template_id: Id, template_name: str, widget_configs: list[WidgetConfig], owner_id: Id, workspace_id: Id | None = None) -> Dashboard:
        db = cls(name=template_name, owner_id=owner_id, workspace_id=workspace_id)
        for i, config in enumerate(widget_configs):
            widget = Widget(title=config.widget_type.value, widget_type=config.widget_type, config=config, order=i)
            db.widgets.append(widget)
        db._register_event(DashboardCreatedFromTemplate(dashboard_id=str(db.id), template_id=str(template_id)))
        return db

    def update_info(self, name: str | None = None, description: str | None = None) -> None:
        changed: list[str] = []
        if name is not None and self.name != name:
            self.name = name
            changed.append("name")
        if description is not None and self.description != description:
            self.description = description
            changed.append("description")
        if changed:
            self.updated_at = datetime.now(tz=timezone.utc)
            self._register_event(DashboardUpdated(dashboard_id=str(self.id), changed_fields=changed))

    def add_widget(self, widget: Widget) -> None:
        self.widgets.append(widget)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(WidgetAdded(dashboard_id=str(self.id), widget_id=str(widget.id), widget_type=widget.widget_type))

    def remove_widget(self, widget_id: Id) -> None:
        widget = next((w for w in self.widgets if w.id == widget_id), None)
        if widget is None:
            raise WidgetNotFoundException(id=widget_id)
        self.widgets.remove(widget)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(WidgetRemoved(dashboard_id=str(self.id), widget_id=str(widget_id)))

    def update_widget(self, widget_id: Id, config: WidgetConfig | None = None, size: WidgetSize | None = None, position: WidgetPosition | None = None) -> None:
        widget = next((w for w in self.widgets if w.id == widget_id), None)
        if widget is None:
            raise WidgetNotFoundException(id=widget_id)
        if config is not None:
            widget.config = config
        if size is not None:
            widget.size = size
        if position is not None:
            widget.position = position
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(WidgetUpdated(dashboard_id=str(self.id), widget_id=str(widget_id)))

    def reorder_widgets(self, widget_ids: list[Id]) -> None:
        id_to_widget = {w.id: w for w in self.widgets}
        reordered = []
        for i, wid in enumerate(widget_ids):
            if wid in id_to_widget:
                id_to_widget[wid].order = i
                reordered.append(id_to_widget[wid])
        self.widgets = reordered
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(WidgetReordered(dashboard_id=str(self.id)))

    def share(self, user_id: Id, access_level: ShareAccessLevel) -> None:
        if user_id == self.owner_id:
            raise CannotShareWithSelfException()
        if any(s.user_id == user_id for s in self.shares):
            raise DuplicateShareException()
        share = DashboardShare(user_id=user_id, access_level=access_level)
        self.shares.append(share)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(DashboardShared(dashboard_id=str(self.id), user_id=str(user_id), access_level=access_level))

    def unshare(self, user_id: Id) -> None:
        self.shares = [s for s in self.shares if s.user_id != user_id]
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(DashboardUnshared(dashboard_id=str(self.id), user_id=str(user_id)))

    def set_auto_refresh(self, enabled: bool, interval_seconds: int | None = None) -> None:
        self.is_auto_refresh = enabled
        if enabled and interval_seconds is not None:
            self.refresh_interval_seconds = max(30, interval_seconds)
        elif not enabled:
            self.refresh_interval_seconds = None
        self.updated_at = datetime.now(tz=timezone.utc)

    def set_default(self) -> None:
        self.is_default = True
        self.updated_at = datetime.now(tz=timezone.utc)

    def unset_default(self) -> None:
        self.is_default = False
        self.updated_at = datetime.now(tz=timezone.utc)

    def delete(self) -> None:
        self._register_event(DashboardDeleted(dashboard_id=str(self.id)))
