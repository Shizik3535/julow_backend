from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id

from app.context.analytics.application.dto.analytics_query_dto import AnalyticsQueryDTO
from app.context.analytics.application.dto.mappers import analytics_query_from_dto
from app.context.analytics.application.dto.report_dto import ReportJobDTO
from app.context.analytics.application.exceptions.analytics_app_exceptions import (
    AnalyticsWorkspaceNotFoundException,
    InvalidAdHocReportRequestException,
)
from app.context.analytics.application.ports.authorization.analytics_permission_checker_port import (
    AnalyticsPermissionCheckerPort,
)
from app.context.analytics.application.ports.integration.inboard.workspace_port import WorkspacePort
from app.context.analytics.application.ports.report_generation.report_generator_port import (
    ReportGeneratorPort,
)
from app.context.analytics.domain.exceptions.report_exceptions import ReportNotFoundException
from app.context.analytics.domain.repositories.report_repository import ReportRepository
from app.context.analytics.domain.value_objects.export_format import ExportFormat
from app.context.analytics.domain.value_objects.report_type import ReportType


class GenerateReportCommand(BaseCommand):
    """Команда запроса асинхронной генерации отчёта.

    Два режима:
        1. ad-hoc — указаны `report_type`, `query`, `format` (без `report_id`);
        2. by-id — указан `report_id` — берётся сохранённый отчёт, query из него.
    """

    caller_id: str
    workspace_id: str
    format: str = "pdf"  # ExportFormat.value
    report_id: str | None = None
    report_type: str | None = None  # обязателен в ad-hoc режиме
    query: AnalyticsQueryDTO | None = None  # обязателен в ad-hoc режиме


class GenerateReportHandler(BaseCommandHandler[GenerateReportCommand, ReportJobDTO]):
    REQUIRED_PERMISSION = "analytics.report.run"

    def __init__(
        self,
        report_repo: ReportRepository,
        report_generator: ReportGeneratorPort,
        permission_checker: AnalyticsPermissionCheckerPort,
        workspace_port: WorkspacePort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._report_repo = report_repo
        self._generator = report_generator
        self._permission_checker = permission_checker
        self._workspace_port = workspace_port
        self._event_bus = event_bus

    async def handle(self, command: GenerateReportCommand) -> ReportJobDTO:
        if not await self._workspace_port.workspace_exists(command.workspace_id):
            raise AnalyticsWorkspaceNotFoundException(command.workspace_id)
        await self._permission_checker.require_permission(
            user_id=command.caller_id,
            workspace_id=command.workspace_id,
            permission=self.REQUIRED_PERMISSION,
        )

        fmt = ExportFormat(command.format)

        if command.report_id is not None:
            report = await self._report_repo.get_by_id(Id.from_string(command.report_id))
            if report is None:
                raise ReportNotFoundException(id=command.report_id)
            report_type = report.report_type
            query = report.query
            report_id_str: str | None = command.report_id
            # Факт генерации/экспорта фиксирует адаптер генератора в
            # callback'е ReportGenerationCompleted, а не application-слой —
            # иначе при ошибке воркера получим ложные ReportGenerated.
        else:
            if command.report_type is None or command.query is None:
                raise InvalidAdHocReportRequestException()
            report_type = ReportType(command.report_type)
            query = analytics_query_from_dto(command.query)
            report_id_str = None

        return await self._generator.request_generation(
            workspace_id=command.workspace_id,
            report_type=report_type,
            query=query,
            format=fmt,
            requested_by=command.caller_id,
            report_id=report_id_str,
        )
