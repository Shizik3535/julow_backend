from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.analytics.application.dto.report_dto import ReportJobDTO
from app.context.analytics.application.exceptions.analytics_app_exceptions import (
    ReportScheduleRequiredException,
    ReportWorkspaceRequiredException,
)
from app.context.analytics.application.exceptions.authorization_exceptions import (
    AnalyticsAccessDeniedException,
)
from app.context.analytics.application.ports.authorization.analytics_permission_checker_port import (
    AnalyticsPermissionCheckerPort,
)
from app.context.analytics.application.ports.report_generation.report_generator_port import (
    ReportGeneratorPort,
)
from app.context.analytics.domain.exceptions.report_exceptions import ReportNotFoundException
from app.context.analytics.domain.repositories.report_repository import ReportRepository


class SendReportNowCommand(BaseCommand):
    """Немедленная отправка scheduled-отчёта получателям."""

    caller_id: str
    report_id: str


class SendReportNowHandler(BaseCommandHandler[SendReportNowCommand, ReportJobDTO]):
    REQUIRED_PERMISSION = "analytics.report.run"

    def __init__(
        self,
        report_repo: ReportRepository,
        report_generator: ReportGeneratorPort,
        permission_checker: AnalyticsPermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._repo = report_repo
        self._generator = report_generator
        self._permission_checker = permission_checker

    async def handle(self, command: SendReportNowCommand) -> ReportJobDTO:
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
        # "Send now" имеет смысл только для отчётов с расписанием — иначе нет
        # списка получателей, и поведение генератора неопределено.
        if report.schedule is None or not report.schedule.recipients:
            raise ReportScheduleRequiredException(command.report_id)
        if report.workspace_id is None:
            # Workspace-less отчёты не могут рассылаться через scheduled-канал.
            raise ReportWorkspaceRequiredException(command.report_id)
        return await self._generator.send_scheduled_now(
            workspace_id=str(report.workspace_id),
            report_id=command.report_id,
            requested_by=command.caller_id,
        )
