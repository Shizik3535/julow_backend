from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.analytics.application.dto.mappers import report_to_dto
from app.context.analytics.application.dto.report_dto import ReportDTO
from app.context.analytics.application.exceptions.authorization_exceptions import (
    AnalyticsAccessDeniedException,
)
from app.context.analytics.application.ports.authorization.analytics_permission_checker_port import (
    AnalyticsPermissionCheckerPort,
)
from app.context.analytics.domain.entities.report_schedule import ReportSchedule
from app.context.analytics.domain.exceptions.report_exceptions import ReportNotFoundException
from app.context.analytics.domain.repositories.report_repository import ReportRepository
from app.context.analytics.domain.value_objects.report_frequency import ReportFrequency


class SetReportScheduleCommand(BaseCommand):
    """Установить/заменить расписание отчёта.

    `NoRecipientsException` будет выброшен, если recipients пуст.
    """

    caller_id: str
    report_id: str
    frequency: str  # ReportFrequency.value
    recipients: list[str]
    is_active: bool = True


class SetReportScheduleHandler(BaseCommandHandler[SetReportScheduleCommand, ReportDTO]):
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

    async def handle(self, command: SetReportScheduleCommand) -> ReportDTO:
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

        schedule = ReportSchedule(
            frequency=ReportFrequency(command.frequency),
            recipients=[Id.from_string(r) for r in command.recipients],
            is_active=command.is_active,
        )
        report.set_schedule(schedule)
        await self._repo.update(report)
        await self._event_bus.publish_all(report.clear_domain_events())
        return report_to_dto(report)
