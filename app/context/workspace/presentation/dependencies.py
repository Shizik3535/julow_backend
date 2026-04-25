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
    return container.workspace_permission_checker(session=session)


# ---------------------------------------------------------------------------
# Workspace BC — Integration ports (inboard)
# ---------------------------------------------------------------------------


async def get_ws_identity_user_port(container: Container = Depends(get_container)):
    """Получить IdentityUserPort (inboard) из DI-контейнера."""
    return container.ws_identity_user_port()


async def get_ws_org_permission_checker_port(container: Container = Depends(get_container)):
    """Получить OrganizationPermissionCheckerPort (inboard) из DI-контейнера."""
    return container.ws_org_permission_checker_port()


async def get_ws_organization_membership_port(container: Container = Depends(get_container)):
    """Получить OrganizationMembershipPort (inboard) из DI-контейнера."""
    return container.ws_organization_membership_port()


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
