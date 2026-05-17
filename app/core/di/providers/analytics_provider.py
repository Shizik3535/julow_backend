"""DI providers для Analytics BC."""
from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy.ext.asyncio import AsyncSession

from app.context.analytics.application.ports.authorization.analytics_permission_checker_port import (
    AnalyticsPermissionCheckerPort,
)
from app.context.analytics.application.ports.integration.inboard.file_attachment_port import (
    FileAttachmentPort,
)
from app.context.analytics.application.ports.integration.inboard.project_analytics_port import (
    ProjectAnalyticsPort,
)
from app.context.analytics.application.ports.integration.inboard.project_port import (
    ProjectPort,
)
from app.context.analytics.application.ports.integration.inboard.sprint_port import (
    SprintPort,
)
from app.context.analytics.application.ports.integration.inboard.task_analytics_port import (
    TaskAnalyticsPort,
)
from app.context.analytics.application.ports.integration.inboard.timetracking_analytics_port import (
    TimeTrackingAnalyticsPort,
)
from app.context.analytics.application.ports.integration.inboard.workspace_analytics_port import (
    WorkspaceAnalyticsPort,
)
from app.context.analytics.application.ports.integration.inboard.workspace_port import (
    WorkspacePort,
)
from app.context.analytics.application.ports.query_execution.analytics_query_executor_port import (
    AnalyticsQueryExecutorPort,
)
from app.context.analytics.application.ports.report_generation.report_generator_port import (
    ReportGeneratorPort,
)
from app.context.analytics.application.ports.report_generation.report_render_scheduler_port import (
    ReportRenderSchedulerPort,
)
from app.context.analytics.domain.repositories.dashboard_repository import (
    DashboardRepository,
)
from app.context.analytics.domain.repositories.dashboard_template_repository import (
    DashboardTemplateRepository,
)
from app.context.analytics.domain.repositories.report_repository import ReportRepository
from app.context.analytics.infrastructure.authorization.analytics_role_based_permission_checker import (
    AnalyticsRoleBasedPermissionChecker,
)
from app.context.analytics.infrastructure.integration.inboard.file_attachment_adapter import (
    FileAttachmentAdapter,
)
from app.context.analytics.infrastructure.integration.inboard.project_adapter import (
    ProjectAdapter,
)
from app.context.analytics.infrastructure.integration.inboard.project_analytics_adapter import (
    ProjectAnalyticsAdapter,
)
from app.context.analytics.infrastructure.integration.inboard.sprint_adapter import (
    SprintAdapter,
)
from app.context.analytics.infrastructure.integration.inboard.task_analytics_adapter import (
    TaskAnalyticsAdapter,
)
from app.context.analytics.infrastructure.integration.inboard.timetracking_analytics_adapter import (
    TimeTrackingAnalyticsAdapter,
)
from app.context.analytics.infrastructure.integration.inboard.workspace_adapter import (
    WorkspaceAdapter,
)
from app.context.analytics.infrastructure.integration.inboard.workspace_analytics_adapter import (
    WorkspaceAnalyticsAdapter,
)
from app.context.analytics.infrastructure.persistence.mappers.dashboard_mapper import (
    DashboardMapper,
)
from app.context.analytics.infrastructure.persistence.mappers.dashboard_template_mapper import (
    DashboardTemplateMapper,
)
from app.context.analytics.infrastructure.persistence.mappers.report_job_mapper import (
    ReportJobMapper,
)
from app.context.analytics.infrastructure.persistence.mappers.report_mapper import (
    ReportMapper,
)
from app.context.analytics.infrastructure.persistence.repositories.sql_dashboard_repository import (
    SqlDashboardRepository,
)
from app.context.analytics.infrastructure.persistence.repositories.sql_dashboard_template_repository import (
    SqlDashboardTemplateRepository,
)
from app.context.analytics.infrastructure.persistence.repositories.sql_report_job_repository import (
    SqlReportJobRepository,
)
from app.context.analytics.infrastructure.persistence.repositories.sql_report_repository import (
    SqlReportRepository,
)
from app.context.analytics.infrastructure.query_execution.analytics_bc_resolver import (
    AnalyticsBCResolver,
)
from app.context.analytics.infrastructure.query_execution.analytics_query_executor_adapter import (
    AnalyticsQueryExecutorAdapter,
)
from app.context.analytics.infrastructure.report_generation.report_generator_adapter import (
    ReportGeneratorAdapter,
)
from app.context.analytics.infrastructure.report_generation.report_render_scheduler import (
    NoopReportRenderScheduler,
)
from app.context.analytics.infrastructure.query_execution.resolvers.project_analytics_resolver import (
    ProjectAnalyticsResolver,
)
from app.context.analytics.infrastructure.query_execution.resolvers.task_analytics_resolver import (
    TaskAnalyticsResolver,
)
from app.context.analytics.infrastructure.query_execution.resolvers.timetracking_analytics_resolver import (
    TimeTrackingAnalyticsResolver,
)
from app.context.analytics.infrastructure.query_execution.resolvers.workspace_analytics_resolver import (
    WorkspaceAnalyticsResolver,
)
from app.context.filestorage.application.ports.integration.outboard.file_attachment_provider import (
    FileAttachmentProvider,
)
from app.context.project.application.ports.integration.outboard.project_analytics_provider import (
    ProjectAnalyticsProvider,
)
from app.context.project.application.ports.integration.outboard.project_provider import (
    ProjectProvider,
)
from app.context.project.application.ports.integration.outboard.sprint_provider import (
    SprintProvider,
)
from app.context.task.application.ports.integration.outboard.task_analytics_provider import (
    TaskAnalyticsProvider,
)
from app.context.timetracking.application.ports.integration.outboard.timetracking_analytics_provider import (
    TimeTrackingAnalyticsProvider,
)
from app.context.workspace.application.ports.integration.outboard.workspace_analytics_provider import (
    WorkspaceAnalyticsProvider,
)
from app.context.workspace.application.ports.integration.outboard.workspace_membership_provider import (
    WorkspaceMembershipProvider,
)
from app.context.workspace.application.ports.integration.outboard.workspace_provider import (
    WorkspaceProvider,
)


# --- Mappers ---


def create_dashboard_mapper() -> DashboardMapper:
    """Создать DashboardMapper."""
    return DashboardMapper()


def create_dashboard_template_mapper() -> DashboardTemplateMapper:
    """Создать DashboardTemplateMapper."""
    return DashboardTemplateMapper()


def create_report_mapper() -> ReportMapper:
    """Создать ReportMapper."""
    return ReportMapper()


def create_report_job_mapper() -> ReportJobMapper:
    """Создать ReportJobMapper (инфраструктурный, без доменного агрегата)."""
    return ReportJobMapper()


# --- Repositories ---


def create_dashboard_repository(
    session: AsyncSession, mapper: DashboardMapper
) -> DashboardRepository:
    """Создать SqlDashboardRepository."""
    return SqlDashboardRepository(session=session, mapper=mapper)


def create_dashboard_template_repository(
    session: AsyncSession, mapper: DashboardTemplateMapper
) -> DashboardTemplateRepository:
    """Создать SqlDashboardTemplateRepository."""
    return SqlDashboardTemplateRepository(session=session, mapper=mapper)


def create_report_repository(
    session: AsyncSession, mapper: ReportMapper
) -> ReportRepository:
    """Создать SqlReportRepository."""
    return SqlReportRepository(session=session, mapper=mapper)


def create_report_job_repository(
    session: AsyncSession, mapper: ReportJobMapper
) -> SqlReportJobRepository:
    """Создать SqlReportJobRepository.

    Используется ``ReportGeneratorAdapter`` для управления состоянием
    asynchronous job'ов (``analytics_report_jobs``). Доменного порта нет —
    это чисто инфраструктурное состояние.
    """
    return SqlReportJobRepository(session=session, mapper=mapper)


# --- Authorization ---


def create_analytics_permission_checker(
    workspace_membership_provider: WorkspaceMembershipProvider,
) -> AnalyticsPermissionCheckerPort:
    """Создать AnalyticsRoleBasedPermissionChecker.

    Каскад workspace-роль → орг-роль делегируется в
    ``WorkspaceMembershipProvider`` (outboard Workspace BC).
    """
    return AnalyticsRoleBasedPermissionChecker(
        workspace_membership_provider=workspace_membership_provider,
    )


# --- Integration inboard adapters ---


def create_analytics_workspace_adapter(
    workspace_provider: WorkspaceProvider,
    workspace_membership_provider: WorkspaceMembershipProvider,
) -> WorkspacePort:
    """Создать WorkspaceAdapter (inboard) для Analytics BC."""
    return WorkspaceAdapter(
        workspace_provider=workspace_provider,
        workspace_membership_provider=workspace_membership_provider,
    )


def create_analytics_project_adapter(
    project_provider: ProjectProvider,
) -> ProjectPort:
    """Создать ProjectAdapter (inboard) для Analytics BC."""
    return ProjectAdapter(project_provider=project_provider)


def create_analytics_file_attachment_adapter(
    file_attachment_provider: FileAttachmentProvider,
) -> FileAttachmentPort:
    """Создать FileAttachmentAdapter (inboard) для Analytics BC.

    Делегирует загрузку файлов отчётов в FileStorage BC через outboard
    ``FileAttachmentProvider`` (учёт квоты, антивирус, события).
    """
    return FileAttachmentAdapter(provider=file_attachment_provider)


# --- Analytics inboard adapters (analytics data) ---


def create_analytics_workspace_analytics_adapter(
    workspace_analytics_provider: WorkspaceAnalyticsProvider,
) -> WorkspaceAnalyticsPort:
    """Создать WorkspaceAnalyticsAdapter (inboard) для Analytics BC."""
    return WorkspaceAnalyticsAdapter(provider=workspace_analytics_provider)


def create_analytics_project_analytics_adapter(
    project_analytics_provider: ProjectAnalyticsProvider,
) -> ProjectAnalyticsPort:
    """Создать ProjectAnalyticsAdapter (inboard) для Analytics BC."""
    return ProjectAnalyticsAdapter(provider=project_analytics_provider)


def create_analytics_task_analytics_adapter(
    task_analytics_provider: TaskAnalyticsProvider,
) -> TaskAnalyticsPort:
    """Создать TaskAnalyticsAdapter (inboard) для Analytics BC."""
    return TaskAnalyticsAdapter(provider=task_analytics_provider)


def create_analytics_timetracking_analytics_adapter(
    timetracking_analytics_provider: TimeTrackingAnalyticsProvider,
) -> TimeTrackingAnalyticsPort:
    """Создать TimeTrackingAnalyticsAdapter (inboard) для Analytics BC."""
    return TimeTrackingAnalyticsAdapter(provider=timetracking_analytics_provider)


def create_analytics_sprint_adapter(
    sprint_provider: SprintProvider,
) -> SprintPort:
    """Создать SprintAdapter (inboard) для Analytics BC."""
    return SprintAdapter(sprint_provider=sprint_provider)


# --- Analytics resolvers ---


def create_workspace_analytics_resolver(
    workspace_port: WorkspaceAnalyticsPort,
) -> WorkspaceAnalyticsResolver:
    """Создать WorkspaceAnalyticsResolver."""
    return WorkspaceAnalyticsResolver(workspace_port=workspace_port)


def create_project_analytics_resolver(
    project_port: ProjectAnalyticsPort,
    task_port: TaskAnalyticsPort,
) -> ProjectAnalyticsResolver:
    """Создать ProjectAnalyticsResolver (cross-BC: Project + Task)."""
    return ProjectAnalyticsResolver(project_port=project_port, task_port=task_port)


def create_task_analytics_resolver(
    task_port: TaskAnalyticsPort,
    sprint_port: SprintPort,
) -> TaskAnalyticsResolver:
    """Создать TaskAnalyticsResolver (cross-BC: Task + Sprint)."""
    return TaskAnalyticsResolver(task_port=task_port, sprint_port=sprint_port)


def create_timetracking_analytics_resolver(
    timetracking_port: TimeTrackingAnalyticsPort,
) -> TimeTrackingAnalyticsResolver:
    """Создать TimeTrackingAnalyticsResolver."""
    return TimeTrackingAnalyticsResolver(timetracking_port=timetracking_port)


# --- Query execution ---


def create_analytics_query_executor(
    resolvers: Iterable[AnalyticsBCResolver] | None = None,
) -> AnalyticsQueryExecutorPort:
    """Создать AnalyticsQueryExecutorAdapter.

    Резолверы регистрируются по ``bounded_context``. Если ``resolvers``
    не передан — при запросе к незарегистрированному BC адаптер вернёт
    ``UnsupportedDataSourceException``.
    """
    return AnalyticsQueryExecutorAdapter(resolvers=resolvers)


# --- Report generation ---


def create_report_render_scheduler() -> ReportRenderSchedulerPort:
    """Создать ReportRenderSchedulerPort.

    Сейчас используется ``NoopReportRenderScheduler`` (без воркера):
    задание остаётся в статусе ``pending`` до подхвата реальным
    воркером. Заменить на Celery/Arq-планировщик при добавлении
    воркера рендеринга.
    """
    return NoopReportRenderScheduler()


def create_report_generator(
    report_repo: ReportRepository,
    job_repo: SqlReportJobRepository,
    render_scheduler: ReportRenderSchedulerPort,
) -> ReportGeneratorPort:
    """Создать ReportGeneratorAdapter."""
    return ReportGeneratorAdapter(
        report_repo=report_repo,
        job_repo=job_repo,
        render_scheduler=render_scheduler,
    )
