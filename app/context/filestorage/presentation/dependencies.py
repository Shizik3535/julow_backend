from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.di.container import Container
from app.shared.application.ports.auth.auth_exceptions import InvalidTokenException
from app.shared.application.ports.auth.auth_port import AuthTokenPort
from app.shared.application.ports.auth.password_port import PasswordPort

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
# Repositories
# ---------------------------------------------------------------------------


async def get_file_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить FileRepository из DI-контейнера."""
    return container.file_repo(session=session)


async def get_folder_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить FolderRepository из DI-контейнера."""
    return container.folder_repo(session=session)


async def get_storage_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить StorageRepository из DI-контейнера."""
    return container.storage_repo(session=session)


# ---------------------------------------------------------------------------
# Permission checker (workspace cascade)
# ---------------------------------------------------------------------------


async def get_fs_workspace_permission_checker(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить WorkspacePermissionCheckerPort для FileStorage BC."""
    ws_membership_repo = container.workspace_membership_repo(session=session)
    ws_role_repo = container.workspace_role_repo(session=session)
    ws_repo = container.workspace_repo(session=session)
    workspace_membership_provider = container.workspace_membership_provider(
        membership_repo=ws_membership_repo,
        workspace_role_repo=ws_role_repo,
        workspace_repo=ws_repo,
    )
    return container.fs_workspace_permission_checker_port(
        workspace_membership_provider=workspace_membership_provider,
    )


async def get_fs_identity_user_port(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить IdentityUserPort для FileStorage BC."""
    user_repo = container.user_repo(session=session)
    identity_user_provider = container.identity_user_provider(user_repo=user_repo)
    return container.fs_identity_user_port(identity_user_provider=identity_user_provider)


# ---------------------------------------------------------------------------
# Event Bus & external file storage
# ---------------------------------------------------------------------------


async def get_filestorage_event_bus(container: Container = Depends(get_container)):
    """Получить DomainEventBus FileStorage BC."""
    return container.filestorage_event_bus()


async def get_file_storage_port(container: Container = Depends(get_container)):
    """Получить FileStoragePort (S3-совместимое хранилище blob'ов)."""
    return container.file_storage_port()


async def get_block_pending_downloads(
    container: Container = Depends(get_container),
) -> bool:
    """Флаг блокировки скачивания PENDING-файлов (из ClamAvSettings)."""
    return container.settings().clamav.block_pending_downloads


async def get_password_port(container: Container = Depends(get_container)) -> PasswordPort:
    """Получить PasswordPort (argon2) из DI-контейнера."""
    return container.password_port()


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


async def get_auth_token_port(container: Container = Depends(get_container)):
    """Получить AuthTokenPort из DI-контейнера."""
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
