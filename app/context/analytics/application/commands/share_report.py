from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.analytics.application.exceptions.analytics_app_exceptions import (
    InvalidShareAccessLevelException,
)
from app.context.analytics.application.exceptions.authorization_exceptions import (
    AnalyticsAccessDeniedException,
)
from app.context.analytics.application.ports.authorization.analytics_permission_checker_port import (
    AnalyticsPermissionCheckerPort,
)
from app.context.analytics.domain.exceptions.report_exceptions import ReportNotFoundException
from app.context.analytics.domain.repositories.report_repository import ReportRepository
from app.context.analytics.domain.value_objects.share_access_level import ShareAccessLevel


class ShareReportCommand(BaseCommand):
    """Расшарить отчёт с пользователем."""

    caller_id: str
    report_id: str
    user_id: str
    access_level: str = "view"


class ShareReportHandler(BaseCommandHandler[ShareReportCommand, None]):
    REQUIRED_PERMISSION = "analytics.share"

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

    async def handle(self, command: ShareReportCommand) -> None:
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

        try:
            access_level = ShareAccessLevel(command.access_level)
        except ValueError as e:
            raise InvalidShareAccessLevelException(command.access_level) from e
        report.share(
            user_id=Id.from_string(command.user_id),
            access_level=access_level,
        )
        await self._repo.update(report)
        await self._event_bus.publish_all(report.clear_domain_events())


class UnshareReportCommand(BaseCommand):
    caller_id: str
    report_id: str
    user_id: str


class UnshareReportHandler(BaseCommandHandler[UnshareReportCommand, None]):
    REQUIRED_PERMISSION = "analytics.share"

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

    async def handle(self, command: UnshareReportCommand) -> None:
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

        report.unshare(Id.from_string(command.user_id))
        await self._repo.update(report)
        await self._event_bus.publish_all(report.clear_domain_events())
