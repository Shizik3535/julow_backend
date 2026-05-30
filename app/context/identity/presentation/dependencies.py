from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.di.container import Container
from app.context.identity.domain.value_objects.failed_login_policy import FailedLoginPolicy
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
# Identity BC — Repositories
# ---------------------------------------------------------------------------


async def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить UserRepository из DI-контейнера."""
    return container.user_repo(session=session)


async def get_user_auth_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить UserAuthRepository из DI-контейнера."""
    return container.user_auth_repo(session=session)


async def get_session_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить SessionRepository из DI-контейнера."""
    return container.session_repo(session=session)


async def get_role_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить RoleRepository из DI-контейнера."""
    return container.role_repo(session=session)


# ---------------------------------------------------------------------------
# Shared ports
# ---------------------------------------------------------------------------


async def get_password_port(container: Container = Depends(get_container)):
    """Получить PasswordPort из DI-контейнера."""
    return container.password_port()


async def get_auth_token_port(container: Container = Depends(get_container)):
    """Получить AuthTokenPort из DI-контейнера."""
    return container.auth_token_port()


async def get_message_broker_port(container: Container = Depends(get_container)):
    """Получить MessageBrokerPort из DI-контейнера."""
    return container.message_broker_port()


async def get_identity_event_bus(container: Container = Depends(get_container)):
    """Получить DomainEventBus Identity BC из DI-контейнера."""
    return container.identity_event_bus()


async def get_totp_port(container: Container = Depends(get_container)):
    """Получить TOTPPort из DI-контейнера."""
    return container.totp_port()


async def get_oauth_port(container: Container = Depends(get_container)):
    """Получить OAuthPort из DI-контейнера."""
    return container.oauth_port()


async def get_identity_notification_port(container: Container = Depends(get_container)):
    """Получить IdentityNotificationPort из DI-контейнера."""
    return container.identity_notification_port()


async def get_sso_port(container: Container = Depends(get_container)):
    """Получить SSOPort из DI-контейнера."""
    return container.sso_port()


async def get_organization_sso_port(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить OrganizationSSOPort (inboard) из DI-контейнера.

    `identity_org_sso_port` оборачивает `org_sso_provider`, который, в свою
    очередь, зависит от двух session-scoped репозиториев. dependency-injector
    не пробрасывает kwargs во вложенные провайдеры, поэтому пре-резолвим их
    вручную (как в `get_permission_checker`).
    """
    sso_repo = container.sso_integration_repo(session=session)
    org_repo = container.organization_repo(session=session)
    org_sso_provider = container.org_sso_provider(
        sso_repo=sso_repo,
        org_repo=org_repo,
    )
    return container.identity_org_sso_port(org_sso_provider=org_sso_provider)


async def get_failed_login_policy(container: Container = Depends(get_container)) -> FailedLoginPolicy:
    """Получить FailedLoginPolicy из DI-контейнера."""
    return container.failed_login_policy()


async def get_cache_port(container: Container = Depends(get_container)):
    """Получить CachePort (Redis) из DI-контейнера."""
    return container.cache_port()


async def get_permission_checker(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить PermissionCheckerPort из DI-контейнера."""
    from app.context.identity.application.ports.authorization.permission_checker_port import PermissionCheckerPort
    user_repo = container.user_repo(session=session)
    role_repo = container.role_repo(session=session)
    return container.permission_checker(user_repo=user_repo, role_repo=role_repo)


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
