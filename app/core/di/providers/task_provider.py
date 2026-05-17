"""DI-провайдеры для Task BC."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.context.identity.application.ports.integration.outboard.identity_user_provider import (
    IdentityUserProvider,
)
from app.context.project.application.ports.integration.outboard.board_provider import (
    BoardProvider,
)
from app.context.project.application.ports.integration.outboard.epic_provider import (
    EpicProvider,
)
from app.context.project.application.ports.integration.outboard.project_membership_provider import (
    ProjectMembershipProvider,
)
from app.context.project.application.ports.integration.outboard.project_permission_provider import (
    ProjectPermissionProvider,
)
from app.context.project.application.ports.integration.outboard.project_provider import (
    ProjectProvider,
)
from app.context.project.application.ports.integration.outboard.sprint_provider import (
    SprintProvider,
)
from app.context.notification.application.ports.integration.outboard.reminder_window_provider import (
    ReminderWindowProvider,
)
from app.context.task.application.ports.authorization.task_permission_checker_port import (
    TaskPermissionCheckerPort,
)
from app.context.task.application.ports.integration.inboard.board_port import BoardPort
from app.context.task.application.ports.integration.inboard.epic_port import EpicPort
from app.context.task.application.ports.integration.inboard.identity_user_port import (
    IdentityUserPort,
)
from app.context.task.application.ports.integration.inboard.project_membership_port import (
    ProjectMembershipPort,
)
from app.context.task.application.ports.integration.inboard.project_port import ProjectPort
from app.context.task.application.ports.integration.inboard.sprint_port import SprintPort
from app.context.task.application.ports.integration.inboard.reminder_window_port import ReminderWindowPort
from app.context.task.application.ports.integration.outboard.task_analytics_provider import (
    TaskAnalyticsProvider,
)
from app.context.task.application.ports.integration.outboard.task_provider import TaskProvider
from app.context.task.application.ports.integration.outboard.task_participant_provider import TaskParticipantProvider
from app.context.task.domain.repositories.changelog_repository import ChangelogRepository
from app.context.task.domain.repositories.task_repository import TaskRepository
from app.context.task.domain.repositories.task_template_repository import TaskTemplateRepository
from app.context.task.infrastructure.integration.inboard.board_adapter import BoardAdapter
from app.context.task.infrastructure.integration.inboard.epic_adapter import EpicAdapter
from app.context.filestorage.application.ports.integration.outboard.file_attachment_provider import (
    FileAttachmentProvider,
)
from app.context.task.application.ports.integration.inboard.file_attachment_port import (
    FileAttachmentPort,
)
from app.context.task.infrastructure.integration.inboard.file_attachment_adapter import (
    FileAttachmentAdapter as TaskFileAttachmentAdapter,
)
from app.context.task.infrastructure.integration.inboard.identity_user_adapter import (
    IdentityUserAdapter,
)
from app.context.task.infrastructure.integration.inboard.project_adapter import ProjectAdapter
from app.context.task.infrastructure.integration.inboard.project_membership_adapter import (
    ProjectMembershipAdapter,
)
from app.context.task.infrastructure.integration.inboard.sprint_adapter import SprintAdapter
from app.context.task.infrastructure.integration.inboard.reminder_window_adapter import (
    ReminderWindowAdapter,
)
from app.context.task.infrastructure.authorization.task_role_based_permission_checker import (
    TaskRoleBasedPermissionChecker,
)
from app.context.task.infrastructure.integration.outboard.sql_task_analytics_adapter import (
    SqlTaskAnalyticsAdapter,
)
from app.context.task.infrastructure.integration.outboard.task_provider_adapter import (
    TaskProviderAdapter,
)
from app.context.task.infrastructure.integration.outboard.task_participant_provider_adapter import (
    TaskParticipantProviderAdapter,
)
from app.context.task.infrastructure.persistence.mappers.changelog_mapper import ChangelogMapper
from app.context.task.infrastructure.persistence.mappers.task_mapper import TaskMapper
from app.context.task.infrastructure.persistence.mappers.task_template_mapper import (
    TaskTemplateMapper,
)
from app.context.task.infrastructure.persistence.repositories.sql_changelog_repository import (
    SqlChangelogRepository,
)
from app.context.task.infrastructure.persistence.repositories.sql_task_repository import (
    SqlTaskRepository,
)
from app.context.task.infrastructure.persistence.repositories.sql_task_template_repository import (
    SqlTaskTemplateRepository,
)


# --- Mappers ---

def create_task_mapper() -> TaskMapper:
    """Создать TaskMapper."""
    return TaskMapper()


def create_task_template_mapper() -> TaskTemplateMapper:
    """Создать TaskTemplateMapper."""
    return TaskTemplateMapper()


def create_changelog_mapper() -> ChangelogMapper:
    """Создать ChangelogMapper."""
    return ChangelogMapper()


# --- Repositories ---

def create_task_repository(session: AsyncSession, mapper: TaskMapper) -> TaskRepository:
    """Создать SqlTaskRepository."""
    return SqlTaskRepository(session=session, mapper=mapper)


def create_task_template_repository(
    session: AsyncSession, mapper: TaskTemplateMapper,
) -> TaskTemplateRepository:
    """Создать SqlTaskTemplateRepository."""
    return SqlTaskTemplateRepository(session=session, mapper=mapper)


def create_changelog_repository(
    session: AsyncSession, mapper: ChangelogMapper,
) -> ChangelogRepository:
    """Создать SqlChangelogRepository."""
    return SqlChangelogRepository(session=session, mapper=mapper)


# --- Outboard adapters ---

def create_task_provider_adapter(repo: TaskRepository) -> TaskProvider:
    """Создать TaskProviderAdapter (outboard)."""
    return TaskProviderAdapter(repo=repo)


def create_task_participant_provider_adapter(repo: TaskRepository) -> TaskParticipantProvider:
    """Создать TaskParticipantProviderAdapter (outboard)."""
    return TaskParticipantProviderAdapter(repo=repo)


def create_task_analytics_adapter(session_factory: async_sessionmaker[AsyncSession]) -> TaskAnalyticsProvider:
    """Создать SqlTaskAnalyticsAdapter (outboard) для Analytics BC."""
    return SqlTaskAnalyticsAdapter(session_factory=session_factory)


# --- Inboard adapters ---

def create_task_file_attachment_adapter(
    file_attachment_provider: FileAttachmentProvider,
) -> FileAttachmentPort:
    """Создать FileAttachmentAdapter (inboard) для Task BC.

    Делегирует в outboard FileStorage BC (FileAttachmentProvider).
    """
    return TaskFileAttachmentAdapter(provider=file_attachment_provider)


def create_task_identity_user_adapter(
    identity_user_provider: IdentityUserProvider,
) -> IdentityUserPort:
    """Создать IdentityUserAdapter (inboard) для Task BC."""
    return IdentityUserAdapter(identity_user_provider=identity_user_provider)


def create_task_project_adapter(project_provider: ProjectProvider) -> ProjectPort:
    """Создать ProjectAdapter (inboard) для Task BC."""
    return ProjectAdapter(project_provider=project_provider)


def create_task_project_membership_adapter(
    project_membership_provider: ProjectMembershipProvider,
) -> ProjectMembershipPort:
    """Создать ProjectMembershipAdapter (inboard) для Task BC."""
    return ProjectMembershipAdapter(project_membership_provider=project_membership_provider)


def create_task_board_adapter(board_provider: BoardProvider) -> BoardPort:
    """Создать BoardAdapter (inboard) для Task BC."""
    return BoardAdapter(board_provider=board_provider)


def create_task_sprint_adapter(sprint_provider: SprintProvider) -> SprintPort:
    """Создать SprintAdapter (inboard) для Task BC."""
    return SprintAdapter(sprint_provider=sprint_provider)


def create_task_reminder_window_adapter(
    reminder_window_provider: ReminderWindowProvider,
) -> ReminderWindowPort:
    """Создать ReminderWindowAdapter (inboard) для Task BC."""
    return ReminderWindowAdapter(reminder_window_provider=reminder_window_provider)


def create_task_epic_adapter(epic_provider: EpicProvider) -> EpicPort:
    """Создать EpicAdapter (inboard) для Task BC."""
    return EpicAdapter(epic_provider=epic_provider)


def create_task_permission_checker(
    task_repo: TaskRepository,
    project_membership_port: ProjectMembershipPort,
    project_permission_provider: ProjectPermissionProvider,
) -> TaskPermissionCheckerPort:
    """Создать TaskRoleBasedPermissionChecker (authorization)."""
    return TaskRoleBasedPermissionChecker(
        task_repo=task_repo,
        project_membership_port=project_membership_port,
        project_permission_provider=project_permission_provider,
    )
