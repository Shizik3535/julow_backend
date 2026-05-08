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
# Communication BC — Repositories
# ---------------------------------------------------------------------------


async def get_comment_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить CommentRepository из DI-контейнера."""
    return container.comment_repo(session=session)


async def get_chat_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить ChatRepository из DI-контейнера."""
    return container.chat_repo(session=session)


async def get_message_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить MessageRepository из DI-контейнера."""
    return container.message_repo(session=session)


async def get_meeting_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить MeetingRepository из DI-контейнера."""
    return container.meeting_repo(session=session)


async def get_conference_provider_registry(
    container: Container = Depends(get_container),
):
    """Получить ConferenceProviderRegistry из DI-контейнера."""
    return container.conference_provider_registry()


async def get_comment_target_access_port(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить ``CommentTargetAccessPort`` из DI-контейнера.

    Адаптер делегирует в провайдеры Project/Task BC, которые читают
    БД через сессию текущего HTTP-запроса.
    """
    # Per-request repositories
    task_repo = container.task_repo(session=session)
    epic_repo = container.epic_repo(session=session)
    sprint_repo = container.sprint_repo(session=session)
    project_membership_repo = container.project_membership_repo(session=session)
    project_role_repo = container.project_role_repo(session=session)
    project_repo = container.project_repo(session=session)
    ws_membership_repo = container.workspace_membership_repo(session=session)
    ws_role_repo = container.workspace_role_repo(session=session)
    ws_repo = container.workspace_repo(session=session)

    # Project permission cascade (Project → Workspace)
    workspace_membership_provider = container.workspace_membership_provider(
        membership_repo=ws_membership_repo,
        workspace_role_repo=ws_role_repo,
        workspace_repo=ws_repo,
    )
    ws_permission_checker = container.project_ws_permission_checker_port(
        workspace_membership_provider=workspace_membership_provider,
    )
    project_permission_checker = container.project_permission_checker(
        membership_repo=project_membership_repo,
        project_role_repo=project_role_repo,
        project_repo=project_repo,
        workspace_permission_checker=ws_permission_checker,
    )
    project_permission_provider = container.project_permission_provider(
        checker=project_permission_checker,
    )

    # Outboard providers Task/Project BC
    task_provider = container.task_provider(repo=task_repo)
    epic_provider = container.epic_provider(repo=epic_repo)
    sprint_provider = container.sprint_provider(repo=sprint_repo)

    return container.comment_target_access_port(
        task_provider=task_provider,
        epic_provider=epic_provider,
        sprint_provider=sprint_provider,
        project_permission_provider=project_permission_provider,
    )


# ---------------------------------------------------------------------------
# Communication BC — Event Bus
# ---------------------------------------------------------------------------


async def get_communication_event_bus(container: Container = Depends(get_container)):
    """Получить DomainEventBus Communication BC из DI-контейнера."""
    return container.communication_event_bus()


# ---------------------------------------------------------------------------
# Auth — текущий пользователь
# ---------------------------------------------------------------------------


async def get_auth_token_port(container: Container = Depends(get_container)):
    """Получить AuthTokenPort из DI-контейнера."""
    return container.auth_token_port()


async def get_file_storage_port(container: Container = Depends(get_container)):
    """Получить FileStoragePort из DI-контейнера."""
    return container.file_storage_port()


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
