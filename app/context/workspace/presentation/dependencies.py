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
# Workspace BC — Repositories
# ---------------------------------------------------------------------------


async def get_workspace_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить WorkspaceRepository из DI-контейнера."""
    return container.workspace_repo(session=session)


async def get_workspace_membership_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить WorkspaceMembershipRepository из DI-контейнера."""
    return container.workspace_membership_repo(session=session)


async def get_workspace_role_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить WorkspaceRoleRepository из DI-контейнера."""
    return container.workspace_role_repo(session=session)


async def get_workspace_team_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить WorkspaceTeamRepository из DI-контейнера."""
    return container.workspace_team_repo(session=session)


async def get_workspace_invitation_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить WorkspaceInvitationRepository из DI-контейнера."""
    return container.workspace_invitation_repo(session=session)


# ---------------------------------------------------------------------------
# Workspace BC — Authorization
# ---------------------------------------------------------------------------


async def get_workspace_permission_checker(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить WorkspacePermissionCheckerPort из DI-контейнера."""
    # Workspace-level repos
    membership_repo = container.workspace_membership_repo(session=session)
    workspace_role_repo = container.workspace_role_repo(session=session)
    ws_repo = container.workspace_repo(session=session)
    # Organization-level chain (for org_permission_checker)
    org_membership_repo = container.org_membership_repo(session=session)
    org_role_repo = container.org_role_repo(session=session)
    org_permission_checker = container.org_permission_checker(
        membership_repo=org_membership_repo,
        org_role_repo=org_role_repo,
    )
    org_permission_provider = container.org_permission_provider(permission_checker=org_permission_checker)
    ws_org_permission_checker = container.ws_org_permission_checker_port(
        org_permission_provider=org_permission_provider,
    )
    return container.workspace_permission_checker(
        membership_repo=membership_repo,
        workspace_role_repo=workspace_role_repo,
        ws_repo=ws_repo,
        org_permission_checker=ws_org_permission_checker,
    )


# ---------------------------------------------------------------------------
# Workspace BC — Integration ports (inboard)
# ---------------------------------------------------------------------------


async def get_ws_identity_user_port(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить IdentityUserPort (inboard) из DI-контейнера."""
    user_repo = container.user_repo(session=session)
    identity_user_provider = container.identity_user_provider(user_repo=user_repo)
    return container.ws_identity_user_port(identity_user_provider=identity_user_provider)


async def get_ws_org_permission_checker_port(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить OrganizationPermissionCheckerPort (inboard) из DI-контейнера."""
    org_membership_repo = container.org_membership_repo(session=session)
    org_role_repo = container.org_role_repo(session=session)
    org_permission_checker = container.org_permission_checker(
        membership_repo=org_membership_repo,
        org_role_repo=org_role_repo,
    )
    org_permission_provider = container.org_permission_provider(permission_checker=org_permission_checker)
    return container.ws_org_permission_checker_port(org_permission_provider=org_permission_provider)


async def get_ws_organization_membership_port(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить OrganizationMembershipPort (inboard) из DI-контейнера."""
    org_membership_repo = container.org_membership_repo(session=session)
    organization_repo = container.organization_repo(session=session)
    org_membership_provider = container.org_membership_provider(
        repo=org_membership_repo,
        org_repo=organization_repo,
    )
    return container.ws_organization_membership_port(org_membership_provider=org_membership_provider)


async def get_ws_organization_port(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить OrganizationPort (inboard) из DI-контейнера."""
    organization_repo = container.organization_repo(session=session)
    organization_provider = container.org_provider(repo=organization_repo)
    return container.ws_organization_port(organization_provider=organization_provider)


# ---------------------------------------------------------------------------
# Shared ports
# ---------------------------------------------------------------------------


async def get_auth_token_port(container: Container = Depends(get_container)):
    """Получить AuthTokenPort из DI-контейнера."""
    return container.auth_token_port()


async def get_workspace_event_bus(container: Container = Depends(get_container)):
    """Получить DomainEventBus Workspace BC из DI-контейнера."""
    return container.workspace_event_bus()


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


# ---------------------------------------------------------------------------
# File storage
# ---------------------------------------------------------------------------


async def get_file_storage_port(container: Container = Depends(get_container)):
    """Получить FileStoragePort из DI-контейнера."""
    return container.file_storage_port()
