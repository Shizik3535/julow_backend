from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.analytics.application.dto.dashboard_template_dto import (
    CustomTemplateWidgetDTO,
    DashboardTemplateDTO,
)
from app.context.analytics.application.dto.mappers import (
    analytics_query_from_dto,
    dashboard_template_to_dto,
)
from app.context.analytics.application.ports.authorization.analytics_permission_checker_port import (
    AnalyticsPermissionCheckerPort,
)
from app.context.analytics.domain.aggregates.dashboard_template import DashboardTemplate
from app.context.analytics.domain.repositories.dashboard_template_repository import (
    DashboardTemplateRepository,
)
from app.context.analytics.domain.value_objects.widget_config import WidgetConfig
from app.context.analytics.domain.value_objects.widget_type import WidgetType


class CreateCustomTemplateCommand(BaseCommand):
    """Создать пользовательский шаблон дашборда (is_system=False)."""

    caller_id: str
    workspace_id: str
    name: str
    description: str | None = None
    widgets: list[CustomTemplateWidgetDTO]


class CreateCustomTemplateHandler(
    BaseCommandHandler[CreateCustomTemplateCommand, DashboardTemplateDTO]
):
    REQUIRED_PERMISSION = "analytics.admin"

    def __init__(
        self,
        template_repo: DashboardTemplateRepository,
        permission_checker: AnalyticsPermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._repo = template_repo
        self._permission_checker = permission_checker

    async def handle(self, command: CreateCustomTemplateCommand) -> DashboardTemplateDTO:
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=command.workspace_id,
            permission=self.REQUIRED_PERMISSION,
        )

        widget_configs = [
            WidgetConfig(
                widget_type=WidgetType(w.widget_type),
                query=analytics_query_from_dto(w.query),
                display_params=w.display_params or {},
            )
            for w in command.widgets
        ]
        template = DashboardTemplate.create_custom(
            name=command.name,
            widget_configs=widget_configs,
            description=command.description,
            workspace_id=Id.from_string(command.workspace_id),
        )
        await self._repo.add(template)
        return dashboard_template_to_dto(template)
