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
# Repositories
# ---------------------------------------------------------------------------


async def get_time_entry_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    return container.time_entry_repo(session=session)


async def get_activity_category_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    return container.activity_category_repo(session=session)


async def get_time_entry_tag_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    return container.time_entry_tag_repo(session=session)


# ---------------------------------------------------------------------------
# Authorization
# ---------------------------------------------------------------------------


async def get_timetracking_permission_checker(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    ws_membership_repo = container.workspace_membership_repo(session=session)
    ws_role_repo = container.workspace_role_repo(session=session)
    ws_repo = container.workspace_repo(session=session)
    workspace_membership_provider = container.workspace_membership_provider(
        membership_repo=ws_membership_repo,
        workspace_role_repo=ws_role_repo,
        workspace_repo=ws_repo,
    )
    return container.timetracking_permission_checker_port(
        workspace_membership_provider=workspace_membership_provider,
    )


# ---------------------------------------------------------------------------
# Integration inboard ports
# ---------------------------------------------------------------------------


async def get_timetracking_workspace_port(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    ws_repo = container.workspace_repo(session=session)
    workspace_provider = container.workspace_provider(repo=ws_repo)
    ws_membership_repo = container.workspace_membership_repo(session=session)
    ws_role_repo = container.workspace_role_repo(session=session)
    workspace_membership_provider = container.workspace_membership_provider(
        membership_repo=ws_membership_repo,
        workspace_role_repo=ws_role_repo,
        workspace_repo=ws_repo,
    )
    return container.timetracking_workspace_port(
        workspace_provider=workspace_provider,
        workspace_membership_provider=workspace_membership_provider,
    )


async def get_timetracking_task_port(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    task_repo = container.task_repo(session=session)
    task_provider = container.task_provider(repo=task_repo)
    return container.timetracking_task_port(task_provider=task_provider)


async def get_timetracking_project_port(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    project_repo = container.project_repo(session=session)
    project_provider = container.project_provider(repo=project_repo)
    return container.timetracking_project_port(project_provider=project_provider)


async def get_timetracking_epic_port(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    epic_repo = container.epic_repo(session=session)
    epic_provider = container.epic_provider(repo=epic_repo)
    return container.timetracking_epic_port(epic_provider=epic_provider)


async def get_timetracking_event_bus(container: Container = Depends(get_container)):
    return container.timetracking_event_bus()


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


async def get_auth_token_port(container: Container = Depends(get_container)):
    return container.auth_token_port()


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
