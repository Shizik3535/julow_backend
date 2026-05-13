from __future__ import annotations

from app.core.logging import get_logger
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.analytics.domain.aggregates.dashboard_template import DashboardTemplate
from app.context.analytics.domain.value_objects.widget_config import WidgetConfig
from app.context.analytics.infrastructure.persistence.mappers._query_serialization import (
    widget_config_from_json,
    widget_config_to_json,
)
from app.context.analytics.infrastructure.persistence.orm_models.dashboard_template_orm import (
    DashboardTemplateORM,
)

logger = get_logger(__name__)


class DashboardTemplateMapper(BaseMapper[DashboardTemplate, DashboardTemplateORM]):
    """Data Mapper: ``DashboardTemplate`` ↔ ``DashboardTemplateORM``."""

    def to_domain(self, orm_model: DashboardTemplateORM) -> DashboardTemplate:
        widget_configs: list[WidgetConfig] = []
        for index, cfg in enumerate(orm_model.widget_configs or []):
            wc = widget_config_from_json(cfg)
            if wc is None:
                # JSONB-массив никогда не должен содержать пустых элементов:
                # это либо повреждение данных, либо несовместимая запись.
                # Лучше показать ошибку в логах, чем молча терять виджет.
                logger.warning(
                    "Dashboard template has unparseable widget config",
                    template_id=str(orm_model.id),
                    index=index,
                    payload=cfg,
                )
                continue
            widget_configs.append(wc)
        return DashboardTemplate(
            id=self._map_id(orm_model.id),
            name=orm_model.name,
            description=orm_model.description,
            widget_configs=widget_configs,
            is_system=orm_model.is_system,
            workspace_id=(
                self._map_id(orm_model.workspace_id)
                if orm_model.workspace_id is not None
                else None
            ),
            is_deleted=orm_model.is_deleted,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: DashboardTemplate) -> DashboardTemplateORM:
        # widget_configs типизирован как list[WidgetConfig] (без None),
        # а widget_config_to_json возвращает None только для None на входе,
        # так что проверка `is not None` была мертвой.
        serialized: list[dict] = [
            widget_config_to_json(cfg) for cfg in aggregate.widget_configs  # type: ignore[misc]
        ]
        return DashboardTemplateORM(
            id=self._map_uuid(aggregate.id),
            workspace_id=(
                self._map_uuid(aggregate.workspace_id)
                if aggregate.workspace_id is not None
                else None
            ),
            name=aggregate.name,
            description=aggregate.description,
            widget_configs=serialized,
            is_system=aggregate.is_system,
            is_deleted=aggregate.is_deleted,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
