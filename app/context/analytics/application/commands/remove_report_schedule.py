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


class RemoveReportScheduleCommand(BaseCommand):
    """Снять расписание отчёта (отчёт остаётся, расписание удаляется)."""

    caller_id: str
    report_id: str


class RemoveReportScheduleHandler(BaseCommandHandler[RemoveReportScheduleCommand, None]):
    REQUIRED_PERMISSION = "analytics.report.schedule"

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

    async def handle(self, command: RemoveReportScheduleCommand) -> None:
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

        report.remove_schedule()
        await self._repo.update(report)
        await self._event_bus.publish_all(report.clear_domain_events())


class DeactivateReportScheduleCommand(BaseCommand):
    """Деактивировать расписание отчёта (без удаления)."""

    caller_id: str
    report_id: str


class DeactivateReportScheduleHandler(
    BaseCommandHandler[DeactivateReportScheduleCommand, None]
):
    REQUIRED_PERMISSION = "analytics.report.schedule"

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

    async def handle(self, command: DeactivateReportScheduleCommand) -> None:
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

        report.deactivate_schedule()
        await self._repo.update(report)
        await self._event_bus.publish_all(report.clear_domain_events())
