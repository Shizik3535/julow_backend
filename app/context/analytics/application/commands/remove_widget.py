from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.analytics.application.exceptions.authorization_exceptions import (
    AnalyticsAccessDeniedException,
)
from app.context.analytics.application.ports.authorization.analytics_permission_checker_port import (
    AnalyticsPermissionCheckerPort,
)
from app.context.analytics.domain.exceptions.dashboard_exceptions import (
    DashboardNotFoundException,
)
from app.context.analytics.domain.repositories.dashboard_repository import DashboardRepository


class RemoveWidgetCommand(BaseCommand):
    """Удалить виджет с дашборда."""

    caller_id: str
    dashboard_id: str
    widget_id: str


class RemoveWidgetHandler(BaseCommandHandler[RemoveWidgetCommand, None]):
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

    async def handle(self, command: RemoveWidgetCommand) -> None:
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

        dashboard.remove_widget(Id.from_string(command.widget_id))
        await self._repo.update(dashboard)
        await self._event_bus.publish_all(dashboard.clear_domain_events())
