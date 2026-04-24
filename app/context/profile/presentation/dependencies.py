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
    """
    Извлечь DI-контейнер из FastAPI application state.

    Контейнер создаётся один раз при старте приложения
    и сохраняется в ``app.state.container``.
    """
    return request.app.state.container


# ---------------------------------------------------------------------------
# Database session (per-request)
# ---------------------------------------------------------------------------


async def get_db_session(
    container: Container = Depends(get_container),
) -> AsyncGenerator[AsyncSession, None]:
    """
    Per-request сессия SQLAlchemy.

    Создаёт AsyncSession из session_factory, commit/rollback
    выполняется автоматически при завершении запроса.
    """
    session_factory = container.db_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ---------------------------------------------------------------------------
# Profile BC — Repositories
# ---------------------------------------------------------------------------


async def get_profile_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить UserProfileRepository из DI-контейнера."""
    return container.profile_repo(session=session)


# ---------------------------------------------------------------------------
# Profile BC — Integration ports
# ---------------------------------------------------------------------------


async def get_identity_user_port(container: Container = Depends(get_container)):
    """Получить IdentityUserPort (inbound) из DI-контейнера."""
    return container.profile_identity_user_port()


# ---------------------------------------------------------------------------
# Shared ports
# ---------------------------------------------------------------------------


async def get_auth_token_port(container: Container = Depends(get_container)):
    """Получить AuthTokenPort из DI-контейнера."""
    return container.auth_token_port()


async def get_message_broker_port(container: Container = Depends(get_container)):
    """Получить MessageBrokerPort из DI-контейнера."""
    return container.message_broker_port()


async def get_profile_event_bus(container: Container = Depends(get_container)):
    """Получить DomainEventBus Profile BC из DI-контейнера."""
    return container.profile_event_bus()


# ---------------------------------------------------------------------------
# Profile BC — BC-specific ports
# ---------------------------------------------------------------------------


async def get_file_storage_port(container: Container = Depends(get_container)):
    """Получить FileStoragePort из DI-контейнера."""
    return container.file_storage_port()


async def get_start_page_registry_port(container: Container = Depends(get_container)):
    """Получить StartPageRegistryPort из DI-контейнера."""
    return container.start_page_registry_port()


# ---------------------------------------------------------------------------
# Auth — текущий пользователь
# ---------------------------------------------------------------------------


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    auth_token_port: AuthTokenPort = Depends(get_auth_token_port),
) -> str:
    """
    Извлечь ID текущего аутентифицированного пользователя из JWT access-токена.

    Валидирует ``Authorization: Bearer <token>`` заголовок через ``AuthTokenPort``.

    Возвращает:
        UUID пользователя в строковом формате.

    Raises:
        HTTPException 401: Если токен отсутствует, невалиден или истёк.
    """
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
