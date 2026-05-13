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
from app.context.analytics.domain.exceptions.dashboard_exceptions import (
    DashboardTemplateNotFoundException,
)
from app.context.analytics.domain.repositories.dashboard_repository import DashboardRepository
from app.context.analytics.domain.repositories.dashboard_template_repository import (
    DashboardTemplateRepository,
)


class CreateDashboardFromTemplateCommand(BaseCommand):
    """Команда создания дашборда из шаблона."""

    caller_id: str
    workspace_id: str
    template_id: str
    name: str | None = None  # если None — используется имя шаблона
    description: str | None = None  # если None — берётся описание шаблона


class CreateDashboardFromTemplateHandler(
    BaseCommandHandler[CreateDashboardFromTemplateCommand, DashboardDTO]
):
    REQUIRED_PERMISSION = "analytics.write"

    def __init__(
        self,
        dashboard_repo: DashboardRepository,
        template_repo: DashboardTemplateRepository,
        permission_checker: AnalyticsPermissionCheckerPort,
        workspace_port: WorkspacePort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._dashboard_repo = dashboard_repo
        self._template_repo = template_repo
        self._permission_checker = permission_checker
        self._workspace_port = workspace_port
        self._event_bus = event_bus

    async def handle(self, command: CreateDashboardFromTemplateCommand) -> DashboardDTO:
        if not await self._workspace_port.workspace_exists(command.workspace_id):
            raise AnalyticsWorkspaceNotFoundException(command.workspace_id)
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=command.workspace_id,
            permission=self.REQUIRED_PERMISSION,
        )
        template = await self._template_repo.get_by_id(Id.from_string(command.template_id))
        if template is None:
            raise DashboardTemplateNotFoundException(id=command.template_id)

        dashboard = Dashboard.create_from_template(
            template_id=template.id,
            template_name=command.name or template.name,
            widget_configs=template.widget_configs,
            owner_id=Id.from_string(command.caller_id),
            workspace_id=Id.from_string(command.workspace_id),
            description=command.description if command.description is not None else template.description,
        )
        await self._dashboard_repo.add(dashboard)
        await self._event_bus.publish_all(dashboard.clear_domain_events())
        return dashboard_to_dto(dashboard)
