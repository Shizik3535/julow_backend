from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.analytics.application.dto.analytics_query_dto import AnalyticsQueryDTO
from app.context.analytics.application.dto.mappers import analytics_query_from_dto, report_to_dto
from app.context.analytics.application.dto.report_dto import ReportDTO
from app.context.analytics.application.exceptions.authorization_exceptions import (
    AnalyticsAccessDeniedException,
)
from app.context.analytics.application.ports.authorization.analytics_permission_checker_port import (
    AnalyticsPermissionCheckerPort,
)
from app.context.analytics.domain.exceptions.report_exceptions import ReportNotFoundException
from app.context.analytics.domain.repositories.report_repository import ReportRepository


class UpdateReportCommand(BaseCommand):
    """Команда обновления отчёта: name/description и/или query."""

    caller_id: str
    report_id: str
    name: str | None = None
    description: str | None = None
    query: AnalyticsQueryDTO | None = None


class UpdateReportHandler(BaseCommandHandler[UpdateReportCommand, ReportDTO]):
    REQUIRED_PERMISSION = "analytics.report.write"

    def __init__(
        self,
        report_repo: ReportRepository,
        permission_checker: AnalyticsPermissionCheckerPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = report_repo
        self._permission_checker = permission_checker
        self._event_bus = event_bus

    async def handle(self, command: UpdateReportCommand) -> ReportDTO:
        report = await self._repo.get_by_id(Id.from_string(command.report_id))
        if report is None:
            raise ReportNotFoundException(id=command.report_id)
        if report.workspace_id is not None:
            await self._permission_checker.require_permission(
                user_id=command.caller_id,
                workspace_id=str(report.workspace_id),
                permission=self.REQUIRED_PERMISSION,
            )
        elif str(report.owner_id) != command.caller_id:
            raise AnalyticsAccessDeniedException("report", command.report_id)

        report.update_info(name=command.name, description=command.description)
        if command.query is not None:
            report.update_query(analytics_query_from_dto(command.query))

        await self._repo.update(report)
        await self._event_bus.publish_all(report.clear_domain_events())
        return report_to_dto(report)
