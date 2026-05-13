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


class DeleteDashboardCommand(BaseCommand):
    """Команда удаления дашборда. Удалять может только владелец или admin."""

    caller_id: str
    dashboard_id: str


class DeleteDashboardHandler(BaseCommandHandler[DeleteDashboardCommand, None]):
    REQUIRED_PERMISSION = "analytics.delete"

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

    async def handle(self, command: DeleteDashboardCommand) -> None:
        dashboard = await self._repo.get_by_id(Id.from_string(command.dashboard_id))
        if dashboard is None:
            raise DashboardNotFoundException(id=command.dashboard_id)
        if dashboard.workspace_id is not None:
            has_admin = await self._permission_checker.has_permission(
                user_id=command.caller_id,
                workspace_id=str(dashboard.workspace_id),
                permission=self.REQUIRED_PERMISSION,
            )
            if not has_admin and str(dashboard.owner_id) != command.caller_id:
                raise AnalyticsAccessDeniedException("dashboard", command.dashboard_id)
        elif str(dashboard.owner_id) != command.caller_id:
            raise AnalyticsAccessDeniedException("dashboard", command.dashboard_id)

        dashboard.delete()
        events = dashboard.clear_domain_events()
        await self._repo.delete(dashboard.id)
        await self._event_bus.publish_all(events)
