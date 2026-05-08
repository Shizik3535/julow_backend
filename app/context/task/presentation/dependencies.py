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
# Task BC — Repositories
# ---------------------------------------------------------------------------


async def get_task_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить TaskRepository из DI-контейнера."""
    return container.task_repo(session=session)


async def get_task_template_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить TaskTemplateRepository из DI-контейнера."""
    return container.task_template_repo(session=session)


async def get_task_changelog_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить ChangelogRepository из DI-контейнера."""
    return container.changelog_repo(session=session)


# ---------------------------------------------------------------------------
# Task BC — Authorization
# ---------------------------------------------------------------------------


async def get_task_permission_checker(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить TaskPermissionCheckerPort из DI-контейнера."""
    # Task-level repo
    task_repo = container.task_repo(session=session)
    # Project membership chain (for task_project_membership_port)
    project_membership_repo = container.project_membership_repo(session=session)
    project_membership_provider = container.project_membership_provider(repo=project_membership_repo)
    task_project_membership_port = container.task_project_membership_port(
        project_membership_provider=project_membership_provider,
    )
    # Project permission chain (for project_permission_provider)
    project_role_repo = container.project_role_repo(session=session)
    project_repo = container.project_repo(session=session)
    # Workspace-level chain (for workspace_permission_checker inside project_permission_checker)
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
    project_permission_checker = container.project_permission_checker(
        membership_repo=project_membership_repo,
        project_role_repo=project_role_repo,
        project_repo=project_repo,
        workspace_permission_checker=ws_permission_checker,
    )
    project_permission_provider = container.project_permission_provider(checker=project_permission_checker)
    return container.task_permission_checker_port(
        task_repo=task_repo,
        project_membership_port=task_project_membership_port,
        project_permission_provider=project_permission_provider,
    )


# ---------------------------------------------------------------------------
# Task BC — Integration inboard ports
# ---------------------------------------------------------------------------


async def get_task_identity_user_port(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить IdentityUserPort (inboard) из DI-контейнера."""
    user_repo = container.user_repo(session=session)
    identity_user_provider = container.identity_user_provider(user_repo=user_repo)
    return container.task_identity_user_port(identity_user_provider=identity_user_provider)


async def get_task_project_port(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить ProjectPort (inboard) из DI-контейнера."""
    project_repo = container.project_repo(session=session)
    project_provider = container.project_provider(repo=project_repo)
    return container.task_project_port(project_provider=project_provider)


async def get_task_project_membership_port(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить ProjectMembershipPort (inboard) из DI-контейнера."""
    project_membership_repo = container.project_membership_repo(session=session)
    project_membership_provider = container.project_membership_provider(repo=project_membership_repo)
    return container.task_project_membership_port(project_membership_provider=project_membership_provider)


async def get_task_board_port(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить BoardPort (inboard) из DI-контейнера."""
    board_repo = container.board_repo(session=session)
    board_provider = container.board_provider(repo=board_repo)
    return container.task_board_port(board_provider=board_provider)


async def get_task_sprint_port(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить SprintPort (inboard) из DI-контейнера."""
    sprint_repo = container.sprint_repo(session=session)
    sprint_provider = container.sprint_provider(repo=sprint_repo)
    return container.task_sprint_port(sprint_provider=sprint_provider)


async def get_task_epic_port(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить EpicPort (inboard) из DI-контейнера."""
    epic_repo = container.epic_repo(session=session)
    epic_provider = container.epic_provider(repo=epic_repo)
    return container.task_epic_port(epic_provider=epic_provider)


# ---------------------------------------------------------------------------
# Task BC — Event Bus
# ---------------------------------------------------------------------------


async def get_task_event_bus(container: Container = Depends(get_container)):
    """Получить DomainEventBus Task BC из DI-контейнера."""
    return container.task_event_bus()


# ---------------------------------------------------------------------------
# Shared ports
# ---------------------------------------------------------------------------


async def get_auth_token_port(container: Container = Depends(get_container)):
    """Получить AuthTokenPort из DI-контейнера."""
    return container.auth_token_port()


async def get_file_storage_port(container: Container = Depends(get_container)):
    """Получить FileStoragePort из DI-контейнера."""
    return container.file_storage_port()


async def get_task_file_attachment_port(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить FileAttachmentPort (inboard) для Task BC.

    Делегирует в FileStorage BC: создаёт агрегат ``File``, учитывает
    квоту workspace, эмитит ``FileUploaded`` / ``FileDeleted``.
    """
    file_repo = container.file_repo(session=session)
    storage_repo = container.storage_repo(session=session)
    file_storage = container.file_storage_port()
    event_bus = container.filestorage_event_bus()
    provider = container.file_attachment_provider(
        file_repo=file_repo,
        storage_repo=storage_repo,
        file_storage=file_storage,
        event_bus=event_bus,
    )
    return container.task_file_attachment_port(file_attachment_provider=provider)


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
