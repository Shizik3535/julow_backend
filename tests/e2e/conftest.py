"""
Conftest для e2e-тестов.

E2E-тесты проверяют полный стек приложения через HTTP-запросы.
Используется httpx AsyncClient для асинхронных запросов.
"""

from __future__ import annotations

import uuid
import warnings
from typing import Any, AsyncGenerator

import asyncpg
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.config import settings
from app.core.di.container import wire_messaging
from app.main import create_app
from app.context.identity.application.ports.oauth.oauth_port import OAuthPort, OAuthUserInfo
from app.shared.application.ports.messaging.message_broker_port import (
    MessageBrokerPort,
    MessageHandler,
)
from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


# ── In-memory broker (заменяет Kafka в e2e-тестах) ───────────────────────────


class InMemoryMessageBrokerAdapter(MessageBrokerPort):
    """Заглушка брокера для e2e-тестов — не требует Kafka."""

    def __init__(self) -> None:
        self.published: list[dict[str, Any]] = []
        self._handlers: dict[str, list[MessageHandler]] = {}

    async def publish(self, topic: str, message: dict[str, Any], key: str | None = None) -> None:
        self.published.append({"topic": topic, "message": message, "key": key})
        for handler in self._handlers.get(topic, []):
            await handler(topic, message)

    async def subscribe(self, topic: str, group_id: str, handler: MessageHandler) -> None:
        self._handlers.setdefault(topic, []).append(handler)

    async def start(self) -> None:  # noqa: D102
        pass

    async def stop(self) -> None:  # noqa: D102
        pass

API = "/api/v1"


# ── In-memory OAuth (заменяет реальные запросы к Google/GitHub) ────────────────


class InMemoryOAuthAdapter(OAuthPort):
    """Заглушка OAuth для e2e-тестов — не делает реальных HTTP-запросов."""

    async def exchange_code(self, provider: str, code: str, redirect_uri: str) -> str:
        return f"mock-access-token-{provider}"

    async def get_user_info(self, provider: str, access_token: str) -> OAuthUserInfo:
        return OAuthUserInfo(
            provider_user_id=f"mock-user-id-{provider}",
            email=f"mock@{provider}.example.com",
            display_name=f"Mock User ({provider})",
        )


# ── App & Client ─────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def app():
    """Создаёт FastAPI приложение для e2e-тестов."""
    application = create_app()
    container = application.state.container
    container.message_broker_port.override(InMemoryMessageBrokerAdapter())
    container.oauth_port.override(InMemoryOAuthAdapter())
    return application


@pytest_asyncio.fixture(scope="session")
async def _db_tables(app):
    """Создаёт таблицы в тестовой БД перед e2e-тестами, удаляет после."""
    db = settings.db
    try:
        conn = await asyncpg.connect(
            host=db.host, port=db.port,
            user=db.user, password=db.password,
            database="postgres",
        )
        try:
            exists = await conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1", db.name,
            )
            if not exists:
                await conn.execute(f'CREATE DATABASE "{db.name}"')
        finally:
            await conn.close()
    except (OSError, asyncpg.PostgresError):
        warnings.warn(
            "PostgreSQL недоступен — e2e-тесты будут пропущены.",
            stacklevel=1,
        )
        pytest.skip("PostgreSQL недоступен")

    engine = app.state.container.db_engine()
    async with engine.begin() as conn:
        await conn.run_sync(BaseORMModel.metadata.create_all)

    # Seed system roles so FK constraints on user_roles are satisfied
    import json as _json
    from sqlalchemy import text as _sa_text
    from app.context.identity.infrastructure.persistence.seed.system_roles import SYSTEM_ROLES as _ROLES
    from app.context.organization.infrastructure.persistence.seed.org_roles import SYSTEM_ORG_ROLES as _ORG_ROLES
    from app.context.workspace.infrastructure.persistence.seed.system_workspace_roles import SYSTEM_WORKSPACE_ROLES as _WS_ROLES
    from app.context.project.infrastructure.persistence.seed.system_project_roles import SYSTEM_PROJECT_ROLES as _PROJ_ROLES
    async with engine.begin() as _conn:
        for _role in _ROLES:
            await _conn.execute(
                _sa_text(
                    "INSERT INTO roles (id, name, permissions, is_system, description, created_at, updated_at) "
                    "VALUES (:id, :name, CAST(:permissions AS jsonb), :is_system, :description, now(), now()) "
                    "ON CONFLICT (name) DO NOTHING"
                ),
                {
                    "id": str(_role["id"]),
                    "name": _role["name"],
                    "permissions": _json.dumps(_role["permissions"]),
                    "is_system": _role["is_system"],
                    "description": _role["description"],
                },
            )
        for _role in _ORG_ROLES:
            await _conn.execute(
                _sa_text(
                    "INSERT INTO org_roles (id, org_id, name, permissions, is_system, description, scope, created_at, updated_at) "
                    "VALUES (CAST(:id AS uuid), :org_id, :name, CAST(:permissions AS jsonb), :is_system, :description, :scope, now(), now()) "
                    "ON CONFLICT (id) DO NOTHING"
                ),
                {
                    "id": str(_role["id"]),
                    "org_id": _role["org_id"],
                    "name": _role["name"],
                    "permissions": _json.dumps(_role["permissions"]),
                    "is_system": _role["is_system"],
                    "description": _role["description"],
                    "scope": _role["scope"],
                },
            )
        for _role in _WS_ROLES:
            await _conn.execute(
                _sa_text(
                    "INSERT INTO workspace_roles "
                    "(id, workspace_id, name, permissions, is_system, description, created_at, updated_at) "
                    "VALUES (CAST(:id AS uuid), :workspace_id, :name, CAST(:permissions AS jsonb), "
                    ":is_system, :description, now(), now()) "
                    "ON CONFLICT (id) DO NOTHING"
                ),
                {
                    "id": str(_role["id"]),
                    "workspace_id": _role["workspace_id"],
                    "name": _role["name"],
                    "permissions": _json.dumps(_role["permissions"]),
                    "is_system": _role["is_system"],
                    "description": _role["description"],
                },
            )
        for _role in _PROJ_ROLES:
            await _conn.execute(
                _sa_text(
                    "INSERT INTO project_roles "
                    "(id, project_id, name, permissions, is_system, description, created_at, updated_at) "
                    "VALUES (CAST(:id AS uuid), :project_id, :name, CAST(:permissions AS jsonb), "
                    ":is_system, :description, now(), now()) "
                    "ON CONFLICT (id) DO NOTHING"
                ),
                {
                    "id": str(_role["id"]),
                    "project_id": _role["project_id"],
                    "name": _role["name"],
                    "permissions": _json.dumps(_role["permissions"]),
                    "is_system": _role["is_system"],
                    "description": _role["description"],
                },
            )

    # Wire messaging manually — httpx ASGITransport does not trigger
    # ASGI lifespan, so broker.start() / wire_messaging() never run.
    broker = app.state.container.message_broker_port()
    await broker.start()
    await wire_messaging(app.state.container)

    yield

    await broker.stop()
    async with engine.begin() as conn:
        await conn.run_sync(BaseORMModel.metadata.drop_all)


@pytest_asyncio.fixture
async def client(app, _db_tables) -> AsyncGenerator[AsyncClient, Any]:
    """Создаёт async HTTP-клиент для тестирования."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ── Helpers ──────────────────────────────────────────────────────────────────


def _unique_email() -> str:
    """Генерирует уникальный email для тестов."""
    return f"e2e-{uuid.uuid4().hex[:12]}@example.com"


DEFAULT_PASSWORD = "StrongP@ss1"


async def register_user(
    client: AsyncClient,
    *,
    email: str | None = None,
    password: str = DEFAULT_PASSWORD,
) -> dict:
    """
    Регистрирует нового пользователя и возвращает dict с данными.

    Возвращает:
        {"email": ..., "password": ..., "user_id": ..., "response": ...}
    """
    email = email or _unique_email()
    resp = await client.post(
        f"{API}/auth/register",
        json={"email": email, "password": password},
    )
    data = resp.json()
    user_id = data.get("data", {}).get("id", "")
    return {
        "email": email,
        "password": password,
        "user_id": user_id,
        "response": resp,
    }


async def login_user(
    client: AsyncClient,
    *,
    email: str,
    password: str = DEFAULT_PASSWORD,
) -> dict:
    """
    Логинит пользователя и возвращает dict с токенами.

    Возвращает:
        {"access_token": ..., "refresh_token": ..., "user": ..., "response": ...}
    """
    resp = await client.post(
        f"{API}/auth/login",
        json={"email": email, "password": password},
    )
    data = resp.json().get("data", {})
    return {
        "access_token": data.get("access_token", ""),
        "refresh_token": data.get("refresh_token", ""),
        "user": data.get("user", {}),
        "response": resp,
    }


async def register_and_login(
    client: AsyncClient,
    *,
    email: str | None = None,
    password: str = DEFAULT_PASSWORD,
) -> dict:
    """
    Регистрирует и логинит пользователя.

    Возвращает:
        {"email", "password", "user_id", "access_token", "refresh_token"}
    """
    reg = await register_user(client, email=email, password=password)
    log = await login_user(client, email=reg["email"], password=password)
    return {
        "email": reg["email"],
        "password": password,
        "user_id": reg["user_id"],
        "access_token": log["access_token"],
        "refresh_token": log["refresh_token"],
    }


def auth_headers(token: str) -> dict[str, str]:
    """Возвращает заголовки авторизации."""
    return {"Authorization": f"Bearer {token}"}


async def register_admin_and_login(
    client: AsyncClient,
    *,
    email: str | None = None,
    password: str = DEFAULT_PASSWORD,
) -> dict:
    """
    Регистрирует пользователя, назначает ему роль admin через БД,
    и логинит. Используется для тестов admin-эндпоинтов.

    Возвращает:
        {"email", "password", "user_id", "access_token", "refresh_token"}
    """
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

    from app.context.identity.infrastructure.persistence.seed.system_roles import SYSTEM_ROLES

    reg = await register_user(client, email=email, password=password)
    user_id = reg["user_id"]

    # Назначаем роль admin через прямой SQL (обход RBAC для тестового сетапа)
    _settings = settings
    engine = create_async_engine(_settings.db.url)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    admin_role_id = str(SYSTEM_ROLES[1]["id"])  # admin role
    async with session_factory() as session:
        await session.execute(
            text("INSERT INTO user_roles (user_id, role_id) VALUES (:uid, :rid) ON CONFLICT DO NOTHING"),
            {"uid": user_id, "rid": admin_role_id},
        )
        await session.commit()
    await engine.dispose()

    log = await login_user(client, email=reg["email"], password=password)
    return {
        "email": reg["email"],
        "password": password,
        "user_id": user_id,
        "access_token": log["access_token"],
        "refresh_token": log["refresh_token"],
    }


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def registered_user(client) -> dict:
    """
    Зарегистрированный и залогиненный пользователь.

    Возвращает dict:
        {"email", "password", "user_id", "access_token", "refresh_token"}
    """
    return await register_and_login(client)


@pytest_asyncio.fixture
async def auth_client(client, registered_user) -> AsyncClient:
    """
    Авторизованный HTTP-клиент.

    Устанавливает заголовок Authorization с JWT access-токеном.
    """
    client.headers["Authorization"] = f"Bearer {registered_user['access_token']}"
    return client


# ── Marker ───────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _e2e_marker(request):
    """Проверяет, что тест помечен как e2e."""
    if not request.node.get_closest_marker("e2e"):
        pytest.skip("Test not marked as e2e")
