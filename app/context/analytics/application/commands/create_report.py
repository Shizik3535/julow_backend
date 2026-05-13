from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.analytics.application.dto.analytics_query_dto import AnalyticsQueryDTO
from app.context.analytics.application.dto.mappers import analytics_query_from_dto, report_to_dto
from app.context.analytics.application.dto.report_dto import ReportDTO
from app.context.analytics.application.exceptions.analytics_app_exceptions import (
    AnalyticsWorkspaceNotFoundException,
)
from app.context.analytics.application.ports.authorization.analytics_permission_checker_port import (
    AnalyticsPermissionCheckerPort,
)
from app.context.analytics.application.ports.integration.inboard.workspace_port import WorkspacePort
from app.context.analytics.domain.aggregates.report import Report
from app.context.analytics.domain.repositories.report_repository import ReportRepository
from app.context.analytics.domain.value_objects.report_type import ReportType


class CreateReportCommand(BaseCommand):
    """Команда создания отчёта (без расписания)."""

    caller_id: str
    workspace_id: str
    name: str
    report_type: str  # ReportType.value
    query: AnalyticsQueryDTO
    description: str | None = None


class CreateReportHandler(BaseCommandHandler[CreateReportCommand, ReportDTO]):
    REQUIRED_PERMISSION = "analytics.report.write"

    def __init__(
        self,
        report_repo: ReportRepository,
        permission_checker: AnalyticsPermissionCheckerPort,
        workspace_port: WorkspacePort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = report_repo
        self._permission_checker = permission_checker
        self._workspace_port = workspace_port
        self._event_bus = event_bus

    async def handle(self, command: CreateReportCommand) -> ReportDTO:
        if not await self._workspace_port.workspace_exists(command.workspace_id):
            raise AnalyticsWorkspaceNotFoundException(command.workspace_id)
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=command.workspace_id,
            permission=self.REQUIRED_PERMISSION,
        )
        report = Report.create(
            name=command.name,
            report_type=ReportType(command.report_type),
            query=analytics_query_from_dto(command.query),
            owner_id=Id.from_string(command.caller_id),
            workspace_id=Id.from_string(command.workspace_id),
            description=command.description,
        )
        await self._repo.add(report)
        await self._event_bus.publish_all(report.clear_domain_events())
        return report_to_dto(report)
