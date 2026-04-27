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
    MessageHandler
)
from app.shared.application.ports.auth.password_port import PasswordPort
from sqlalchemy import text as _sa_text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


# ── Fast password stub (заменяет Argon2 в e2e-тестах) ──────────────────────────


class FastPasswordAdapter(PasswordPort):
    """Быстрая заглушка для e2e-тестов — не тратит время на argon2."""

    def hash_password(self, password: str) -> str:
        return f"fast${password}"

    def verify_password(self, password: str, password_hash: str) -> bool:
        return password_hash == f"fast${password}"


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
            display_name=f"Mock User ({provider})"
        )


# ── App & Client ─────────────────────────────────────────────────────────────


@pytest_asyncio.fixture(scope="session")
async def app():
    """Создаёт FastAPI приложение для e2e-тестов."""
    application = create_app()
    container = application.state.container
    container.message_broker_port.override(InMemoryMessageBrokerAdapter())
    container.oauth_port.override(InMemoryOAuthAdapter())
    container.password_port.override(FastPasswordAdapter())
    return application


@pytest_asyncio.fixture(scope="session")
async def _db_tables(app):
    """Создаёт таблицы в тестовой БД перед e2e-тестами, удаляет после."""
    db = settings.db
    try:
        conn = await asyncpg.connect(
            host=db.host, port=db.port,
            user=db.user, password=db.password,
            database="postgres"
        )
        try:
            exists = await conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1", db.name
            )
            if not exists:
                await conn.execute(f'CREATE DATABASE "{db.name}"')
        finally:
            await conn.close()
    except (OSError, asyncpg.PostgresError):
        warnings.warn(
            "PostgreSQL недоступен — e2e-тесты будут пропущены.",
            stacklevel=1
        )
        pytest.skip("PostgreSQL недоступен")

    engine = app.state.container.db_engine()
    async with engine.begin() as conn:
        await conn.run_sync(BaseORMModel.metadata.drop_all)
    async with engine.begin() as conn:
        await conn.run_sync(BaseORMModel.metadata.create_all, checkfirst=True)

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
                }
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
                }
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
                }
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
                }
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


@pytest_asyncio.fixture(scope="session")
async def client(app, _db_tables) -> AsyncGenerator[AsyncClient, Any]:
    """Создаёт async HTTP-клиент для тестирования (один на всю сессию)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# Таблицы, которые НЕ нужно TRUNCATE (seeded при старте сессии)
_SEEDED_TABLES = frozenset({"roles", "org_roles", "workspace_roles", "project_roles"})


async def _truncate_and_reseed_fast(app) -> None:
    """TRUNCATE таблиц и быстрое re-seeding системных ролей с batch insert.
    
    Оптимизация: используем executemany для ускорения re-seeding.
    """
    engine = app.state.container.db_engine()
    
    tables = [
        t.name for t in BaseORMModel.metadata.sorted_tables
        if t.name not in _SEEDED_TABLES
    ]
    
    if not tables:
        return
    
    # TRUNCATE с CASCADE (удалит и системные роли из-за FK)
    stmt = "TRUNCATE TABLE " + ", ".join(tables) + " CASCADE"
    async with engine.begin() as conn:
        await conn.execute(_sa_text(stmt))
    
    # Быстрое re-seeding системных ролей с executemany
    import json as _json
    from app.context.identity.infrastructure.persistence.seed.system_roles import SYSTEM_ROLES as _ROLES
    from app.context.organization.infrastructure.persistence.seed.org_roles import SYSTEM_ORG_ROLES as _ORG_ROLES
    from app.context.workspace.infrastructure.persistence.seed.system_workspace_roles import SYSTEM_WORKSPACE_ROLES as _WS_ROLES
    from app.context.project.infrastructure.persistence.seed.system_project_roles import SYSTEM_PROJECT_ROLES as _PROJ_ROLES
    
    async with engine.begin() as _conn:
        # Batch insert для roles
        if _ROLES:
            roles_data = [
                {
                    "id": str(_role["id"]),
                    "name": _role["name"],
                    "permissions": _json.dumps(_role["permissions"]),
                    "is_system": _role["is_system"],
                    "description": _role["description"],
                }
                for _role in _ROLES
            ]
            await _conn.execute(
                _sa_text(
                    "INSERT INTO roles (id, name, permissions, is_system, description, created_at, updated_at) "
                    "VALUES (:id, :name, CAST(:permissions AS jsonb), :is_system, :description, now(), now()) "
                    "ON CONFLICT (name) DO NOTHING"
                ),
                roles_data
            )
        
        # Batch insert для org_roles
        if _ORG_ROLES:
            org_roles_data = [
                {
                    "id": str(_role["id"]),
                    "org_id": _role["org_id"],
                    "name": _role["name"],
                    "permissions": _json.dumps(_role["permissions"]),
                    "is_system": _role["is_system"],
                    "description": _role["description"],
                    "scope": _role["scope"],
                }
                for _role in _ORG_ROLES
            ]
            await _conn.execute(
                _sa_text(
                    "INSERT INTO org_roles (id, org_id, name, permissions, is_system, description, scope, created_at, updated_at) "
                    "VALUES (CAST(:id AS uuid), :org_id, :name, CAST(:permissions AS jsonb), :is_system, :description, :scope, now(), now()) "
                    "ON CONFLICT (id) DO NOTHING"
                ),
                org_roles_data
            )
        
        # Batch insert для workspace_roles
        if _WS_ROLES:
            ws_roles_data = [
                {
                    "id": str(_role["id"]),
                    "workspace_id": _role["workspace_id"],
                    "name": _role["name"],
                    "permissions": _json.dumps(_role["permissions"]),
                    "is_system": _role["is_system"],
                    "description": _role["description"],
                }
                for _role in _WS_ROLES
            ]
            await _conn.execute(
                _sa_text(
                    "INSERT INTO workspace_roles (id, workspace_id, name, permissions, is_system, description, created_at, updated_at) "
                    "VALUES (CAST(:id AS uuid), :workspace_id, :name, CAST(:permissions AS jsonb), "
                    ":is_system, :description, now(), now()) "
                    "ON CONFLICT (id) DO NOTHING"
                ),
                ws_roles_data
            )
        
        # Batch insert для project_roles
        if _PROJ_ROLES:
            proj_roles_data = [
                {
                    "id": str(_role["id"]),
                    "project_id": _role["project_id"],
                    "name": _role["name"],
                    "permissions": _json.dumps(_role["permissions"]),
                    "is_system": _role["is_system"],
                    "description": _role["description"],
                }
                for _role in _PROJ_ROLES
            ]
            await _conn.execute(
                _sa_text(
                    "INSERT INTO project_roles "
                    "(id, project_id, name, permissions, is_system, description, created_at, updated_at) "
                    "VALUES (CAST(:id AS uuid), :project_id, :name, CAST(:permissions AS jsonb), "
                    ":is_system, :description, now(), now()) "
                    "ON CONFLICT (id) DO NOTHING"
                ),
                proj_roles_data
            )


@pytest_asyncio.fixture(autouse=True)
async def _clean_db_after_test(app):
    """TRUNCATE данных после каждого теста с оптимизированным re-seeding.

    Гарантирует полную изоляцию: каждый тест начинает с чистой БД.
    Оптимизировано: batch insert вместо цикла для ускорения re-seeding.
    """
    yield
    await _truncate_and_reseed_fast(app)


# ── Fixtures для workspace ───────────────────────────────────────────────────


@pytest_asyncio.fixture
async def workspace_owner(client: AsyncClient) -> dict:
    """Создаёт workspace с владельцем."""
    return await create_workspace_with_owner(client)


@pytest_asyncio.fixture
async def workspace_in_org(client: AsyncClient) -> dict:
    """Создаёт workspace внутри организации."""
    return await create_workspace_in_org(client)


@pytest_asyncio.fixture
async def workspace_lifecycle(client: AsyncClient) -> dict:
    """Создаёт workspace с именем 'Lifecycle WS' для теста lifecycle."""
    user = await register_and_login(client)
    ws = await create_workspace(client, token=user["access_token"], name="Lifecycle WS")
    return {**user, "ws_id": ws["ws_id"], "ws_name": ws["ws_name"]}


# ── Helpers ──────────────────────────────────────────────────────────────────


def _unique_email() -> str:
    """Генерирует уникальный email для тестов."""
    return f"e2e-{uuid.uuid4().hex[:12]}@example.com"


DEFAULT_PASSWORD = "StrongP@ss1"


async def register_user(
    client: AsyncClient,
    *,
    email: str | None = None,
    password: str = DEFAULT_PASSWORD
) -> dict:
    """
    Регистрирует нового пользователя и возвращает dict с данными.

    Возвращает:
        {"email": ..., "password": ..., "user_id": ..., "response": ...}
    """
    email = email or _unique_email()
    resp = await client.post(
        f"{API}/auth/register",
        json={"email": email, "password": password}
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
    password: str = DEFAULT_PASSWORD
) -> dict:
    """
    Логинит пользователя и возвращает dict с токенами.

    Возвращает:
        {"access_token": ..., "refresh_token": ..., "user": ..., "response": ...}
    """
    resp = await client.post(
        f"{API}/auth/login",
        json={"email": email, "password": password}
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
    password: str = DEFAULT_PASSWORD
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
    app,
    *,
    email: str | None = None,
    password: str = DEFAULT_PASSWORD
) -> dict:
    """
    Регистрирует пользователя, назначает ему роль admin через БД,
    и логинит. Используется для тестов admin-эндпоинтов.

    Возвращает:
        {"email", "password", "user_id", "access_token", "refresh_token"}
    """
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

    from app.context.identity.infrastructure.persistence.seed.system_roles import SYSTEM_ROLES

    reg = await register_user(client, email=email, password=password)
    user_id = reg["user_id"]

    # Назначаем роль admin через прямой SQL (обход RBAC для тестового сетапа)
    # Используем engine из контейнера
    engine = app.state.container.db_engine()
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    admin_role_id = str(SYSTEM_ROLES[1]["id"])  # admin role
    async with session_factory() as session:
        await session.execute(
            text("INSERT INTO user_roles (user_id, role_id) VALUES (:uid, :rid) ON CONFLICT DO NOTHING"),
            {"uid": user_id, "rid": admin_role_id}
        )
        await session.commit()

    log = await login_user(client, email=reg["email"], password=password)
    return {
        "email": reg["email"],
        "password": password,
        "user_id": user_id,
        "access_token": log["access_token"],
        "refresh_token": log["refresh_token"],
    }


async def create_organization(
    client: AsyncClient,
    *,
    token: str,
    name: str | None = None
) -> dict:
    """
    Создаёт организацию через API.

    Возвращает:
        {"org_id": ..., "org_name": ..., "response": ...}
    """
    name = name or f"e2e-org-{uuid.uuid4().hex[:8]}"
    resp = await client.post(
        f"{API}/orgs/",
        json={"name": name},
        headers=auth_headers(token)
    )
    data = resp.json().get("data", {})
    return {"org_id": data.get("id", ""), "org_name": name, "response": resp}


async def create_org_with_owner(client: AsyncClient) -> dict:
    """
    Регистрирует пользователя, логинит, создаёт организацию.

    Возвращает:
        {"email", "password", "user_id", "access_token", "refresh_token", "org_id", "org_name"}
    """
    user = await register_and_login(client)
    org = await create_organization(client, token=user["access_token"])
    return {**user, "org_id": org["org_id"], "org_name": org["org_name"]}


async def add_member_to_org(
    client: AsyncClient,
    *,
    org_id: str,
    owner_token: str,
    new_member_user_id: str,
    role_id: str | None = None
) -> dict:
    """
    Добавляет участника в организацию через API.

    Возвращает:
        {"response": ...}
    """
    body: dict[str, Any] = {"user_id": new_member_user_id}
    if role_id:
        body["role_id"] = role_id
    resp = await client.post(
        f"{API}/orgs/{org_id}/members",
        json=body,
        headers=auth_headers(owner_token)
    )
    return {"response": resp}


async def create_workspace(
    client: AsyncClient,
    *,
    token: str,
    name: str | None = None,
    organization_id: str | None = None,
    parent_workspace_id: str | None = None
) -> dict:
    """
    Создаёт workspace через API.

    Возвращает:
        {"ws_id": ..., "ws_name": ..., "response": ...}
    """
    name = name or f"e2e-ws-{uuid.uuid4().hex[:8]}"
    body: dict[str, Any] = {"name": name}
    if organization_id:
        body["organization_id"] = organization_id
    if parent_workspace_id:
        body["parent_workspace_id"] = parent_workspace_id
    resp = await client.post(
        f"{API}/workspaces/",
        json=body,
        headers=auth_headers(token)
    )
    data = resp.json().get("data", {})
    return {"ws_id": data.get("id", ""), "ws_name": name, "response": resp}


async def create_workspace_with_owner(
    client: AsyncClient,
    *,
    organization_id: str | None = None,
    name: str | None = None
) -> dict:
    """
    Регистрирует пользователя, логинит, создаёт workspace.

    Возвращает:
        {"email", "password", "user_id", "access_token", "refresh_token", "ws_id", "ws_name"}
    """
    user = await register_and_login(client)
    ws = await create_workspace(
        client,
        token=user["access_token"],
        name=name,
        organization_id=organization_id
    )
    return {**user, "ws_id": ws["ws_id"], "ws_name": ws["ws_name"]}


async def create_workspace_in_org(client: AsyncClient) -> dict:
    """
    Регистрирует пользователя, логинит, создаёт организацию,
    затем создаёт workspace внутри организации.

    Возвращает:
        {"email", "password", "user_id", "access_token", "refresh_token",
         "org_id", "org_name", "ws_id", "ws_name"}
    """
    user = await register_and_login(client)
    org = await create_organization(client, token=user["access_token"])
    ws = await create_workspace(
        client,
        token=user["access_token"],
        organization_id=org["org_id"]
    )
    return {
        **user,
        "org_id": org["org_id"],
        "org_name": org["org_name"],
        "ws_id": ws["ws_id"],
        "ws_name": ws["ws_name"],
    }


async def add_member_to_workspace(
    client: AsyncClient,
    *,
    ws_id: str,
    owner_token: str,
    new_member_user_id: str,
    role_id: str
) -> dict:
    """
    Добавляет участника в workspace через API.

    Возвращает:
        {"response": ...}
    """
    body: dict[str, Any] = {"user_id": new_member_user_id, "role_id": role_id}
    resp = await client.post(
        f"{API}/workspaces/{ws_id}/members",
        json=body,
        headers=auth_headers(owner_token)
    )
    return {"response": resp}


async def add_ws_member_with_role(
    client: AsyncClient,
    *,
    ws_id: str,
    owner_token: str,
    new_member_user_id: str,
    role_name: str
) -> dict:
    """
    Добавляет участника с конкретной ролью по имени (owner/admin/manager/member).
    Находит role_id через GET /workspaces/{ws_id}/roles?system_only=true.

    Возвращает:
        {"response": ..., "role_id": ...}
    """
    roles_resp = await client.get(
        f"{API}/workspaces/{ws_id}/roles",
        params={"system_only": True},
        headers=auth_headers(owner_token)
    )
    roles = roles_resp.json().get("items", [])
    role_id = ""
    for r in roles:
        if r.get("name") == role_name:
            role_id = r.get("id", "")
            break
    if not role_id:
        raise ValueError(f"System role '{role_name}' not found in workspace {ws_id}")
    result = await add_member_to_workspace(
        client,
        ws_id=ws_id,
        owner_token=owner_token,
        new_member_user_id=new_member_user_id,
        role_id=role_id
    )
    return {**result, "role_id": role_id}


# ── Project helpers ──────────────────────────────────────────────────────────


async def create_project(
    client: AsyncClient,
    *,
    ws_id: str,
    token: str,
    name: str | None = None,
    methodology: str = "scrum"
) -> dict:
    """
    Создаёт проект через API.

    Возвращает:
        {"project_id": ..., "project_name": ..., "response": ...}
    """
    name = name or f"e2e-project-{uuid.uuid4().hex[:8]}"
    resp = await client.post(
        f"{API}/workspaces/{ws_id}/projects/",
        json={"name": name, "methodology": methodology},
        headers=auth_headers(token)
    )
    data = resp.json().get("data", {})
    return {"project_id": data.get("id", ""), "project_name": name, "response": resp}


async def create_project_with_owner(
    client: AsyncClient,
    *,
    methodology: str = "kanban"
) -> dict:
    """
    Регистрирует пользователя, логинит, создаёт workspace, создаёт проект.

    Возвращает:
        {"email", "password", "user_id", "access_token", "refresh_token",
         "ws_id", "ws_name", "project_id", "project_name"}
    """
    ws = await create_workspace_with_owner(client)
    proj = await create_project(
        client, ws_id=ws["ws_id"], token=ws["access_token"], methodology=methodology
    )
    return {**ws, "project_id": proj["project_id"], "project_name": proj["project_name"]}


async def add_project_member_with_role(
    client: AsyncClient,
    *,
    ws_id: str,
    project_id: str,
    owner_token: str,
    new_member_user_id: str,
    role_name: str
) -> dict:
    """
    Добавляет участника в проект с конкретной ролью по имени
    (owner/admin/manager/member/guest).
    Сначала добавляет пользователя в workspace (роль member),
    затем — в проект. Находит role_id через API.

    Возвращает:
        {"response": ..., "role_id": ...}
    """
    # Сначала добавляем пользователя в workspace (иначе проект вернёт 400)
    await add_ws_member_with_role(
        client,
        ws_id=ws_id,
        owner_token=owner_token,
        new_member_user_id=new_member_user_id,
        role_name="member"
    )

    roles_resp = await client.get(
        f"{API}/workspaces/{ws_id}/projects/{project_id}/roles",
        headers=auth_headers(owner_token)
    )
    roles_data = roles_resp.json().get("data", [])
    roles = roles_data if isinstance(roles_data, list) else roles_data.get("items", [])
    role_id = ""
    for r in roles:
        if r.get("name") == role_name:
            role_id = r.get("id", "")
            break
    if not role_id:
        raise ValueError(f"Role '{role_name}' not found in project {project_id}")
    resp = await client.post(
        f"{API}/workspaces/{ws_id}/projects/{project_id}/members",
        json={"user_id": new_member_user_id, "role_id": role_id},
        headers=auth_headers(owner_token)
    )
    return {"response": resp, "role_id": role_id}


# ── Task helpers ─────────────────────────────────────────────────────────────


async def create_task(
    client: AsyncClient,
    *,
    ws_id: str,
    project_id: str,
    token: str,
    title: str | None = None,
    task_type: str = "task",
    reporter_id: str | None = None,
    parent_task_id: str | None = None,
    epic_id: str | None = None,
) -> dict:
    """
    Создаёт задачу через API.

    Возвращает:
        {"task_id": ..., "title": ..., "response": ...}
    """
    title = title or f"e2e-task-{uuid.uuid4().hex[:8]}"
    resp = await client.post(
        f"{API}/workspaces/{ws_id}/projects/{project_id}/tasks",
        json={
            "title": title,
            "task_type": task_type,
            "reporter_id": reporter_id,
            "parent_task_id": parent_task_id,
            "epic_id": epic_id,
        },
        headers=auth_headers(token)
    )
    data = resp.json().get("data", {})
    return {"task_id": data.get("id", ""), "title": title, "response": resp}


async def create_task_with_project(
    client: AsyncClient,
    *,
    methodology: str = "scrum"
) -> dict:
    """
    Регистрирует пользователя, логинит, создаёт workspace, проект и задачу.

    Возвращает:
        {"email", "password", "user_id", "access_token", "refresh_token",
         "ws_id", "ws_name", "project_id", "project_name", "task_id", "title"}
    """
    proj = await create_project_with_owner(client, methodology=methodology)
    task = await create_task(
        client,
        ws_id=proj["ws_id"],
        project_id=proj["project_id"],
        token=proj["access_token"]
    )
    return {**proj, "task_id": task["task_id"], "title": task["title"]}


async def create_task_template(
    client: AsyncClient,
    *,
    ws_id: str,
    project_id: str,
    token: str,
    name: str | None = None,
    task_type: str = "task",
) -> dict:
    """
    Создаёт шаблон задачи через API.

    Возвращает:
        {"template_id": ..., "name": ..., "response": ...}
    """
    name = name or f"e2e-template-{uuid.uuid4().hex[:8]}"
    resp = await client.post(
        f"{API}/workspaces/{ws_id}/projects/{project_id}/task-templates",
        json={
            "name": name,
            "task_type": task_type,
        },
        headers=auth_headers(token)
    )
    data = resp.json().get("data", {})
    return {"template_id": data.get("id", ""), "name": name, "response": resp}


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
    Очищает заголовок после использования тестом.
    """
    client.headers["Authorization"] = f"Bearer {registered_user['access_token']}"
    yield client
    client.headers.pop("Authorization", None)


# ── Fixtures (1 setup на тест) ──────────────────────────────────────────────


@pytest_asyncio.fixture
async def workspace_owner(client) -> dict:
    """
    Регистрирует пользователя и создаёт workspace — 1 раз на тест.

    Возвращает dict:
        {"email", "password", "user_id", "access_token", "refresh_token", "ws_id", "ws_name"}
    """
    return await create_workspace_with_owner(client)


@pytest_asyncio.fixture
async def org_with_owner(client) -> dict:
    """
    Регистрирует пользователя и создаёт организацию — 1 раз на тест.

    Возвращает dict:
        {"email", "password", "user_id", "access_token", "refresh_token", "org_id", "org_name"}
    """
    return await create_org_with_owner(client)


@pytest_asyncio.fixture
async def project_owner(client) -> dict:
    """
    Регистрирует пользователя, создаёт workspace и проект — 1 раз на тест.

    Возвращает dict:
        {"email", "password", "user_id", "access_token", "refresh_token",
         "ws_id", "ws_name", "project_id", "project_name"}
    """
    return await create_project_with_owner(client, methodology="scrum")


@pytest_asyncio.fixture
async def workspace_in_org(client) -> dict:
    """
    Регистрирует пользователя, создаёт организацию и workspace в ней — 1 раз на тест.

    Возвращает dict:
        {"email", "password", "user_id", "access_token", "refresh_token",
         "org_id", "org_name", "ws_id", "ws_name"}
    """
    return await create_workspace_in_org(client)


# ── Marker ───────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _e2e_marker(request):
    """Проверяет, что тест помечен как e2e."""
    if not request.node.get_closest_marker("e2e"):
        pytest.skip("Test not marked as e2e")
