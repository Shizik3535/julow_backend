"""
DI-провайдеры для Workspace BC.
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.context.identity.application.ports.integration.outboard.identity_user_provider import (
    IdentityUserProvider,
)
from app.context.organization.application.ports.integration.outboard.organization_membership_provider import (
    OrganizationMembershipProvider,
)
from app.context.organization.application.ports.integration.outboard.organization_permission_provider import (
    OrganizationPermissionProvider,
)
from app.context.organization.application.ports.integration.outboard.organization_provider import (
    OrganizationProvider,
)
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.application.ports.integration.inboard.identity_user_port import IdentityUserPort
from app.context.workspace.application.ports.integration.inboard.organization_membership_port import (
    OrganizationMembershipPort,
)
from app.context.workspace.application.ports.integration.inboard.organization_permission_checker_port import (
    OrganizationPermissionCheckerPort,
)
from app.context.workspace.application.ports.integration.inboard.organization_port import OrganizationPort
from app.context.workspace.domain.repositories.workspace_invitation_repository import (
    WorkspaceInvitationRepository,
)
from app.context.workspace.domain.repositories.workspace_membership_repository import (
    WorkspaceMembershipRepository,
)
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository
from app.context.workspace.domain.repositories.workspace_role_repository import WorkspaceRoleRepository
from app.context.workspace.domain.repositories.workspace_team_repository import WorkspaceTeamRepository
from app.context.workspace.infrastructure.authorization.workspace_role_based_permission_checker import (
    WorkspaceRoleBasedPermissionChecker,
)
from app.context.workspace.infrastructure.integration.inboard.identity_user_adapter import IdentityUserAdapter
from app.context.workspace.infrastructure.integration.inboard.organization_adapter import OrganizationAdapter
from app.context.workspace.infrastructure.integration.inboard.organization_membership_adapter import (
    OrganizationMembershipAdapter,
)
from app.context.workspace.infrastructure.integration.inboard.organization_permission_checker_adapter import (
    OrganizationPermissionCheckerAdapter,
)
from app.context.workspace.infrastructure.integration.outboard.workspace_membership_provider_adapter import (
    WorkspaceMembershipProviderAdapter,
)
from app.context.workspace.infrastructure.integration.outboard.workspace_provider_adapter import (
    WorkspaceProviderAdapter,
)
from app.context.workspace.infrastructure.persistence.mappers.workspace_invitation_mapper import (
    WorkspaceInvitationMapper,
)
from app.context.workspace.infrastructure.persistence.mappers.workspace_membership_mapper import (
    WorkspaceMembershipMapper,
)
from app.context.workspace.infrastructure.persistence.mappers.workspace_mapper import WorkspaceMapper
from app.context.workspace.infrastructure.persistence.mappers.workspace_role_mapper import WorkspaceRoleMapper
from app.context.workspace.infrastructure.persistence.mappers.workspace_team_mapper import WorkspaceTeamMapper
from app.context.workspace.infrastructure.persistence.repositories.sql_workspace_invitation_repository import (
    SqlWorkspaceInvitationRepository,
)
from app.context.workspace.infrastructure.persistence.repositories.sql_workspace_membership_repository import (
    SqlWorkspaceMembershipRepository,
)
from app.context.workspace.infrastructure.persistence.repositories.sql_workspace_repository import (
    SqlWorkspaceRepository,
)
from app.context.workspace.infrastructure.persistence.repositories.sql_workspace_role_repository import (
    SqlWorkspaceRoleRepository,
)
from app.context.workspace.infrastructure.persistence.repositories.sql_workspace_team_repository import (
    SqlWorkspaceTeamRepository,
)


# --- Mappers ---

def create_workspace_mapper() -> WorkspaceMapper:
    """Создать WorkspaceMapper."""
    return WorkspaceMapper()


def create_workspace_membership_mapper() -> WorkspaceMembershipMapper:
    """Создать WorkspaceMembershipMapper."""
    return WorkspaceMembershipMapper()


def create_workspace_role_mapper() -> WorkspaceRoleMapper:
    """Создать WorkspaceRoleMapper."""
    return WorkspaceRoleMapper()


def create_workspace_team_mapper() -> WorkspaceTeamMapper:
    """Создать WorkspaceTeamMapper."""
    return WorkspaceTeamMapper()


def create_workspace_invitation_mapper() -> WorkspaceInvitationMapper:
    """Создать WorkspaceInvitationMapper."""
    return WorkspaceInvitationMapper()


# --- Repositories ---

def create_workspace_repository(session: AsyncSession, mapper: WorkspaceMapper) -> WorkspaceRepository:
    """Создать SqlWorkspaceRepository."""
    return SqlWorkspaceRepository(session=session, mapper=mapper)


def create_workspace_membership_repository(
    session: AsyncSession, mapper: WorkspaceMembershipMapper
) -> WorkspaceMembershipRepository:
    """Создать SqlWorkspaceMembershipRepository."""
    return SqlWorkspaceMembershipRepository(session=session, mapper=mapper)


def create_workspace_role_repository(
    session: AsyncSession, mapper: WorkspaceRoleMapper
) -> WorkspaceRoleRepository:
    """Создать SqlWorkspaceRoleRepository."""
    return SqlWorkspaceRoleRepository(session=session, mapper=mapper)


def create_workspace_team_repository(
    session: AsyncSession, mapper: WorkspaceTeamMapper
) -> WorkspaceTeamRepository:
    """Создать SqlWorkspaceTeamRepository."""
    return SqlWorkspaceTeamRepository(session=session, mapper=mapper)


def create_workspace_invitation_repository(
    session: AsyncSession, mapper: WorkspaceInvitationMapper
) -> WorkspaceInvitationRepository:
    """Создать SqlWorkspaceInvitationRepository."""
    return SqlWorkspaceInvitationRepository(session=session, mapper=mapper)


# --- Inboard adapters (кросс-BC) ---

def create_ws_identity_user_adapter(identity_user_provider: IdentityUserProvider) -> IdentityUserPort:
    """Создать адаптер inboard-порта IdentityUserPort для Workspace BC."""
    return IdentityUserAdapter(identity_user_provider=identity_user_provider)


def create_ws_organization_membership_adapter(
    org_membership_provider: OrganizationMembershipProvider,
) -> OrganizationMembershipPort:
    """Создать адаптер inboard-порта OrganizationMembershipPort для Workspace BC."""
    return OrganizationMembershipAdapter(org_membership_provider=org_membership_provider)


def create_ws_organization_adapter(organization_provider: OrganizationProvider) -> OrganizationPort:
    """Создать адаптер inboard-порта OrganizationPort для Workspace BC."""
    return OrganizationAdapter(organization_provider=organization_provider)


def create_ws_org_permission_checker_adapter(
    org_permission_provider: OrganizationPermissionProvider,
) -> OrganizationPermissionCheckerPort:
    """Создать адаптер inboard-порта OrganizationPermissionCheckerPort для Workspace BC."""
    return OrganizationPermissionCheckerAdapter(org_permission_provider=org_permission_provider)


# --- Outboard adapters ---

def create_workspace_provider_adapter(repo: WorkspaceRepository) -> WorkspaceProviderAdapter:
    """Создать outboard-адаптер WorkspaceProvider."""
    return WorkspaceProviderAdapter(repo=repo)


def create_workspace_membership_provider_adapter(
    membership_repo: WorkspaceMembershipRepository,
    workspace_role_repo: WorkspaceRoleRepository,
    workspace_repo: WorkspaceRepository,
) -> WorkspaceMembershipProviderAdapter:
    """Создать outboard-адаптер WorkspaceMembershipProvider."""
    return WorkspaceMembershipProviderAdapter(
        membership_repo=membership_repo,
        workspace_role_repo=workspace_role_repo,
        workspace_repo=workspace_repo,
    )


# --- Authorization ---

def create_workspace_permission_checker(
    membership_repo: WorkspaceMembershipRepository,
    workspace_role_repo: WorkspaceRoleRepository,
    ws_repo: WorkspaceRepository,
    org_permission_checker: OrganizationPermissionCheckerPort,
) -> WorkspacePermissionCheckerPort:
    """Создать WorkspaceRoleBasedPermissionChecker с каскадом OrgRole → Workspace."""
    return WorkspaceRoleBasedPermissionChecker(
        membership_repo=membership_repo,
        workspace_role_repo=workspace_role_repo,
        ws_repo=ws_repo,
        org_permission_checker=org_permission_checker,
    )
