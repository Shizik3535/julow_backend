from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.analytics.application.dto.dashboard_dto import DashboardDTO
from app.context.analytics.application.dto.mappers import dashboard_to_dto
from app.context.analytics.application.exceptions.analytics_app_exceptions import (
    AnalyticsWorkspaceNotFoundException,
)
from app.context.analytics.application.ports.authorization.analytics_permission_checker_port import (
    AnalyticsPermissionCheckerPort,
)
from app.context.analytics.application.ports.integration.inboard.workspace_port import WorkspacePort
from app.context.analytics.domain.aggregates.dashboard import Dashboard
from app.context.analytics.domain.repositories.dashboard_repository import DashboardRepository


class CreateDashboardCommand(BaseCommand):
    """Команда создания дашборда."""

    caller_id: str
    workspace_id: str
    name: str
    description: str | None = None


class CreateDashboardHandler(BaseCommandHandler[CreateDashboardCommand, DashboardDTO]):
    """Создание дашборда. Требует `analytics.write`."""

    REQUIRED_PERMISSION = "analytics.write"

    def __init__(
        self,
        dashboard_repo: DashboardRepository,
        permission_checker: AnalyticsPermissionCheckerPort,
        workspace_port: WorkspacePort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = dashboard_repo
        self._permission_checker = permission_checker
        self._workspace_port = workspace_port
        self._event_bus = event_bus

    async def handle(self, command: CreateDashboardCommand) -> DashboardDTO:
        if not await self._workspace_port.workspace_exists(command.workspace_id):
            raise AnalyticsWorkspaceNotFoundException(command.workspace_id)
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=command.workspace_id,
            permission=self.REQUIRED_PERMISSION,
        )
        dashboard = Dashboard.create(
            name=command.name,
            owner_id=Id.from_string(command.caller_id),
            workspace_id=Id.from_string(command.workspace_id),
            description=command.description,
        )
        await self._repo.add(dashboard)
        await self._event_bus.publish_all(dashboard.clear_domain_events())
        return dashboard_to_dto(dashboard)
