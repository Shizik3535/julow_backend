"""
Conftest для integration-тестов.

Integration-тесты проверяют работу с реальными внешними сервисами
(БД, Redis, Kafka, S3/MinIO, SMTP/MailHog и т.д.).
Запускаются только при наличии подключений.
"""

import uuid
import warnings

import asyncpg
import pytest
import pytest_asyncio

from aiobotocore.session import AioSession
from aiokafka import AIOKafkaProducer
from celery import Celery
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.shared.infrastructure.auth.argon2_password_adapter import Argon2PasswordAdapter
from app.shared.infrastructure.auth.jwt_auth_adapter import JwtAuthAdapter
from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel

# Импортируем все ORM-модели, чтобы они зарегистрировались в BaseORMModel.metadata
# до вызова create_all. Без этих импортов таблицы не будут созданы в тестовой БД.
import app.context.identity.infrastructure.persistence.orm_models as _identity_orm  # noqa: F401
import app.context.organization.infrastructure.persistence.orm_models as _organization_orm  # noqa: F401
import app.context.profile.infrastructure.persistence.orm_models as _profile_orm  # noqa: F401
import app.context.project.infrastructure.persistence.orm_models as _project_orm  # noqa: F401
import app.context.task.infrastructure.persistence.orm_models as _task_orm  # noqa: F401
import app.context.workspace.infrastructure.persistence.orm_models as _workspace_orm  # noqa: F401


# ── Settings ─────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def app_settings():
    """Настройки приложения для тестов."""
    return settings


# ── Database ──────────────────────────────────────────────────────────────────


async def _ensure_pg_database(db_settings) -> str | None:
    """
    Пытается подключиться к PostgreSQL и создать тестовую БД если её нет.

    Возвращает URL для подключения или None если PostgreSQL недоступен.
    """
    try:
        conn = await asyncpg.connect(
            host=db_settings.host,
            port=db_settings.port,
            user=db_settings.user,
            password=db_settings.password,
            database="postgres",
        )
        try:
            exists = await conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1",
                db_settings.name,
            )
            if not exists:
                await conn.execute(
                    f'CREATE DATABASE "{db_settings.name}"',
                )
        finally:
            await conn.close()
        return db_settings.url
    except (OSError, asyncpg.PostgresError):
        return None


@pytest_asyncio.fixture(scope="session")
async def db_engine(app_settings):
    """
    Async SQLAlchemy engine для тестов.

    Стратегия:
        1. Попытка создать/использовать PostgreSQL тестовую БД.
        2. Если PostgreSQL недоступен — fallback на SQLite in-memory.

    Создаёт таблицы при старте, удаляет при завершении.
    """
    pg_url = await _ensure_pg_database(app_settings.db)

    if pg_url is not None:
        engine = create_async_engine(
            pg_url,
            echo=False,
            pool_size=1,
            max_overflow=0,
        )
    else:
        warnings.warn(
            "PostgreSQL недоступен — используется SQLite in-memory fallback.",
            stacklevel=1,
        )
        engine = create_async_engine(
            "sqlite+aiosqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False,
        )

    async with engine.begin() as conn:
        await conn.run_sync(BaseORMModel.metadata.create_all)

    # Seed system roles so FK constraints and role lookups work (PostgreSQL only)
    if pg_url is not None:
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

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(BaseORMModel.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def db_session_factory(db_engine):
    """Фабрика сессий (session-scoped)."""
    return async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture
async def db_session(db_session_factory):
    """
    Изолированная DB-сессия.

    Откатывается после каждого теста для изоляции данных.
    """
    async with db_session_factory() as session:
        yield session
        await session.rollback()


# ── Redis ────────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture(scope="session")
async def redis_client(app_settings):
    """Async Redis клиент для тестов. Очищает DB при завершении."""
    client = Redis(
        host=app_settings.redis.host,
        port=app_settings.redis.port,
        db=app_settings.redis.db,
        decode_responses=False,
    )
    yield client
    await client.flushdb()
    await client.aclose()


@pytest_asyncio.fixture
async def clean_redis(redis_client):
    """Очищает Redis перед каждым тестом."""
    await redis_client.flushdb()
    return redis_client


# ── Kafka ────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def kafka_bootstrap(app_settings):
    """Kafka bootstrap servers string."""
    return app_settings.kafka.bootstrap_servers


@pytest_asyncio.fixture(scope="session")
async def kafka_producer(kafka_bootstrap):
    """AIOKafkaProducer (session-scoped). Started/stopped automatically."""
    producer = AIOKafkaProducer(bootstrap_servers=kafka_bootstrap)
    await producer.start()
    yield producer
    await producer.stop()


# ── S3 / MinIO ──────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def s3_session():
    """AioSession для aiobotocore."""
    return AioSession()


@pytest.fixture(scope="session")
def s3_client_kwargs(app_settings):
    """Параметры для создания S3 клиента (MinIO)."""
    return {
        "endpoint_url": app_settings.s3.endpoint_url,
        "aws_access_key_id": app_settings.s3.access_key,
        "aws_secret_access_key": app_settings.s3.secret_key,
        "region_name": app_settings.s3.region,
    }


@pytest_asyncio.fixture
async def s3_test_bucket(s3_session, s3_client_kwargs):
    """
    Создаёт уникальный тестовый бакет, удаляет после теста.

    Возвращает имя бакета.
    """
    bucket_name = f"test-{uuid.uuid4().hex[:12]}"
    async with s3_session.create_client("s3", **s3_client_kwargs) as client:
        await client.create_bucket(Bucket=bucket_name)

    yield bucket_name

    async with s3_session.create_client("s3", **s3_client_kwargs) as client:
        # Удалить все объекты
        paginator = client.get_paginator("list_objects_v2")
        async for page in paginator.paginate(Bucket=bucket_name):
            for obj in page.get("Contents", []):
                await client.delete_object(Bucket=bucket_name, Key=obj["Key"])
        await client.delete_bucket(Bucket=bucket_name)


# ── SMTP (MailHog) ──────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def smtp_host(app_settings):
    """SMTP host (MailHog)."""
    return app_settings.smtp.host


@pytest.fixture(scope="session")
def smtp_port(app_settings):
    """SMTP port (MailHog)."""
    return app_settings.smtp.port


# ── Celery ───────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def celery_app(app_settings):
    """Celery app для тестов (eager mode — задачи выполняются синхронно)."""
    app = Celery("test-integration")
    app.conf.update(
        broker_url=app_settings.celery.broker_url,
        result_backend=app_settings.celery.result_backend,
    )
    return app


# ── Auth Adapters ────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def password_adapter():
    """Реальный Argon2PasswordAdapter."""
    return Argon2PasswordAdapter()


@pytest.fixture(scope="session")
def jwt_adapter(app_settings):
    """Реальный JwtAuthAdapter с тестовым секретом."""
    return JwtAuthAdapter(
        secret_key=app_settings.auth.jwt_secret_key,
        algorithm=app_settings.auth.jwt_algorithm,
        access_token_expire_minutes=app_settings.auth.access_token_expire_minutes,
        refresh_token_expire_days=app_settings.auth.refresh_token_expire_days,
    )


# ── Marker ───────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _integration_marker(request):
    """Проверяет, что тест помечен как integration."""
    if not request.node.get_closest_marker("integration"):
        pytest.skip("Test not marked as integration")
