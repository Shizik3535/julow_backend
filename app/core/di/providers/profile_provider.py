from sqlalchemy.ext.asyncio import AsyncSession

from app.context.identity.application.ports.integration.outboard.identity_user_provider import (
    IdentityUserProvider,
)
from app.context.profile.application.ports.integration.inboard.identity_user_port import (
    IdentityUserPort,
)
from app.context.organization.application.ports.integration.outboard.organization_membership_provider import (
    OrganizationMembershipProvider,
)
from app.context.profile.application.ports.integration.inboard.organization_membership_port import (
    OrganizationMembershipPort,
)
from app.context.profile.application.ports.integration.outboard.profile_settings_provider import (
    ProfileSettingsProvider,
)
from app.context.profile.application.ports.integration.outboard.profile_user_provider import (
    ProfileUserProvider,
)
from app.context.profile.application.ports.navigation.start_page_registry_port import (
    StartPageRegistryPort,
)
from app.context.profile.infrastructure.integration.inboard.identity_user_adapter import (
    IdentityUserAdapter,
)
from app.context.profile.infrastructure.integration.inboard.organization_membership_adapter import (
    OrganizationMembershipAdapter,
)
from app.context.profile.infrastructure.integration.outboard.profile_settings_provider_adapter import (
    ProfileSettingsProviderAdapter,
)
from app.context.profile.infrastructure.integration.outboard.profile_user_provider_adapter import (
    ProfileUserProviderAdapter,
)
from app.context.profile.infrastructure.navigation.start_page_registry_adapter import (
    StartPageRegistryAdapter,
)
from app.context.profile.infrastructure.persistence.mappers.user_profile_mapper import (
    UserProfileMapper,
)
from app.context.profile.domain.repositories.user_profile_repository import (
    UserProfileRepository,
)
from app.context.profile.infrastructure.persistence.repositories.sql_user_profile_repository import (
    SqlUserProfileRepository,
)


# --- Mappers ---

def create_profile_mapper() -> UserProfileMapper:
    """Создать UserProfileMapper."""
    return UserProfileMapper()


# --- Repositories ---

def create_profile_repository(
    session: AsyncSession,
    mapper: UserProfileMapper,
) -> UserProfileRepository:
    """Создать SqlUserProfileRepository."""
    return SqlUserProfileRepository(session=session, mapper=mapper)


# --- Integration adapters ---

def create_identity_user_adapter(
    identity_user_provider: IdentityUserProvider,
) -> IdentityUserPort:
    """Создать IdentityUserAdapter (inboard) — получает IdentityUserProvider из DI."""
    return IdentityUserAdapter(identity_user_provider=identity_user_provider)


def create_profile_user_provider(
    profile_repo: UserProfileRepository,
) -> ProfileUserProvider:
    """Создать ProfileUserProviderAdapter (outboard)."""
    return ProfileUserProviderAdapter(profile_repo=profile_repo)


def create_profile_settings_provider(
    profile_repo: UserProfileRepository,
) -> ProfileSettingsProvider:
    """Создать ProfileSettingsProviderAdapter (outboard)."""
    return ProfileSettingsProviderAdapter(profile_repo=profile_repo)


# --- BC-specific adapters ---

def create_organization_membership_adapter(
    org_membership_provider: OrganizationMembershipProvider,
) -> OrganizationMembershipPort:
    """Создать OrganizationMembershipAdapter (inboard) — делегирует в Organization BC outboard."""
    return OrganizationMembershipAdapter(org_membership_provider=org_membership_provider)


def create_start_page_registry_adapter() -> StartPageRegistryPort:
    """Создать StartPageRegistryAdapter (BC-specific)."""
    return StartPageRegistryAdapter()

