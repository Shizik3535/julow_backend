from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.di.container import Container
from app.shared.application.ports.auth.auth_exceptions import InvalidTokenException
from app.shared.application.ports.auth.auth_port import AuthTokenPort

_bearer_scheme = HTTPBearer(
    scheme_name="JWT Bearer",
    description="JWT access-токен в формате `Bearer <token>`",
    auto_error=False,
)


def get_container(request: Request) -> Container:
    """Извлечь DI-контейнер из FastAPI application state."""
    return request.app.state.container


# ---------------------------------------------------------------------------
# Database session (per-request)
# ---------------------------------------------------------------------------


async def get_db_session(
    container: Container = Depends(get_container),
) -> AsyncGenerator[AsyncSession, None]:
    """Per-request AsyncSession с автоматическим commit/rollback."""
    session_factory = container.db_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ---------------------------------------------------------------------------
# Organization BC — Repositories
# ---------------------------------------------------------------------------


async def get_organization_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить OrganizationRepository из DI-контейнера."""
    return container.organization_repo(session=session)


async def get_org_membership_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить OrgMembershipRepository из DI-контейнера."""
    return container.org_membership_repo(session=session)


async def get_team_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить TeamRepository из DI-контейнера."""
    return container.team_repo(session=session)


async def get_org_role_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить OrgRoleRepository из DI-контейнера."""
    return container.org_role_repo(session=session)


async def get_department_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить DepartmentRepository из DI-контейнера."""
    return container.department_repo(session=session)


async def get_invitation_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить InvitationRepository из DI-контейнера."""
    return container.invitation_repo(session=session)


async def get_sso_integration_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить SSOIntegrationRepository из DI-контейнера."""
    return container.sso_integration_repo(session=session)


async def get_storage_integration_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить StorageIntegrationRepository из DI-контейнера."""
    return container.storage_integration_repo(session=session)


# ---------------------------------------------------------------------------
# Organization BC — Authorization
# ---------------------------------------------------------------------------


async def get_org_permission_checker(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить OrgPermissionCheckerPort из DI-контейнера."""
    membership_repo = container.org_membership_repo(session=session)
    org_role_repo = container.org_role_repo(session=session)
    return container.org_permission_checker(
        membership_repo=membership_repo,
        org_role_repo=org_role_repo,
    )


# ---------------------------------------------------------------------------
# Organization BC — Integration ports
# ---------------------------------------------------------------------------


async def get_org_identity_user_port(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить IdentityUserPort (inbound) из DI-контейнера."""
    user_repo = container.user_repo(session=session)
    identity_user_provider = container.identity_user_provider(user_repo=user_repo)
    return container.org_identity_user_port(identity_user_provider=identity_user_provider)


# ---------------------------------------------------------------------------
# Organization BC — BC-specific ports
# ---------------------------------------------------------------------------


async def get_encryption_port(container: Container = Depends(get_container)):
    """Получить EncryptionPort из DI-контейнера."""
    return container.encryption_port()


# ---------------------------------------------------------------------------
# Shared ports
# ---------------------------------------------------------------------------


async def get_auth_token_port(container: Container = Depends(get_container)):
    """Получить AuthTokenPort из DI-контейнера."""
    return container.auth_token_port()


async def get_organization_event_bus(container: Container = Depends(get_container)):
    """Получить DomainEventBus Organization BC из DI-контейнера."""
    return container.organization_event_bus()


# ---------------------------------------------------------------------------
# Auth — текущий пользователь
# ---------------------------------------------------------------------------


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    auth_token_port: AuthTokenPort = Depends(get_auth_token_port),
) -> str:
    """Извлечь user_id из JWT access-токена."""
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Не аутентифицирован — отсутствует Authorization заголовок",
        )
    try:
        payload = auth_token_port.validate_access_token(credentials.credentials)
    except InvalidTokenException:
        raise HTTPException(
            status_code=401,
            detail="Невалидный или просроченный access-токен",
        )
    return str(payload.user_id)
