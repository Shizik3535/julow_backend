from sqlalchemy.ext.asyncio import AsyncSession

from app.context.identity.application.ports.integration.outboard.identity_user_provider import (
    IdentityUserProvider,
)
from app.context.organization.application.ports.encryption.encryption_port import EncryptionPort
from app.context.organization.application.ports.integration.inboard.identity_user_port import (
    IdentityUserPort,
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
from app.context.organization.domain.repositories.department_repository import DepartmentRepository
from app.context.organization.domain.repositories.invitation_repository import InvitationRepository
from app.context.organization.domain.repositories.org_membership_repository import OrgMembershipRepository
from app.context.organization.domain.repositories.org_role_repository import OrgRoleRepository
from app.context.organization.domain.repositories.organization_repository import OrganizationRepository
from app.context.organization.domain.repositories.sso_integration_repository import SSOIntegrationRepository
from app.context.organization.domain.repositories.storage_integration_repository import StorageIntegrationRepository
from app.context.organization.domain.repositories.team_repository import TeamRepository
from app.context.organization.application.ports.authorization.org_permission_checker_port import OrgPermissionCheckerPort
from app.context.organization.infrastructure.authorization.org_role_based_permission_checker import OrgRoleBasedPermissionChecker
from app.context.organization.infrastructure.encryption.fernet_encryption_adapter import FernetEncryptionAdapter
from app.context.organization.infrastructure.integration.inboard.identity_user_adapter import IdentityUserAdapter
from app.context.organization.infrastructure.integration.outboard.organization_membership_provider_adapter import (
    OrganizationMembershipProviderAdapter,
)
from app.context.organization.infrastructure.integration.outboard.organization_permission_provider_adapter import (
    OrganizationPermissionProviderAdapter,
)
from app.context.organization.infrastructure.integration.outboard.organization_provider_adapter import (
    OrganizationProviderAdapter,
)
from app.context.organization.infrastructure.persistence.mappers.department_mapper import DepartmentMapper
from app.context.organization.infrastructure.persistence.mappers.invitation_mapper import InvitationMapper
from app.context.organization.infrastructure.persistence.mappers.org_membership_mapper import OrgMembershipMapper
from app.context.organization.infrastructure.persistence.mappers.org_role_mapper import OrgRoleMapper
from app.context.organization.infrastructure.persistence.mappers.organization_mapper import OrganizationMapper
from app.context.organization.infrastructure.persistence.mappers.sso_integration_mapper import SSOIntegrationMapper
from app.context.organization.infrastructure.persistence.mappers.storage_integration_mapper import (
    StorageIntegrationMapper,
)
from app.context.organization.infrastructure.persistence.mappers.team_mapper import TeamMapper
from app.context.organization.infrastructure.persistence.repositories.sql_department_repository import (
    SqlDepartmentRepository,
)
from app.context.organization.infrastructure.persistence.repositories.sql_invitation_repository import (
    SqlInvitationRepository,
)
from app.context.organization.infrastructure.persistence.repositories.sql_org_membership_repository import (
    SqlOrgMembershipRepository,
)
from app.context.organization.infrastructure.persistence.repositories.sql_org_role_repository import (
    SqlOrgRoleRepository,
)
from app.context.organization.infrastructure.persistence.repositories.sql_organization_repository import (
    SqlOrganizationRepository,
)
from app.context.organization.infrastructure.persistence.repositories.sql_sso_integration_repository import (
    SqlSSOIntegrationRepository,
)
from app.context.organization.infrastructure.persistence.repositories.sql_storage_integration_repository import (
    SqlStorageIntegrationRepository,
)
from app.context.organization.infrastructure.persistence.repositories.sql_team_repository import (
    SqlTeamRepository,
)


# --- Mappers ---

def create_organization_mapper() -> OrganizationMapper:
    """Создать OrganizationMapper."""
    return OrganizationMapper()


def create_org_membership_mapper() -> OrgMembershipMapper:
    """Создать OrgMembershipMapper."""
    return OrgMembershipMapper()


def create_team_mapper() -> TeamMapper:
    """Создать TeamMapper."""
    return TeamMapper()


def create_org_role_mapper() -> OrgRoleMapper:
    """Создать OrgRoleMapper."""
    return OrgRoleMapper()


def create_department_mapper() -> DepartmentMapper:
    """Создать DepartmentMapper."""
    return DepartmentMapper()


def create_invitation_mapper() -> InvitationMapper:
    """Создать InvitationMapper."""
    return InvitationMapper()


def create_sso_integration_mapper() -> SSOIntegrationMapper:
    """Создать SSOIntegrationMapper."""
    return SSOIntegrationMapper()


def create_storage_integration_mapper() -> StorageIntegrationMapper:
    """Создать StorageIntegrationMapper."""
    return StorageIntegrationMapper()


# --- Repositories ---

def create_organization_repository(
    session: AsyncSession, mapper: OrganizationMapper,
) -> OrganizationRepository:
    """Создать SqlOrganizationRepository."""
    return SqlOrganizationRepository(session=session, mapper=mapper)


def create_org_membership_repository(
    session: AsyncSession, mapper: OrgMembershipMapper,
) -> OrgMembershipRepository:
    """Создать SqlOrgMembershipRepository."""
    return SqlOrgMembershipRepository(session=session, mapper=mapper)


def create_team_repository(
    session: AsyncSession, mapper: TeamMapper,
) -> TeamRepository:
    """Создать SqlTeamRepository."""
    return SqlTeamRepository(session=session, mapper=mapper)


def create_org_role_repository(
    session: AsyncSession, mapper: OrgRoleMapper,
) -> OrgRoleRepository:
    """Создать SqlOrgRoleRepository."""
    return SqlOrgRoleRepository(session=session, mapper=mapper)


def create_department_repository(
    session: AsyncSession, mapper: DepartmentMapper,
) -> DepartmentRepository:
    """Создать SqlDepartmentRepository."""
    return SqlDepartmentRepository(session=session, mapper=mapper)


def create_invitation_repository(
    session: AsyncSession, mapper: InvitationMapper,
) -> InvitationRepository:
    """Создать SqlInvitationRepository."""
    return SqlInvitationRepository(session=session, mapper=mapper)


def create_sso_integration_repository(
    session: AsyncSession, mapper: SSOIntegrationMapper,
) -> SSOIntegrationRepository:
    """Создать SqlSSOIntegrationRepository."""
    return SqlSSOIntegrationRepository(session=session, mapper=mapper)


def create_storage_integration_repository(
    session: AsyncSession, mapper: StorageIntegrationMapper,
) -> StorageIntegrationRepository:
    """Создать SqlStorageIntegrationRepository."""
    return SqlStorageIntegrationRepository(session=session, mapper=mapper)


# --- Integration adapters ---

def create_org_identity_user_adapter(
    identity_user_provider: IdentityUserProvider,
) -> IdentityUserPort:
    """Создать IdentityUserAdapter (inboard) для Organization BC."""
    return IdentityUserAdapter(identity_user_provider=identity_user_provider)


def create_organization_provider(
    repo: OrganizationRepository,
) -> OrganizationProvider:
    """Создать OrganizationProviderAdapter (outboard)."""
    return OrganizationProviderAdapter(repo=repo)


def create_organization_membership_provider(
    repo: OrgMembershipRepository,
    org_repo: OrganizationRepository,
) -> OrganizationMembershipProvider:
    """Создать OrganizationMembershipProviderAdapter (outbound)."""
    return OrganizationMembershipProviderAdapter(repo=repo, org_repo=org_repo)


# --- Authorization ---

def create_org_permission_checker(
    membership_repo: OrgMembershipRepository,
    org_role_repo: OrgRoleRepository,
) -> OrgPermissionCheckerPort:
    """Создать OrgRoleBasedPermissionChecker."""
    return OrgRoleBasedPermissionChecker(membership_repo=membership_repo, org_role_repo=org_role_repo)


def create_organization_permission_provider(
    permission_checker: OrgPermissionCheckerPort,
) -> OrganizationPermissionProvider:
    """Создать OrganizationPermissionProviderAdapter (outboard).

    Предоставляет проверку орг-разрешений другим BC (Workspace, Profile, ...).
    """
    return OrganizationPermissionProviderAdapter(permission_checker=permission_checker)


# --- BC-specific adapters ---

def create_fernet_encryption_adapter(encryption_key: str) -> EncryptionPort:
    """Создать FernetEncryptionAdapter."""
    return FernetEncryptionAdapter(encryption_key=encryption_key)
