from __future__ import annotations

from typing import Any

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.analytics.application.dto.analytics_query_dto import AnalyticsQueryDTO
from app.context.analytics.application.dto.dashboard_dto import WidgetDTO
from app.context.analytics.application.dto.mappers import (
    widget_config_from_dto,
    widget_position_from_dict,
    widget_size_from_dict,
    widget_to_dto,
)
from app.context.analytics.application.exceptions.authorization_exceptions import (
    AnalyticsAccessDeniedException,
)
from app.context.analytics.application.ports.authorization.analytics_permission_checker_port import (
    AnalyticsPermissionCheckerPort,
)
from app.context.analytics.domain.entities.widget import Widget
from app.context.analytics.domain.exceptions.dashboard_exceptions import (
    DashboardNotFoundException,
)
from app.context.analytics.domain.repositories.dashboard_repository import DashboardRepository
from app.context.analytics.domain.value_objects.widget_type import WidgetType


class AddWidgetCommand(BaseCommand):
    """Добавить виджет на дашборд."""

    caller_id: str
    dashboard_id: str
    title: str
    widget_type: str  # WidgetType.value
    query: AnalyticsQueryDTO
    size: dict[str, int] | None = None  # {"cols", "rows"}
    position: dict[str, int] | None = None
    display_params: dict[str, Any] | None = None


class AddWidgetHandler(BaseCommandHandler[AddWidgetCommand, WidgetDTO]):
    REQUIRED_PERMISSION = "analytics.write"

    def __init__(
        self,
        dashboard_repo: DashboardRepository,
        permission_checker: AnalyticsPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = dashboard_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: AddWidgetCommand) -> WidgetDTO:
        dashboard = await self._repo.get_by_id(Id.from_string(command.dashboard_id))
        if dashboard is None:
            raise DashboardNotFoundException(id=command.dashboard_id)
        if dashboard.workspace_id is not None:
            await self._permission_checker.require_permission(
                user_id=command.caller_id,
                workspace_id=str(dashboard.workspace_id),
                permission=self.REQUIRED_PERMISSION,
            )
        elif str(dashboard.owner_id) != command.caller_id:
            raise AnalyticsAccessDeniedException("dashboard", command.dashboard_id)

        widget_type = WidgetType(command.widget_type)
        widget = Widget(
            title=command.title,
            widget_type=widget_type,
            config=widget_config_from_dto(
                widget_type=widget_type,
                query_dto=command.query,
                display_params=command.display_params,
            ),
            # order назначает агрегат (max+1), чтобы избежать коллизий после remove_widget.
            size=widget_size_from_dict(command.size),
            position=widget_position_from_dict(command.position),
        )
        dashboard.add_widget(widget)
        await self._repo.update(dashboard)
        await self._event_bus.publish_all(dashboard.clear_domain_events())
        return widget_to_dto(widget)
