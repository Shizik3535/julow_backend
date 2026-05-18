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
# Project BC — Repositories
# ---------------------------------------------------------------------------


async def get_project_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить ProjectRepository из DI-контейнера."""
    return container.project_repo(session=session)


async def get_board_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить BoardRepository из DI-контейнера."""
    return container.board_repo(session=session)


async def get_epic_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить EpicRepository из DI-контейнера."""
    return container.epic_repo(session=session)


async def get_sprint_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить SprintRepository из DI-контейнера."""
    return container.sprint_repo(session=session)


async def get_project_membership_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить ProjectMembershipRepository из DI-контейнера."""
    return container.project_membership_repo(session=session)


async def get_project_invitation_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить ProjectInvitationRepository из DI-контейнера."""
    return container.project_invitation_repo(session=session)


async def get_project_role_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить ProjectRoleRepository из DI-контейнера."""
    return container.project_role_repo(session=session)


async def get_retro_template_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить RetroTemplateRepository из DI-контейнера."""
    return container.retro_template_repo(session=session)


# ---------------------------------------------------------------------------
# Project BC — Authorization
# ---------------------------------------------------------------------------


async def get_project_permission_checker(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить ProjectPermissionCheckerPort из DI-контейнера."""
    # Project-level repos (session reaches them directly)
    membership_repo = container.project_membership_repo(session=session)
    project_role_repo = container.project_role_repo(session=session)
    project_repo = container.project_repo(session=session)
    # Workspace-level chain (3 nested repos need explicit session)
    ws_membership_repo = container.workspace_membership_repo(session=session)
    ws_role_repo = container.workspace_role_repo(session=session)
    ws_repo = container.workspace_repo(session=session)
    workspace_membership_provider = container.workspace_membership_provider(
        membership_repo=ws_membership_repo,
        workspace_role_repo=ws_role_repo,
        workspace_repo=ws_repo,
    )
    ws_permission_checker = container.project_ws_permission_checker_port(
        workspace_membership_provider=workspace_membership_provider,
    )
    return container.project_permission_checker(
        membership_repo=membership_repo,
        project_role_repo=project_role_repo,
        project_repo=project_repo,
        workspace_permission_checker=ws_permission_checker,
    )


# ---------------------------------------------------------------------------
# Project BC — Integration inboard adapters
# ---------------------------------------------------------------------------


async def get_project_identity_user_port(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить IdentityUserPort (inboard) из DI-контейнера."""
    user_repo = container.user_repo(session=session)
    identity_user_provider = container.identity_user_provider(user_repo=user_repo)
    return container.project_identity_user_port(identity_user_provider=identity_user_provider)


async def get_project_workspace_port(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить WorkspacePort (inboard) из DI-контейнера."""
    ws_repo = container.workspace_repo(session=session)
    workspace_provider = container.workspace_provider(repo=ws_repo)
    return container.project_workspace_port(workspace_provider=workspace_provider)


async def get_project_workspace_membership_port(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить WorkspaceMembershipPort (inboard) из DI-контейнера."""
    ws_membership_repo = container.workspace_membership_repo(session=session)
    ws_role_repo = container.workspace_role_repo(session=session)
    ws_repo = container.workspace_repo(session=session)
    workspace_membership_provider = container.workspace_membership_provider(
        membership_repo=ws_membership_repo,
        workspace_role_repo=ws_role_repo,
        workspace_repo=ws_repo,
    )
    return container.project_workspace_membership_port(
        workspace_membership_provider=workspace_membership_provider,
    )


async def get_project_org_membership_port(
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
    return container.project_org_membership_port(org_membership_provider=org_membership_provider)


async def get_project_ws_permission_checker_port(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить WorkspacePermissionCheckerPort (inboard) из DI-контейнера."""
    ws_membership_repo = container.workspace_membership_repo(session=session)
    ws_role_repo = container.workspace_role_repo(session=session)
    ws_repo = container.workspace_repo(session=session)
    workspace_membership_provider = container.workspace_membership_provider(
        membership_repo=ws_membership_repo,
        workspace_role_repo=ws_role_repo,
        workspace_repo=ws_repo,
    )
    return container.project_ws_permission_checker_port(
        workspace_membership_provider=workspace_membership_provider,
    )


# ---------------------------------------------------------------------------
# Shared ports
# ---------------------------------------------------------------------------


async def get_auth_token_port(container: Container = Depends(get_container)):
    """Получить AuthTokenPort из DI-контейнера."""
    return container.auth_token_port()


async def get_project_event_bus(container: Container = Depends(get_container)):
    """Получить DomainEventBus Project BC из DI-контейнера."""
    return container.project_event_bus()


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
