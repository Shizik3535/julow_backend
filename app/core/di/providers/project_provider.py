"""
DI-провайдеры для Project BC.
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.context.identity.application.ports.integration.outboard.identity_user_provider import (
    IdentityUserProvider,
)
from app.context.organization.application.ports.integration.outboard.organization_membership_provider import (
    OrganizationMembershipProvider,
)
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)
from app.context.project.application.ports.integration.inboard.identity_user_port import (
    IdentityUserPort,
)
from app.context.project.application.ports.integration.inboard.organization_membership_port import (
    OrganizationMembershipPort,
)
from app.context.project.application.ports.integration.inboard.workspace_membership_port import (
    WorkspaceMembershipPort,
)
from app.context.project.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.project.application.ports.integration.inboard.reminder_window_port import ReminderWindowPort
from app.context.project.application.ports.integration.inboard.workspace_port import (
    WorkspacePort,
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
from app.context.project.application.ports.integration.outboard.project_role_provider import (
    ProjectRoleProvider,
)
from app.context.project.application.ports.integration.outboard.project_analytics_provider import (
    ProjectAnalyticsProvider,
)
from app.context.project.application.ports.integration.outboard.sprint_provider import (
    SprintProvider,
)
from app.context.project.domain.repositories.board_repository import BoardRepository
from app.context.project.domain.repositories.epic_repository import EpicRepository
from app.context.project.domain.repositories.project_membership_repository import (
    ProjectMembershipRepository,
)
from app.context.project.domain.repositories.project_repository import ProjectRepository
from app.context.project.domain.repositories.project_role_repository import ProjectRoleRepository
from app.context.project.domain.repositories.retro_template_repository import RetroTemplateRepository
from app.context.project.domain.repositories.sprint_repository import SprintRepository
from app.context.project.infrastructure.authorization.project_role_based_permission_checker import (
    ProjectRoleBasedPermissionChecker,
)
from app.context.project.infrastructure.integration.inboard.identity_user_adapter import (
    IdentityUserAdapter,
)
from app.context.project.infrastructure.integration.inboard.organization_membership_adapter import (
    OrganizationMembershipAdapter,
)
from app.context.project.infrastructure.integration.inboard.workspace_adapter import (
    WorkspaceAdapter,
)
from app.context.project.infrastructure.integration.inboard.workspace_membership_adapter import (
    WorkspaceMembershipAdapter,
)
from app.context.project.infrastructure.integration.inboard.workspace_permission_checker_adapter import (
    WorkspacePermissionCheckerAdapter,
)
from app.context.project.infrastructure.integration.inboard.reminder_window_adapter import (
    ReminderWindowAdapter,
)
from app.context.project.infrastructure.integration.outboard.board_provider_adapter import (
    BoardProviderAdapter,
)
from app.context.project.infrastructure.integration.outboard.epic_provider_adapter import (
    EpicProviderAdapter,
)
from app.context.project.infrastructure.integration.outboard.project_membership_provider_adapter import (
    ProjectMembershipProviderAdapter,
)
from app.context.project.infrastructure.integration.outboard.project_permission_provider_impl import (
    ProjectPermissionProviderImpl,
)
from app.context.project.infrastructure.integration.outboard.project_provider_adapter import (
    ProjectProviderAdapter,
)
from app.context.project.infrastructure.integration.outboard.project_role_provider_adapter import (
    ProjectRoleProviderAdapter,
)
from app.context.project.infrastructure.integration.outboard.sql_project_analytics_adapter import (
    SqlProjectAnalyticsAdapter,
)
from app.context.project.infrastructure.integration.outboard.sprint_provider_adapter import (
    SprintProviderAdapter,
)
from app.context.project.infrastructure.persistence.mappers.board_mapper import BoardMapper
from app.context.project.infrastructure.persistence.mappers.epic_mapper import EpicMapper
from app.context.project.infrastructure.persistence.mappers.project_mapper import ProjectMapper
from app.context.project.infrastructure.persistence.mappers.project_membership_mapper import (
    ProjectMembershipMapper,
)
from app.context.project.infrastructure.persistence.mappers.project_role_mapper import (
    ProjectRoleMapper,
)
from app.context.project.infrastructure.persistence.mappers.retro_template_mapper import (
    RetroTemplateMapper,
)
from app.context.project.infrastructure.persistence.mappers.sprint_mapper import SprintMapper
from app.context.project.infrastructure.persistence.repositories.sql_board_repository import (
    SqlBoardRepository,
)
from app.context.project.infrastructure.persistence.repositories.sql_epic_repository import (
    SqlEpicRepository,
)
from app.context.project.infrastructure.persistence.repositories.sql_project_membership_repository import (
    SqlProjectMembershipRepository,
)
from app.context.project.infrastructure.persistence.repositories.sql_project_repository import (
    SqlProjectRepository,
)
from app.context.project.infrastructure.persistence.repositories.sql_project_role_repository import (
    SqlProjectRoleRepository,
)
from app.context.project.infrastructure.persistence.repositories.sql_retro_template_repository import (
    SqlRetroTemplateRepository,
)
from app.context.project.infrastructure.persistence.repositories.sql_sprint_repository import (
    SqlSprintRepository,
)
from app.context.workspace.application.ports.integration.outboard.workspace_membership_provider import (
    WorkspaceMembershipProvider,
)
from app.context.notification.application.ports.integration.outboard.reminder_window_provider import (
    ReminderWindowProvider,
)
from app.context.workspace.application.ports.integration.outboard.workspace_provider import (
    WorkspaceProvider,
)


# --- Mappers ---

def create_project_mapper() -> ProjectMapper:
    """Создать ProjectMapper."""
    return ProjectMapper()


def create_board_mapper() -> BoardMapper:
    """Создать BoardMapper."""
    return BoardMapper()


def create_epic_mapper() -> EpicMapper:
    """Создать EpicMapper."""
    return EpicMapper()


def create_sprint_mapper() -> SprintMapper:
    """Создать SprintMapper."""
    return SprintMapper()


def create_project_membership_mapper() -> ProjectMembershipMapper:
    """Создать ProjectMembershipMapper."""
    return ProjectMembershipMapper()


def create_project_role_mapper() -> ProjectRoleMapper:
    """Создать ProjectRoleMapper."""
    return ProjectRoleMapper()


def create_retro_template_mapper() -> RetroTemplateMapper:
    """Создать RetroTemplateMapper."""
    return RetroTemplateMapper()


# --- Repositories ---

def create_project_repository(session: AsyncSession, mapper: ProjectMapper) -> ProjectRepository:
    """Создать SqlProjectRepository."""
    return SqlProjectRepository(session=session, mapper=mapper)


def create_board_repository(session: AsyncSession, mapper: BoardMapper) -> BoardRepository:
    """Создать SqlBoardRepository."""
    return SqlBoardRepository(session=session, mapper=mapper)


def create_epic_repository(session: AsyncSession, mapper: EpicMapper) -> EpicRepository:
    """Создать SqlEpicRepository."""
    return SqlEpicRepository(session=session, mapper=mapper)


def create_sprint_repository(session: AsyncSession, mapper: SprintMapper) -> SprintRepository:
    """Создать SqlSprintRepository."""
    return SqlSprintRepository(session=session, mapper=mapper)


def create_project_membership_repository(
    session: AsyncSession, mapper: ProjectMembershipMapper,
) -> ProjectMembershipRepository:
    """Создать SqlProjectMembershipRepository."""
    return SqlProjectMembershipRepository(session=session, mapper=mapper)


def create_project_role_repository(
    session: AsyncSession, mapper: ProjectRoleMapper,
) -> ProjectRoleRepository:
    """Создать SqlProjectRoleRepository."""
    return SqlProjectRoleRepository(session=session, mapper=mapper)


def create_retro_template_repository(
    session: AsyncSession, mapper: RetroTemplateMapper,
) -> RetroTemplateRepository:
    """Создать SqlRetroTemplateRepository."""
    return SqlRetroTemplateRepository(session=session, mapper=mapper)


# --- Inboard adapters (кросс-BC) ---

def create_project_identity_user_adapter(
    identity_user_provider: IdentityUserProvider,
) -> IdentityUserPort:
    """Создать IdentityUserAdapter (inboard) для Project BC."""
    return IdentityUserAdapter(identity_user_provider=identity_user_provider)


def create_project_workspace_adapter(
    workspace_provider: WorkspaceProvider,
) -> WorkspacePort:
    """Создать WorkspaceAdapter (inboard) для Project BC."""
    return WorkspaceAdapter(workspace_provider=workspace_provider)


def create_project_workspace_membership_adapter(
    workspace_membership_provider: WorkspaceMembershipProvider,
) -> WorkspaceMembershipPort:
    """Создать WorkspaceMembershipAdapter (inboard) для Project BC."""
    return WorkspaceMembershipAdapter(workspace_membership_provider=workspace_membership_provider)


def create_project_org_membership_adapter(
    org_membership_provider: OrganizationMembershipProvider,
) -> OrganizationMembershipPort:
    """Создать OrganizationMembershipAdapter (inboard) для Project BC."""
    return OrganizationMembershipAdapter(org_membership_provider=org_membership_provider)


def create_project_ws_permission_checker_adapter(
    workspace_membership_provider: WorkspaceMembershipProvider,
) -> WorkspacePermissionCheckerPort:
    """Создать WorkspacePermissionCheckerAdapter (inboard) для Project BC."""
    return WorkspacePermissionCheckerAdapter(workspace_membership_provider=workspace_membership_provider)


# --- Outboard adapters ---

def create_project_provider_adapter(repo: ProjectRepository) -> ProjectProvider:
    """Создать ProjectProviderAdapter (outboard)."""
    return ProjectProviderAdapter(repo=repo)


def create_board_provider_adapter(repo: BoardRepository) -> BoardProvider:
    """Создать BoardProviderAdapter (outboard)."""
    return BoardProviderAdapter(repo=repo)


def create_epic_provider_adapter(repo: EpicRepository) -> EpicProvider:
    """Создать EpicProviderAdapter (outboard)."""
    return EpicProviderAdapter(repo=repo)


def create_sprint_provider_adapter(repo: SprintRepository) -> SprintProvider:
    """Создать SprintProviderAdapter (outboard)."""
    return SprintProviderAdapter(repo=repo)


def create_project_analytics_adapter(session_factory: async_sessionmaker[AsyncSession]) -> ProjectAnalyticsProvider:
    """Создать SqlProjectAnalyticsAdapter (outboard) для Analytics BC."""
    return SqlProjectAnalyticsAdapter(session_factory=session_factory)


def create_project_membership_provider_adapter(
    repo: ProjectMembershipRepository,
) -> ProjectMembershipProvider:
    """Создать ProjectMembershipProviderAdapter (outboard)."""
    return ProjectMembershipProviderAdapter(repo=repo)


def create_project_role_provider_adapter(repo: ProjectRoleRepository) -> ProjectRoleProvider:
    """Создать ProjectRoleProviderAdapter (outboard)."""
    return ProjectRoleProviderAdapter(repo=repo)


def create_project_permission_provider(
    checker: ProjectPermissionCheckerPort,
) -> ProjectPermissionProvider:
    """Создать ProjectPermissionProviderImpl (outboard)."""
    return ProjectPermissionProviderImpl(checker=checker)


# --- Authorization ---

def create_project_permission_checker(
    membership_repo: ProjectMembershipRepository,
    project_role_repo: ProjectRoleRepository,
    project_repo: ProjectRepository,
    workspace_permission_checker: WorkspacePermissionCheckerPort,
) -> ProjectPermissionCheckerPort:
    """Создать ProjectRoleBasedPermissionChecker."""
    return ProjectRoleBasedPermissionChecker(
        membership_repo=membership_repo,
        project_role_repo=project_role_repo,
        project_repo=project_repo,
        workspace_permission_checker=workspace_permission_checker,
    )


def create_project_reminder_window_adapter(
    reminder_window_provider: ReminderWindowProvider,
) -> ReminderWindowPort:
    """Создать ReminderWindowAdapter (inboard) для Project BC."""
    return ReminderWindowAdapter(reminder_window_provider=reminder_window_provider)
