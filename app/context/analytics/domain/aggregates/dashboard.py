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
from app.shared.domain.exceptions import ValidationException
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
    def create(
        cls,
        name: str,
        owner_id: Id,
        workspace_id: Id | None = None,
        description: str | None = None,
    ) -> Dashboard:
        db = cls(name=name, description=description, owner_id=owner_id, workspace_id=workspace_id)
        db._register_event(DashboardCreated(dashboard_id=str(db.id), owner_id=str(owner_id), workspace_id=str(workspace_id) if workspace_id else ""))
        return db

    @classmethod
    def create_from_template(
        cls,
        template_id: Id,
        template_name: str,
        widget_configs: list[WidgetConfig],
        owner_id: Id,
        workspace_id: Id | None = None,
        description: str | None = None,
    ) -> Dashboard:
        db = cls(
            name=template_name,
            description=description,
            owner_id=owner_id,
            workspace_id=workspace_id,
        )
        for i, config in enumerate(widget_configs):
            widget = Widget(title=config.widget_type.value, widget_type=config.widget_type, config=config, order=i)
            db.widgets.append(widget)
        # Сначала эмитим общее событие факта создания, затем уточняющее —
        # чтобы read-model/проекции, подписанные только на DashboardCreated,
        # корректно увидели дашборды, созданные из шаблона.
        db._register_event(DashboardCreated(dashboard_id=str(db.id), owner_id=str(owner_id), workspace_id=str(workspace_id) if workspace_id else ""))
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
        # Назначаем order как max+1, чтобы избежать коллизий после удалений
        # (в remove_widget мы не компактим order).
        widget.order = max((w.order for w in self.widgets), default=-1) + 1
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

    def update_widget(
        self,
        widget_id: Id,
        title: str | None = None,
        config: WidgetConfig | None = None,
        size: WidgetSize | None = None,
        position: WidgetPosition | None = None,
    ) -> None:
        widget = next((w for w in self.widgets if w.id == widget_id), None)
        if widget is None:
            raise WidgetNotFoundException(id=widget_id)
        changed = False
        if title is not None and widget.title != title:
            widget.title = title
            changed = True
        if config is not None and widget.config != config:
            widget.config = config
            changed = True
        if size is not None and widget.size != size:
            widget.size = size
            changed = True
        if position is not None and widget.position != position:
            widget.position = position
            changed = True
        if not changed:
            return
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(WidgetUpdated(dashboard_id=str(self.id), widget_id=str(widget_id)))

    def reorder_widgets(self, widget_ids: list[Id]) -> None:
        id_to_widget = {w.id: w for w in self.widgets}
        # Виджеты, не упомянутые в widget_ids, должны сохраниться — иначе
        # частичный список молча удалит их с дашборда.
        seen: set[Id] = set()
        reordered: list[Widget] = []
        for wid in widget_ids:
            if wid in seen:
                continue
            widget = id_to_widget.get(wid)
            if widget is None:
                raise WidgetNotFoundException(id=wid)
            reordered.append(widget)
            seen.add(wid)
        # Не упомянутые виджеты добавляем в конец, сохраняя исходный порядок.
        for w in self.widgets:
            if w.id not in seen:
                reordered.append(w)
        # Если итоговый порядок совпадает с текущим — событие не эмитим,
        # чтобы не плодить ложных уведомлений у подписчиков.
        if [w.id for w in reordered] == [w.id for w in self.widgets]:
            return
        for i, w in enumerate(reordered):
            w.order = i
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
        before = len(self.shares)
        self.shares = [s for s in self.shares if s.user_id != user_id]
        if len(self.shares) == before:
            return
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(DashboardUnshared(dashboard_id=str(self.id), user_id=str(user_id)))

    def set_auto_refresh(self, enabled: bool, interval_seconds: int | None = None) -> None:
        # При включении требуем интервал: иначе агрегат остался бы в
        # некорректном состоянии (enabled=True, interval=None).
        if enabled and interval_seconds is None and self.refresh_interval_seconds is None:
            raise ValidationException(
                field="interval_seconds",
                message="interval_seconds обязателен при включении auto-refresh",
            )
        if enabled and interval_seconds is not None and interval_seconds < 30:
            raise ValidationException(
                field="interval_seconds",
                message=f"interval_seconds должен быть >= 30: {interval_seconds}",
            )
        prev_enabled = self.is_auto_refresh
        prev_interval = self.refresh_interval_seconds
        self.is_auto_refresh = enabled
        if enabled and interval_seconds is not None:
            self.refresh_interval_seconds = interval_seconds
        elif not enabled:
            self.refresh_interval_seconds = None
        changed: list[str] = []
        if prev_enabled != self.is_auto_refresh:
            changed.append("is_auto_refresh")
        if prev_interval != self.refresh_interval_seconds:
            changed.append("refresh_interval_seconds")
        if not changed:
            return
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            DashboardUpdated(dashboard_id=str(self.id), changed_fields=changed)
        )

    def set_default(self) -> None:
        if self.is_default:
            return
        self.is_default = True
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(DashboardUpdated(dashboard_id=str(self.id), changed_fields=["is_default"]))

    def unset_default(self) -> None:
        if not self.is_default:
            return
        self.is_default = False
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(DashboardUpdated(dashboard_id=str(self.id), changed_fields=["is_default"]))

    def delete(self) -> None:
        # updated_at не мутируем: агрегат удаляется, фантомный update в
        # проекциях/outbox по updated_at нам не нужен.
        self._register_event(DashboardDeleted(dashboard_id=str(self.id)))
