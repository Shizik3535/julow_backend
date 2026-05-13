from __future__ import annotations

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.analytics.domain.aggregates.dashboard import Dashboard
from app.context.analytics.domain.entities.dashboard_share import DashboardShare
from app.context.analytics.domain.entities.widget import Widget
from app.context.analytics.domain.value_objects.share_access_level import ShareAccessLevel
from app.context.analytics.domain.value_objects.widget_position import WidgetPosition
from app.context.analytics.domain.value_objects.widget_size import WidgetSize
from app.context.analytics.domain.value_objects.widget_type import WidgetType
from app.context.analytics.infrastructure.persistence.mappers._query_serialization import (
    widget_config_from_json,
    widget_config_to_json,
)
from app.context.analytics.infrastructure.persistence.orm_models.dashboard_orm import (
    DashboardORM,
    DashboardShareORM,
    DashboardWidgetORM,
)


class DashboardMapper(BaseMapper[Dashboard, DashboardORM]):
    """Data Mapper: ``Dashboard`` ↔ ``DashboardORM``."""

    def to_domain(self, orm_model: DashboardORM) -> Dashboard:
        widgets = [self._widget_to_domain(w) for w in (orm_model.widgets or [])]
        shares = [self._share_to_domain(s) for s in (orm_model.shares or [])]
        return Dashboard(
            id=self._map_id(orm_model.id),
            owner_id=self._map_id(orm_model.owner_id),
            workspace_id=(
                self._map_id(orm_model.workspace_id)
                if orm_model.workspace_id
                else None
            ),
            name=orm_model.name,
            description=orm_model.description,
            widgets=widgets,
            shares=shares,
            is_auto_refresh=orm_model.is_auto_refresh,
            refresh_interval_seconds=orm_model.refresh_interval_seconds,
            is_default=orm_model.is_default,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: Dashboard) -> DashboardORM:
        orm = DashboardORM(
            id=self._map_uuid(aggregate.id),
            owner_id=self._map_uuid(aggregate.owner_id),
            workspace_id=(
                self._map_uuid(aggregate.workspace_id)
                if aggregate.workspace_id
                else None
            ),
            name=aggregate.name,
            description=aggregate.description,
            is_auto_refresh=aggregate.is_auto_refresh,
            refresh_interval_seconds=aggregate.refresh_interval_seconds,
            is_default=aggregate.is_default,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
        orm.widgets = [
            self._widget_to_orm(w, dashboard_id=aggregate.id)
            for w in aggregate.widgets
        ]
        orm.shares = [
            self._share_to_orm(s, dashboard_id=aggregate.id) for s in aggregate.shares
        ]
        return orm

    # ---- Widget ----

    def _widget_to_domain(self, orm: DashboardWidgetORM) -> Widget:
        position: WidgetPosition | None = None
        if orm.position_row is not None and orm.position_col is not None:
            position = WidgetPosition(row=orm.position_row, col=orm.position_col)
        return Widget(
            id=self._map_id(orm.id),
            title=orm.title,
            widget_type=WidgetType(orm.widget_type),
            config=widget_config_from_json(orm.config),
            order=orm.order,
            size=WidgetSize(cols=orm.size_cols, rows=orm.size_rows),
            position=position,
        )

    def _widget_to_orm(self, widget: Widget, dashboard_id: Id) -> DashboardWidgetORM:
        return DashboardWidgetORM(
            id=self._map_uuid(widget.id),
            dashboard_id=self._map_uuid(dashboard_id),
            title=widget.title,
            widget_type=widget.widget_type.value,
            config=widget_config_to_json(widget.config),
            order=widget.order,
            size_cols=widget.size.cols,
            size_rows=widget.size.rows,
            position_row=widget.position.row if widget.position else None,
            position_col=widget.position.col if widget.position else None,
        )

    # ---- Share ----

    def _share_to_domain(self, orm: DashboardShareORM) -> DashboardShare:
        return DashboardShare(
            id=self._map_id(orm.id),
            user_id=self._map_id(orm.user_id),
            access_level=ShareAccessLevel(orm.access_level),
            shared_at=orm.shared_at,
        )

    def _share_to_orm(
        self, share: DashboardShare, dashboard_id: Id
    ) -> DashboardShareORM:
        return DashboardShareORM(
            id=self._map_uuid(share.id),
            dashboard_id=self._map_uuid(dashboard_id),
            user_id=self._map_uuid(share.user_id),
            access_level=share.access_level.value,
            shared_at=share.shared_at,
        )
