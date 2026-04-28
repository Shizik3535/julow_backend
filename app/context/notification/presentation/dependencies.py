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
# Notification BC — Repositories
# ---------------------------------------------------------------------------


async def get_notification_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить NotificationRepository из DI-контейнера."""
    return container.notification_repo(session=session)


async def get_notification_preferences_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить NotificationPreferencesRepository из DI-контейнера."""
    return container.notification_preferences_repo(session=session)


async def get_device_token_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить DeviceTokenRepository из DI-контейнера."""
    return container.device_token_repo(session=session)


# ---------------------------------------------------------------------------
# Notification BC — Event Bus
# ---------------------------------------------------------------------------


async def get_notification_event_bus(container: Container = Depends(get_container)):
    """Получить DomainEventBus Notification BC из DI-контейнера."""
    return container.notification_event_bus()


# ---------------------------------------------------------------------------
# Shared ports
# ---------------------------------------------------------------------------


async def get_auth_token_port(container: Container = Depends(get_container)):
    """Получить AuthTokenPort из DI-контейнера."""
    return container.auth_token_port()


# ---------------------------------------------------------------------------
# Auth — текущий пользователь
# ---------------------------------------------------------------------------


def get_settings(request: Request):
    """Получить Settings из application state."""
    return request.app.state.settings


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
