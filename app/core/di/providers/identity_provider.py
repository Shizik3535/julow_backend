from sqlalchemy.ext.asyncio import AsyncSession

from app.context.identity.application.ports.integration.outboard.identity_role_provider import (
    IdentityRoleProvider,
)
from app.context.identity.application.ports.integration.outboard.identity_user_provider import (
    IdentityUserProvider,
)
from app.context.identity.application.ports.authorization.permission_checker_port import (
    PermissionCheckerPort,
)
from app.context.identity.application.ports.integration.outboard.identity_permission_provider import (
    IdentityPermissionProvider,
)
from app.context.identity.application.ports.notification.identity_notification_port import (
    IdentityNotificationPort,
)
from app.context.identity.application.ports.oauth.oauth_port import OAuthPort
from app.context.identity.application.ports.two_fa.totp_port import TOTPPort
from app.context.identity.domain.repositories.role_repository import RoleRepository
from app.context.identity.domain.repositories.session_repository import SessionRepository
from app.context.identity.domain.repositories.user_auth_repository import UserAuthRepository
from app.context.identity.domain.repositories.user_repository import UserRepository
from app.context.identity.infrastructure.authorization.role_based_permission_checker import (
    RoleBasedPermissionChecker,
)
from app.context.identity.infrastructure.integration.outboard.permission_provider_adapter import (
    PermissionProviderAdapter,
)
from app.context.identity.infrastructure.integration.outboard.role_provider_adapter import (
    RoleProviderAdapter,
)
from app.context.identity.infrastructure.integration.outboard.user_provider_adapter import (
    UserProviderAdapter,
)
from app.context.identity.infrastructure.notification.identity_notification_adapter import (
    IdentityNotificationAdapter,
)
from app.context.identity.infrastructure.oauth.oauth_adapter import HttpxOAuthAdapter
from app.context.identity.infrastructure.persistence.mappers.role_mapper import RoleMapper
from app.context.identity.infrastructure.persistence.mappers.session_mapper import SessionMapper
from app.context.identity.infrastructure.persistence.mappers.user_auth_mapper import UserAuthMapper
from app.context.identity.domain.value_objects.failed_login_policy import FailedLoginPolicy
from app.context.identity.domain.value_objects.lockout_threshold import LockoutThreshold
from app.context.identity.infrastructure.persistence.mappers.user_mapper import UserMapper
from app.context.identity.infrastructure.persistence.repositories.sql_role_repository import (
    SqlRoleRepository,
)
from app.context.identity.infrastructure.persistence.repositories.sql_session_repository import (
    SqlSessionRepository,
)
from app.context.identity.infrastructure.persistence.repositories.sql_user_auth_repository import (
    SqlUserAuthRepository,
)
from app.context.identity.infrastructure.persistence.repositories.sql_user_repository import (
    SqlUserRepository,
)
from app.context.identity.infrastructure.two_fa.totp_adapter import PyOTPTotpAdapter
from app.shared.application.ports.notification.email_port import EmailPort


# --- Mappers ---

def create_user_mapper() -> UserMapper:
    """Создать UserMapper."""
    return UserMapper()


def create_user_auth_mapper() -> UserAuthMapper:
    """Создать UserAuthMapper."""
    return UserAuthMapper()


def create_session_mapper() -> SessionMapper:
    """Создать SessionMapper."""
    return SessionMapper()


def create_role_mapper() -> RoleMapper:
    """Создать RoleMapper."""
    return RoleMapper()


# --- Repositories ---

def create_user_repository(session: AsyncSession, mapper: UserMapper) -> UserRepository:
    """Создать SqlUserRepository."""
    return SqlUserRepository(session=session, mapper=mapper)


def create_user_auth_repository(session: AsyncSession, mapper: UserAuthMapper) -> UserAuthRepository:
    """Создать SqlUserAuthRepository."""
    return SqlUserAuthRepository(session=session, mapper=mapper)


def create_session_repository(session: AsyncSession, mapper: SessionMapper) -> SessionRepository:
    """Создать SqlSessionRepository."""
    return SqlSessionRepository(session=session, mapper=mapper)


def create_role_repository(session: AsyncSession, mapper: RoleMapper) -> RoleRepository:
    """Создать SqlRoleRepository."""
    return SqlRoleRepository(session=session, mapper=mapper)


# --- Integration adapters ---

def create_user_provider(user_repo: UserRepository) -> IdentityUserProvider:
    """Создать UserProviderAdapter (outboard)."""
    return UserProviderAdapter(user_repo=user_repo)


def create_role_provider(
    role_repo: RoleRepository,
    user_repo: UserRepository,
) -> IdentityRoleProvider:
    """Создать RoleProviderAdapter (outboard)."""
    return RoleProviderAdapter(role_repo=role_repo, user_repo=user_repo)


# --- BC-специфичные адаптеры ---

def create_totp_adapter() -> TOTPPort:
    """Создать PyOTPTotpAdapter."""
    return PyOTPTotpAdapter()


def create_oauth_adapter(
    client_id_map: dict[str, str],
    client_secret_map: dict[str, str],
) -> OAuthPort:
    """Создать HttpxOAuthAdapter."""
    return HttpxOAuthAdapter(
        client_id_map=client_id_map,
        client_secret_map=client_secret_map,
    )


def create_identity_notification_adapter(
    email_port: EmailPort,
    frontend_base_url: str,
) -> IdentityNotificationPort:
    """Создать IdentityNotificationAdapter."""
    return IdentityNotificationAdapter(
        email_port=email_port,
        frontend_base_url=frontend_base_url,
    )


# --- Domain policies ---

def create_failed_login_policy() -> FailedLoginPolicy:
    """Создать FailedLoginPolicy с порогами по умолчанию."""
    return FailedLoginPolicy(
        thresholds=[
            LockoutThreshold(failed_attempts=5, lock_duration_minutes=15),
            LockoutThreshold(failed_attempts=10, lock_duration_minutes=60),
            LockoutThreshold(failed_attempts=15, lock_duration_minutes=1440),
        ]
    )


# --- Authorization ---

def create_permission_checker(
    user_repo: UserRepository,
    role_repo: RoleRepository,
) -> PermissionCheckerPort:
    """Создать RoleBasedPermissionChecker."""
    return RoleBasedPermissionChecker(user_repo=user_repo, role_repo=role_repo)


def create_permission_provider(
    permission_checker: PermissionCheckerPort,
) -> IdentityPermissionProvider:
    """Создать PermissionProviderAdapter (outboard)."""
    return PermissionProviderAdapter(permission_checker=permission_checker)

