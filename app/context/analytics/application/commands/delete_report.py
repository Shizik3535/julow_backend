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
from app.context.analytics.domain.exceptions.report_exceptions import ReportNotFoundException
from app.context.analytics.domain.repositories.report_repository import ReportRepository


class DeleteReportCommand(BaseCommand):
    """Команда удаления отчёта."""

    caller_id: str
    report_id: str


class DeleteReportHandler(BaseCommandHandler[DeleteReportCommand, None]):
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

    async def handle(self, command: DeleteReportCommand) -> None:
        report = await self._repo.get_by_id(Id.from_string(command.report_id))
        if report is None:
            raise ReportNotFoundException(id=command.report_id)
        if report.workspace_id is not None:
            has_perm = await self._permission_checker.has_permission(
                user_id=command.caller_id,
                workspace_id=str(report.workspace_id),
                permission=self.REQUIRED_PERMISSION,
            )
            if not has_perm and str(report.owner_id) != command.caller_id:
                raise AnalyticsAccessDeniedException("report", command.report_id)
        elif str(report.owner_id) != command.caller_id:
            raise AnalyticsAccessDeniedException("report", command.report_id)

        report.delete()
        events = report.clear_domain_events()
        await self._repo.delete(report.id)
        await self._event_bus.publish_all(events)
