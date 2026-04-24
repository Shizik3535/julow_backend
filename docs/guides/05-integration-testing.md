# Гайд: Integration-тестирование

## Содержание

1. [Обзор](#1-обзор)
2. [Структура директорий](#2-структура-директорий)
3. [Конфигурация pytest](#3-конфигурация-pytest)
4. [Глобальный conftest](#4-глобальный-conftest)
5. [BC conftest: фикстуры и seed-хелперы](#5-bc-conftest-фикстуры-и-seed-хелперы)
6. [Тестирование Repositories](#6-тестирование-repositories)
7. [Тестирование Command Handlers](#7-тестирование-command-handlers)
8. [Тестирование Query Handlers](#8-тестирование-query-handlers)
9. [Тестирование Event Handlers](#9-тестирование-event-handlers)
10. [Тестирование Adapters](#10-тестирование-adapters)
11. [Cross-context тесты](#11-cross-context-тесты)
12. [Конвенции и антипаттерны](#12-конвенции-и-антипаттерны)
13. [Чеклист нового BC](#13-чеклист-нового-bc)

---

## 1. Обзор

Integration-тесты проверяют взаимодействие компонентов с **реальными внешними сервисами**: PostgreSQL, Redis, Kafka, S3/MinIO, SMTP/MailHog. В отличие от unit-тестов, здесь мы не мокаем инфраструктуру — мы проверяем, что mappers, repositories, handlers и adapters корректно работают с настоящими хранилищами и протоколами.

### Отличие от unit и e2e

| Уровень | Что тестируем | Внешние зависимости | Скорость |
|---|---|---|---|
| **Unit** | Чистая бизнес-логика (domain) | Нет | Миллисекунды |
| **Integration** | Repos, handlers, adapters + реальные БД/брокеры | PostgreSQL, Redis, Kafka, SMTP | Секунды |
| **E2E** | HTTP API (full stack) | Всё + FastAPI | Секунды–минуты |

### Принципы

- **Реальные сервисы**: PostgreSQL вместо SQLite (с fallback), Kafka вместо in-memory, SMTP через MailHog.
- **Изоляция по тестам**: каждый тест работает в своей DB-сессии с `rollback` после завершения.
- **Seed-хелперы**: данные создаются через фабрики-фикстуры (`make_user`, `make_role`), а не через raw SQL.
- **Маркер `@pytest.mark.integration`**: обязателен для каждого тест-класса.
- **Async**: все тесты — `async def`, работают через `pytest-asyncio`.

### Что тестируем

| Компонент | Что проверяем |
|---|---|
| **Repository** | CRUD, поиск, пагинация, сохранение дочерних коллекций, маппинг domain ↔ ORM |
| **Command Handler** | Полный цикл: команда → handler → repo → БД, события |
| **Query Handler** | Запрос → handler → repo → DTO |
| **Event Handler** | Событие → handler → side-effect в БД |
| **Adapter** | TOTP (pyotp), OAuth (respx), SMTP (MailHog), S3 (MinIO) |
| **Cross-context** | Outboard provider → inbound adapter между BC |

---

## 2. Структура директорий

```
tests/integration/
├── __init__.py
├── conftest.py                          # Глобальные фикстуры: DB, Redis, Kafka, S3, SMTP, Auth
├── <bc_name>/
│   ├── __init__.py
│   ├── conftest.py                      # BC-level: mappers, repos, seed-хелперы
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── test_sql_<aggregate>_repository.py
│   ├── commands/
│   │   ├── __init__.py
│   │   └── test_<command_name>.py
│   ├── queries/
│   │   ├── __init__.py
│   │   └── test_<query_name>.py
│   ├── event_handlers/
│   │   ├── __init__.py
│   │   └── test_on_<event>_<action>.py
│   └── adapters/
│       ├── __init__.py
│       └── test_<adapter_name>.py
└── cross_context/
    ├── __init__.py
    ├── conftest.py                      # Фикстуры из нескольких BC
    └── test_<adapter_name>.py
```

### Правило именования файлов

| Категория | Имя файла | Пример |
|---|---|---|
| Repository | `test_sql_<aggregate>_repository.py` | `test_sql_user_repository.py` |
| Command | `test_<command_name>.py` | `test_register_user.py`, `test_assign_role.py` |
| Query | `test_<query_name>.py` | `test_get_active_sessions.py`, `test_get_roles.py` |
| Event handler | `test_on_<event>_<action>.py` | `test_on_user_logged_in.py` |
| Adapter | `test_<adapter_name>.py` | `test_totp_adapter.py`, `test_oauth_adapter.py` |
| Cross-context | `test_<adapter_name>.py` | `test_identity_user_adapter.py` |

---

## 3. Конфигурация pytest

### Маркеры (`pyproject.toml`)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
markers = [
    "unit: Unit tests (no external dependencies)",
    "integration: Integration tests (DB, Redis, etc.)",
    "e2e: End-to-end tests (full HTTP stack)",
]
addopts = [
    "--strict-markers",
    "--strict-config",
    "-v",
]
```

### Запуск

```bash
pytest -m integration                           # все integration-тесты
pytest tests/integration                        # по директории
pytest tests/integration/identity               # один BC
pytest tests/integration/identity/repositories  # одна категория
pytest tests/integration/identity/commands/test_register_user.py  # один файл
pytest tests/integration/cross_context          # cross-context тесты
```

### Autouse marker (`tests/integration/conftest.py`)

```python
@pytest.fixture(autouse=True)
def _integration_marker(request):
    """Проверяет, что тест помечен как integration."""
    if not request.node.get_closest_marker("integration"):
        pytest.skip("Test not marked as integration")
```

**Важно**: если забыть `@pytest.mark.integration`, тест будет пропущен.

---

## 4. Глобальный conftest

Файл `tests/integration/conftest.py` предоставляет инфраструктурные фикстуры для **всех** integration-тестов.

### 4.1. Database

```python
@pytest_asyncio.fixture(scope="session")
async def db_engine(app_settings):
    """
    Async SQLAlchemy engine.

    Стратегия:
        1. PostgreSQL тестовая БД (создаётся если нет).
        2. Fallback на SQLite in-memory если PG недоступен.

    Создаёт таблицы + seed system roles при старте, drop при завершении.
    """
    pg_url = await _ensure_pg_database(app_settings.db)

    if pg_url is not None:
        engine = create_async_engine(pg_url, echo=False, pool_size=1, max_overflow=0)
    else:
        warnings.warn("PostgreSQL недоступен — SQLite in-memory fallback.")
        engine = create_async_engine(
            "sqlite+aiosqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

    async with engine.begin() as conn:
        await conn.run_sync(BaseORMModel.metadata.create_all)

    # Seed system roles (PostgreSQL only)
    if pg_url is not None:
        # ... INSERT INTO roles ... ON CONFLICT DO NOTHING

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(BaseORMModel.metadata.drop_all)
    await engine.dispose()
```

**Ключевые моменты:**
- **scope="session"** — engine создаётся один раз на весь прогон.
- **Автоматический seed** — системные роли вставляются для удовлетворения FK constraints.
- **Fallback** — SQLite позволяет запускать часть тестов без PostgreSQL.

### 4.2. DB Session (изоляция)

```python
@pytest_asyncio.fixture(scope="session")
async def db_session_factory(db_engine):
    """Фабрика сессий (session-scoped)."""
    return async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def db_session(db_session_factory):
    """Изолированная DB-сессия. Откатывается после каждого теста."""
    async with db_session_factory() as session:
        yield session
        await session.rollback()
```

**Важно**: `expire_on_commit=False` — чтобы атрибуты ORM-объектов оставались доступными после `commit`. Rollback в конце — изоляция данных между тестами.

### 4.3. Redis

```python
@pytest_asyncio.fixture(scope="session")
async def redis_client(app_settings):
    """Async Redis клиент. Очищает DB при завершении."""
    client = Redis(host=..., port=..., db=..., decode_responses=False)
    yield client
    await client.flushdb()
    await client.aclose()


@pytest_asyncio.fixture
async def clean_redis(redis_client):
    """Очищает Redis перед каждым тестом."""
    await redis_client.flushdb()
    return redis_client
```

### 4.4. Kafka

```python
@pytest.fixture(scope="session")
def kafka_bootstrap(app_settings):
    return app_settings.kafka.bootstrap_servers


@pytest_asyncio.fixture(scope="session")
async def kafka_producer(kafka_bootstrap):
    """AIOKafkaProducer (session-scoped). Started/stopped automatically."""
    producer = AIOKafkaProducer(bootstrap_servers=kafka_bootstrap)
    await producer.start()
    yield producer
    await producer.stop()
```

### 4.5. S3 / MinIO

```python
@pytest_asyncio.fixture
async def s3_test_bucket(s3_session, s3_client_kwargs):
    """Создаёт уникальный тестовый бакет, удаляет после теста."""
    bucket_name = f"test-{uuid.uuid4().hex[:12]}"
    async with s3_session.create_client("s3", **s3_client_kwargs) as client:
        await client.create_bucket(Bucket=bucket_name)
    yield bucket_name
    # cleanup: удалить все объекты + бакет
```

### 4.6. SMTP / MailHog

```python
@pytest.fixture(scope="session")
def smtp_host(app_settings):
    return app_settings.smtp.host

@pytest.fixture(scope="session")
def smtp_port(app_settings):
    return app_settings.smtp.port
```

### 4.7. Auth Adapters

```python
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
```

### Scope фикстур — сводная таблица

| Фикстура | Scope | Почему |
|---|---|---|
| `app_settings` | session | Конфиг не меняется |
| `db_engine` | session | Один engine на прогон, DDL при старте |
| `db_session_factory` | session | Привязана к engine |
| `db_session` | **function** | Rollback — изоляция между тестами |
| `redis_client` | session | Один клиент, flushdb при teardown |
| `clean_redis` | **function** | Очистка перед каждым тестом |
| `kafka_producer` | session | Start/stop — дорого |
| `s3_test_bucket` | **function** | Уникальный бакет на тест |
| `password_adapter`, `jwt_adapter` | session | Stateless, дорогая инициализация |

---

## 5. BC conftest: фикстуры и seed-хелперы

Каждый BC имеет свой `conftest.py` в `tests/integration/<bc_name>/`. Содержит три группы фикстур: **mappers**, **repositories**, **seed-хелперы**.

### 5.1. Mappers

```python
@pytest.fixture
def user_mapper() -> UserMapper:
    return UserMapper()

@pytest.fixture
def session_mapper() -> SessionMapper:
    return SessionMapper()

@pytest.fixture
def role_mapper() -> RoleMapper:
    return RoleMapper()
```

Mappers — stateless объекты, scope по умолчанию (`function`) достаточен.

### 5.2. Repositories

```python
@pytest.fixture
def user_repo(db_session: AsyncSession, user_mapper: UserMapper) -> SqlUserRepository:
    return SqlUserRepository(session=db_session, mapper=user_mapper)

@pytest.fixture
def role_repo(db_session: AsyncSession, role_mapper: RoleMapper) -> SqlRoleRepository:
    return SqlRoleRepository(session=db_session, mapper=role_mapper)
```

Repository привязан к `db_session` — автоматически получает rollback-изоляцию.

### 5.3. Seed-хелперы

Seed-хелперы — это фикстуры-фабрики, возвращающие `async`-функции для создания доменных объектов в БД.

#### `_ensure_user` — гарантирует наличие User

```python
@pytest.fixture
def _ensure_user(user_repo: SqlUserRepository):
    """Хелпер: гарантирует наличие User в БД для FK-зависимостей."""
    _created: set[Id] = set()

    async def _fn(user_id: Id | None = None) -> User:
        uid = user_id or Id.generate()
        found = await user_repo.get_by_id(uid)
        if found is not None:
            _created.add(uid)
            return found
        email_vo = Email(f"auto-{uuid.uuid4().hex[:8]}@test.com")
        user = User(id=uid, email=email_vo)
        user.clear_domain_events()
        await user_repo.add(user)
        _created.add(uid)
        return user

    return _fn
```

**Назначение**: другие seed-хелперы (`make_user_auth`, `make_session`) зависят от `User` через FK. `_ensure_user` создаёт минимального User, если его ещё нет.

#### `make_user` — полноценный User

```python
@pytest.fixture
def make_user(user_repo: SqlUserRepository, _ensure_user):
    """Фабрика: создаёт User и сохраняет в БД."""

    async def _make(
        email: str | None = None,
        auth_provider: AuthProvider = AuthProvider.EMAIL_PASSWORD,
    ) -> User:
        email_vo = Email(email or f"user-{uuid.uuid4().hex[:8]}@test.com")
        user = User.register(email=email_vo, auth_provider=auth_provider)
        user.clear_domain_events()
        await user_repo.add(user)
        return user

    return _make
```

#### `make_role` — Role с идемпотентностью

```python
@pytest.fixture
def make_role(role_repo: SqlRoleRepository):
    """Фабрика: создаёт Role. Возвращает существующую по имени, если есть."""

    async def _make(
        name: str | None = None,
        permissions: list[str] | None = None,
        is_system: bool = False,
    ) -> Role:
        role_name = name or f"role-{uuid.uuid4().hex[:6]}"
        existing = await role_repo.get_by_name(role_name)
        if existing is not None:
            return existing
        role = Role(name=role_name, permissions=permissions or [], is_system=is_system)
        await role_repo.add(role)
        return role

    return _make
```

**Важно**: `make_role` проверяет `get_by_name` перед созданием — защита от `UniqueViolationError` при seeded system roles.

#### `make_user_auth` — UserAuth с FK-зависимостью

```python
@pytest.fixture
def make_user_auth(user_auth_repo: SqlUserAuthRepository, _ensure_user):
    """Фабрика: создаёт UserAuth и сохраняет в БД."""

    async def _make(
        user_id: Id | None = None,
        email: str | None = None,
        password_hash: str = "hashed-password",
    ) -> UserAuth:
        uid = user_id or Id.generate()
        await _ensure_user(uid)  # ← гарантирует FK
        email_vo = Email(email or f"auth-{uuid.uuid4().hex[:8]}@test.com")
        user_auth = UserAuth.create_for_email_auth(
            user_id=uid, email=email_vo, password_hash=PasswordHash(value=password_hash),
        )
        await user_auth_repo.add(user_auth)
        return user_auth

    return _make
```

#### `make_session` — Session

```python
@pytest.fixture
def make_session(session_repo: SqlSessionRepository, _ensure_user):
    """Фабрика: создаёт Session и сохраняет в БД."""

    async def _make(user_id: Id | None = None) -> Session:
        uid = user_id or Id.generate()
        await _ensure_user(uid)
        session = Session.create(
            user_id=uid,
            device_info=DeviceInfo(user_agent="TestBrowser/1.0"),
            ip_address=IpAddress("10.0.0.1"),
        )
        session.clear_domain_events()
        await session_repo.add(session)
        return session

    return _make
```

### Шаблон seed-хелпера

```python
@pytest.fixture
def make_<entity>(<repo>: Sql<Entity>Repository, _ensure_user):
    """Фабрика: создаёт <Entity> и сохраняет в БД."""

    async def _make(
        <param>: <Type> | None = None,
    ) -> <Entity>:
        # 1. Гарантируем FK-зависимости
        await _ensure_user(...)

        # 2. Создаём через доменный фабричный метод
        entity = <Entity>.create(...)
        entity.clear_domain_events()

        # 3. Сохраняем
        await <repo>.add(entity)
        return entity

    return _make
```

**Правила seed-хелперов:**
- Всегда `clear_domain_events()` — тест не должен видеть события от setup.
- Используют `_ensure_user` для FK-зависимостей.
- Генерируют уникальные данные через `uuid.uuid4().hex[:8]`.
- Возвращают **доменный объект**, не ORM-модель.

---

## 6. Тестирование Repositories

Repository-тесты проверяют, что SQL-реализация корректно сохраняет, читает и обновляет доменные объекты через mapper.

### Организация: один класс — одна группа операций

```python
"""Интеграционные тесты Sql<Aggregate>Repository (реальная PostgreSQL)."""

import pytest

from app.context.<bc>.domain.aggregates.<aggregate> import MyAggregate
from app.context.<bc>.infrastructure.persistence.repositories.sql_<aggregate>_repository import (
    Sql<Aggregate>Repository,
)


@pytest.mark.integration
class TestSql<Aggregate>RepositoryAdd:
    """Тесты добавления."""

    async def test_add_and_get_by_id(self, <repo>, make_<entity>) -> None:
        entity = await make_<entity>()
        found = await <repo>.get_by_id(entity.id)
        assert found is not None
        assert found.id == entity.id

    async def test_add_persists_attributes(self, <repo>, make_<entity>) -> None:
        entity = await make_<entity>()
        found = await <repo>.get_by_id(entity.id)
        assert found.status == <ExpectedStatus>


@pytest.mark.integration
class TestSql<Aggregate>RepositorySearch:
    """Тесты поиска."""

    async def test_get_by_email_found(self, <repo>, make_<entity>) -> None:
        entity = await make_<entity>(email="findme@test.com")
        found = await <repo>.get_by_email(Email("findme@test.com"))
        assert found is not None
        assert found.id == entity.id

    async def test_get_by_email_not_found(self, <repo>) -> None:
        found = await <repo>.get_by_email(Email("nobody@test.com"))
        assert found is None


@pytest.mark.integration
class TestSql<Aggregate>RepositoryUpdate:
    """Тесты обновления."""

    async def test_update_status(self, <repo>, make_<entity>) -> None:
        entity = await make_<entity>()
        entity.do_something()
        entity.clear_domain_events()
        await <repo>.update(entity)

        found = await <repo>.get_by_id(entity.id)
        assert found.<field> == <expected>


@pytest.mark.integration
class TestSql<Aggregate>RepositoryDelete:
    """Тесты удаления."""

    async def test_delete(self, <repo>, make_<entity>) -> None:
        entity = await make_<entity>()
        await <repo>.delete(entity.id)
        found = await <repo>.get_by_id(entity.id)
        assert found is None
```

### Что тестировать в Repository

| Аспект | Пример |
|---|---|
| **Add + Get** | `add()` → `get_by_id()` — round-trip |
| **Атрибуты** | Все поля сохраняются: status, email, created_at |
| **Поиск** | `get_by_email()`, `get_by_role()`, `search()` |
| **Not found** | Возвращает `None` для несуществующего ID/email |
| **Пагинация** | `get_paginated()` → проверка `len(items)` и `total` |
| **Update** | Изменение поля → `update()` → `get_by_id()` → проверка |
| **Дочерние коллекции** | `auth_factors`, `oauth_links`, `trusted_devices`, `backup_codes` — сохраняются при `update()` |
| **Delete** | `delete()` → `get_by_id()` → `None` |
| **Role sync** | `assign_role()` → `update()` → `get_by_id()` → проверка `role_ids` |

### Реальный пример: дочерние коллекции

```python
@pytest.mark.integration
class TestSqlUserAuthRepositoryUpdate:
    async def test_update_with_auth_factor(self, user_auth_repo, make_user_auth) -> None:
        auth = await make_user_auth()
        secret = TwoFASecret(value="JBSWY3DPEHPK3PXP", method=TwoFactorMethod.TOTP)
        auth.enable_auth_factor(method=TwoFactorMethod.TOTP, secret=secret, is_primary=True)
        auth.clear_domain_events()
        await user_auth_repo.update(auth)

        found = await user_auth_repo.get_by_id(auth.id)
        assert found is not None
        assert len(found.auth_factors) == 1
        assert found.auth_factors[0].method == TwoFactorMethod.TOTP
        assert found.auth_factors[0].is_primary is True

    async def test_update_with_trusted_device(self, user_auth_repo, make_user_auth) -> None:
        auth = await make_user_auth()
        auth.add_trusted_device("fp-123", DeviceInfo(user_agent="TrustedBrowser"), IpAddress("10.0.0.5"))
        auth.clear_domain_events()
        await user_auth_repo.update(auth)

        found = await user_auth_repo.get_by_id(auth.id)
        assert len(found.trusted_devices) == 1
        assert found.trusted_devices[0].device_fingerprint == "fp-123"
```

---

## 7. Тестирование Command Handlers

Command handler тесты — **full-stack**: реальные repos, реальные порты (Argon2, JWT, Kafka), реальная БД. Стабится только то, что не связано с тестируемой логикой (например, `PermissionCheckerPort`).

### Паттерн: сборка handler через внутренние фикстуры

```python
"""Интеграционные тесты <CommandName>Handler (реальные repos + реальные порты)."""

import pytest

from app.context.<bc>.application.commands.<command> import <Command>, <Handler>


@pytest.mark.integration
class Test<Handler>:
    """Тесты <описание> — full stack."""

    @pytest.fixture
    def event_bus(self, kafka_producer) -> BrokerDomainEventBus:
        broker = KafkaMessageBrokerAdapter(producer=kafka_producer, bootstrap_servers="")
        return BrokerDomainEventBus(broker=broker, topic="<bc>.events.test")

    @pytest.fixture
    def handler(
        self,
        <repo>: Sql<Aggregate>Repository,
        event_bus: BrokerDomainEventBus,
        # ... другие зависимости
    ) -> <Handler>:
        return <Handler>(
            <repo>=<repo>,
            event_bus=event_bus,
            # ...
        )

    async def test_<command>_success(self, handler, make_<entity>, <repo>) -> None:
        # Arrange: создаём данные через seed-хелперы
        entity = await make_<entity>()

        # Act
        cmd = <Command>(field="value")
        result = await handler.handle(cmd)

        # Assert: проверяем результат + состояние в БД
        assert result is not None
        updated = await <repo>.get_by_id(entity.id)
        assert updated.<field> == <expected>

    async def test_<command>_error_case(self, handler, ...) -> None:
        cmd = <Command>(field="invalid")
        with pytest.raises(<ExpectedException>):
            await handler.handle(cmd)
```

### Реальный пример: RegisterUserHandler

```python
@pytest.mark.integration
class TestRegisterUserHandler:
    @pytest.fixture
    def notification_adapter(self, smtp_host, smtp_port) -> IdentityNotificationPort:
        email_port = SmtpEmailAdapter(
            host=smtp_host, port=smtp_port, username=None, password=None, use_tls=False,
        )
        return IdentityNotificationAdapter(email_port=email_port, frontend_base_url="http://localhost:3000")

    @pytest.fixture
    def event_bus(self, kafka_producer) -> BrokerDomainEventBus:
        broker = KafkaMessageBrokerAdapter(producer=kafka_producer, bootstrap_servers="")
        return BrokerDomainEventBus(broker=broker, topic="identity.events.test")

    @pytest.fixture
    def handler(
        self, user_repo, user_auth_repo, role_repo,
        password_adapter, event_bus, notification_adapter,
    ) -> RegisterUserHandler:
        return RegisterUserHandler(
            user_repo=user_repo,
            user_auth_repo=user_auth_repo,
            role_repo=role_repo,
            password_port=password_adapter,
            event_bus=event_bus,
            notification_port=notification_adapter,
        )

    async def test_register_user_success(self, handler, user_repo, make_role) -> None:
        await make_role(name="user", is_system=True)

        cmd = RegisterUserCommand(
            email="newuser@test.com",
            password="StrongPass123!",
            auth_provider="email_password",
        )
        result = await handler.handle(cmd)
        assert result is not None

        user = await user_repo.get_by_email(Email("newuser@test.com"))
        assert user is not None
        assert user.status == AccountStatus.PENDING_VERIFICATION

    async def test_register_duplicate_email_raises(self, handler, make_role, make_user) -> None:
        await make_role(name="user", is_system=True)
        await make_user(email="duplicate@test.com")

        cmd = RegisterUserCommand(
            email="duplicate@test.com",
            password="StrongPass123!",
            auth_provider="email_password",
        )
        with pytest.raises(UserAlreadyExistsException):
            await handler.handle(cmd)
```

### Паттерн: стабирование PermissionCheckerPort

Для команд с RBAC-проверкой — авторизационный порт стабится:

```python
@pytest.fixture
def permission_checker(self) -> PermissionCheckerPort:
    """Стаб: всегда разрешает."""

    class _AlwaysAllow(PermissionCheckerPort):
        async def has_permission(self, user_id: Id, permission: str) -> bool:
            return True

        async def require_permission(self, user_id: Id, permission: str) -> None:
            pass

    return _AlwaysAllow()
```

**Почему стаб, а не реальный checker**: integration-тест проверяет бизнес-логику handler'а (назначение роли, сохранение), а не авторизацию. Авторизация тестируется отдельно.

---

## 8. Тестирование Query Handlers

Query handler тесты проверяют: данные создаются через seed-хелперы → query → handler возвращает корректный DTO.

### Шаблон

```python
"""Интеграционные тесты <QueryName>Handler (реальная PostgreSQL)."""

import pytest

from app.context.<bc>.application.queries.<query> import <Handler>, <Query>


@pytest.mark.integration
class Test<Handler>:
    """Тесты <описание>."""

    @pytest.fixture
    def handler(self, <repo>) -> <Handler>:
        return <Handler>(<repo>=<repo>)

    async def test_<query>_found(self, handler, make_<entity>) -> None:
        entity = await make_<entity>()
        query = <Query>(id=str(entity.id))
        dto = await handler.handle(query)
        assert dto.id == str(entity.id)

    async def test_<query>_not_found(self, handler) -> None:
        query = <Query>(id=str(Id.generate()))
        with pytest.raises(<NotFoundException>):
            await handler.handle(query)
```

### Реальный пример: GetActiveSessionsHandler

```python
@pytest.mark.integration
class TestGetActiveSessionsHandler:
    @pytest.fixture
    def handler(self, session_repo) -> GetActiveSessionsHandler:
        return GetActiveSessionsHandler(session_repo=session_repo)

    async def test_get_active_sessions(self, handler, make_session) -> None:
        user_id = Id.generate()
        await make_session(user_id=user_id)
        await make_session(user_id=user_id)

        query = GetActiveSessionsQuery(user_id=str(user_id))
        result = await handler.handle(query)
        assert result.total == 2
        assert len(result.items) == 2

    async def test_get_active_sessions_empty(self, handler) -> None:
        query = GetActiveSessionsQuery(user_id=str(Id.generate()))
        result = await handler.handle(query)
        assert result.total == 0
        assert result.items == []
```

### Что тестировать

| Аспект | Пример |
|---|---|
| **Успешный запрос** | Данные seed → query → DTO с правильными полями |
| **Пустой результат** | Нет данных → пустой список / total=0 |
| **Not found** | Несуществующий ID → `NotFoundException` |
| **Фильтры** | `system_only=True` → все элементы `is_system == True` |
| **Пагинация** | `offset/limit` → `len(items) <= limit` |
| **Связанные данные** | Profile с bio/job_title → DTO содержит эти поля |

---

## 9. Тестирование Event Handlers

Event handler тесты проверяют side-effect: получив доменное событие, handler создаёт/обновляет данные в БД.

### Шаблон

```python
"""Интеграционные тесты <EventHandler> (реальная PostgreSQL)."""

import pytest

from app.context.<bc>.application.event_handlers.<handler> import <EventHandler>
from app.context.<bc>.domain.events.<events> import <DomainEvent>


@pytest.mark.integration
class Test<EventHandler>:
    """Тесты <описание>."""

    @pytest.fixture
    def handler(self, <repo>) -> <EventHandler>:
        return <EventHandler>(<repo>=<repo>)

    async def test_creates_entity_from_event(self, handler, <repo>, _ensure_user) -> None:
        user_id_vo = Id.generate()
        await _ensure_user(user_id_vo)

        event = <DomainEvent>(
            user_id=str(user_id_vo),
            aggregate_id=Id.generate(),
            aggregate_type="<AggregateType>",
            # ... event-specific fields
        )
        await handler.handle(event)

        result = await <repo>.get_by_user_id(Id.from_string(str(user_id_vo)))
        assert result is not None

    async def test_idempotent(self, handler, make_<entity>, <repo>) -> None:
        existing = await make_<entity>()
        event = { ... }
        await handler.handle(event)  # повторный вызов — без ошибки
        # проверяем, что данные не дублируются
```

### Реальный пример: OnUserRegisteredCreateProfile

```python
@pytest.mark.integration
class TestOnUserRegisteredCreateProfile:
    @pytest.fixture
    def handler(self, profile_repo) -> OnUserRegisteredCreateProfile:
        return OnUserRegisteredCreateProfile(profile_repo=profile_repo)

    async def test_creates_profile(self, handler, profile_repo) -> None:
        user_id = Id.generate()
        event = {"event_type": "UserRegistered", "payload": {"user_id": str(user_id)}}
        await handler.handle(event)

        profile = await profile_repo.get_by_user_id(user_id)
        assert profile is not None
        assert profile.user_id == user_id

    async def test_idempotent_skips_if_exists(self, handler, make_profile, profile_repo) -> None:
        existing = await make_profile()
        event = {"event_type": "UserRegistered", "payload": {"user_id": str(existing.user_id)}}
        await handler.handle(event)

        found = await profile_repo.get_by_user_id(existing.user_id)
        assert found.id == existing.id  # тот же профиль

    async def test_ignores_non_target_event(self, handler, profile_repo) -> None:
        user_id = Id.generate()
        event = {"event_type": "UserLoggedIn", "payload": {"user_id": str(user_id)}}
        await handler.handle(event)

        assert await profile_repo.get_by_user_id(user_id) is None
```

### Что тестировать

| Аспект | Пример |
|---|---|
| **Создание side-effect** | Событие → объект появляется в БД |
| **Идемпотентность** | Повторный вызов → без ошибки, без дубликатов |
| **Фильтрация событий** | Чужой `event_type` → noop |
| **Невалидный payload** | Пустой `user_id` → без ошибки (graceful skip) |

---

## 10. Тестирование Adapters

Adapter-тесты проверяют инфраструктурные реализации портов.

### 10.1. TOTP Adapter (реальная библиотека)

```python
@pytest.mark.integration
class TestPyOTPTotpAdapter:
    @pytest.fixture
    def adapter(self) -> PyOTPTotpAdapter:
        return PyOTPTotpAdapter()

    def test_generate_secret(self, adapter) -> None:
        secret = adapter.generate_secret()
        assert isinstance(secret, str)
        assert len(secret) > 0

    def test_generate_secret_unique(self, adapter) -> None:
        assert adapter.generate_secret() != adapter.generate_secret()

    def test_verify_code_valid(self, adapter) -> None:
        secret = adapter.generate_secret()
        totp = pyotp.TOTP(secret)
        code = totp.now()
        assert adapter.verify_code(secret, code) is True

    def test_verify_code_invalid(self, adapter) -> None:
        secret = adapter.generate_secret()
        assert adapter.verify_code(secret, "000000") is False

    def test_get_provisioning_uri(self, adapter) -> None:
        secret = adapter.generate_secret()
        uri = adapter.get_provisioning_uri(secret, "user@example.com", "Julow")
        assert uri.startswith("otpauth://totp/")
```

**Заметка**: TOTP-тесты не требуют внешних сервисов — `pyotp` работает in-process. Но они интеграционные, потому что проверяют реальную библиотеку, а не мок.

### 10.2. OAuth Adapter (respx — мок HTTP)

```python
@pytest.mark.integration
class TestHttpxOAuthAdapter:
    @pytest.fixture
    def adapter(self) -> HttpxOAuthAdapter:
        return HttpxOAuthAdapter(
            client_id_map={"oauth_google": "id", "oauth_github": "id"},
            client_secret_map={"oauth_google": "secret", "oauth_github": "secret"},
        )

    @respx.mock
    async def test_exchange_code_google(self, adapter) -> None:
        respx.post("https://oauth2.googleapis.com/token").mock(
            return_value=Response(200, json={"access_token": "google-access-123"})
        )
        token = await adapter.exchange_code("oauth_google", "code", "http://localhost/callback")
        assert token == "google-access-123"

    @respx.mock
    async def test_get_user_info_google(self, adapter) -> None:
        respx.get("https://www.googleapis.com/oauth2/v3/userinfo").mock(
            return_value=Response(200, json={
                "sub": "google-user-id", "email": "user@gmail.com", "name": "User",
            })
        )
        info = await adapter.get_user_info("oauth_google", "access-token")
        assert info.provider_user_id == "google-user-id"
        assert info.email == "user@gmail.com"

    @respx.mock
    async def test_exchange_code_error(self, adapter) -> None:
        respx.post("https://oauth2.googleapis.com/token").mock(
            return_value=Response(200, json={"error": "invalid_grant"})
        )
        with pytest.raises(RuntimeError, match="access_token"):
            await adapter.exchange_code("oauth_google", "bad-code", "http://localhost/callback")
```

**`respx`** — мокает HTTP-запросы `httpx`. Декоратор `@respx.mock` активирует перехват. Позволяет тестировать парсинг ответов OAuth-провайдеров без реальных запросов.

### 10.3. SMTP / MailHog (реальная отправка)

```python
@pytest.mark.integration
class TestIdentityNotificationAdapter:
    @pytest.fixture
    def email_port(self, smtp_host, smtp_port) -> SmtpEmailAdapter:
        return SmtpEmailAdapter(host=smtp_host, port=smtp_port, username=None, password=None, use_tls=False)

    @pytest.fixture
    def adapter(self, email_port) -> IdentityNotificationAdapter:
        return IdentityNotificationAdapter(email_port=email_port, frontend_base_url="http://localhost:3000")

    @staticmethod
    async def _clear_mailhog() -> None:
        async with httpx.AsyncClient() as client:
            await client.delete("http://localhost:8025/api/v1/messages")

    @staticmethod
    async def _get_latest_message() -> dict | None:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:8025/api/v2/messages")
            items = resp.json().get("items", [])
            return items[0] if items else None

    async def test_send_email_verification(self, adapter) -> None:
        await self._clear_mailhog()
        await adapter.send_email_verification(email="new@example.com", user_id="user-123", token="token")

        msg = await self._get_latest_message()
        assert msg is not None
        assert "new@example.com" in msg["Content"]["Headers"]["To"][0]
        assert "Подтверждение" in self._decode_subject(msg)
```

**Паттерн**: очистка MailHog → отправка → проверка через MailHog API.

---

## 11. Cross-context тесты

Cross-context тесты проверяют **outboard providers** и **inbound adapters** — взаимодействие между Bounded Contexts через порты.

### Структура conftest

`tests/integration/cross_context/conftest.py` содержит фикстуры из **обоих** BC:

```python
"""
Cross-context conftest — фикстуры из Identity и Profile BC.

Cross-context тесты требуют доступа к репозиториям и seed-хелперам
обоих BC. Фикстуры дублируют те, что определены в identity/ и profile/
conftest-ах, чтобы не нарушать иерархию pytest conftest.
"""

# ── Identity Mappers & Repos ────────────────────────────────────────────
@pytest.fixture
def user_mapper() -> UserMapper: ...

@pytest.fixture
def user_repo(db_session, user_mapper) -> SqlUserRepository: ...

# ── Profile Mapper & Repo ───────────────────────────────────────────────
@pytest.fixture
def profile_mapper() -> UserProfileMapper: ...

@pytest.fixture
def profile_repo(db_session, profile_mapper) -> SqlUserProfileRepository: ...

# ── Identity Seed Helpers ───────────────────────────────────────────────
@pytest.fixture
def make_user(user_repo, _ensure_user): ...

@pytest.fixture
def make_role(role_repo): ...

# ── Profile Seed Helpers ────────────────────────────────────────────────
@pytest.fixture
def make_profile(profile_repo): ...
```

**Почему дублирование**: pytest conftest иерархия не позволяет `cross_context/conftest.py` импортировать фикстуры из `identity/conftest.py` — они в разных поддеревьях. Поэтому фикстуры дублируются.

### Шаблон: outbound provider

```python
@pytest.mark.integration
class TestRoleProviderAdapter:
    @pytest.fixture
    def adapter(self, role_repo, user_repo) -> RoleProviderAdapter:
        return RoleProviderAdapter(role_repo=role_repo, user_repo=user_repo)

    async def test_get_role_returns_dto(self, adapter, make_role) -> None:
        role = await make_role(name="moderator", permissions=["ban", "mute"])
        dto = await adapter.get_role(str(role.id))
        assert isinstance(dto, RoleDTO)
        assert dto.name == "moderator"
        assert dto.permissions == ["ban", "mute"]

    async def test_get_role_returns_none_for_unknown(self, adapter) -> None:
        assert await adapter.get_role(str(Id.generate())) is None
```

### Шаблон: inbound adapter

```python
@pytest.mark.integration
class TestIdentityUserAdapter:
    @pytest.fixture
    def adapter(self, user_repo) -> IdentityUserAdapter:
        provider = UserProviderAdapter(user_repo=user_repo)
        return IdentityUserAdapter(identity_user_provider=provider)

    async def test_get_user_returns_dict(self, adapter, make_user) -> None:
        user = await make_user(email="ident@test.com")
        result = await adapter.get_user(str(user.id))
        assert result is not None
        assert result["id"] == str(user.id)
        assert result["email"] == "ident@test.com"

    async def test_user_exists_true(self, adapter, make_user) -> None:
        user = await make_user()
        assert await adapter.user_exists(str(user.id)) is True

    async def test_user_exists_false(self, adapter) -> None:
        assert await adapter.user_exists(str(Id.generate())) is False
```

---

## 12. Конвенции и антипаттерны

### Именование

| Элемент | Конвенция | Пример |
|---|---|---|
| **Файл** | `test_<component>.py` | `test_sql_user_repository.py`, `test_register_user.py` |
| **Класс** | `Test<Component>` или `Test<Component><Group>` | `TestSqlUserRepositoryAdd`, `TestLoginUserHandler` |
| **Метод** | `test_<action>` или `test_<action>_<outcome>` | `test_add_and_get_by_id`, `test_login_wrong_password` |
| **Фикстура handler** | `handler` (внутри класса) | `def handler(self, repo, ...)` |
| **Seed-хелпер** | `make_<entity>` | `make_user`, `make_role`, `make_session` |
| **FK-хелпер** | `_ensure_<entity>` | `_ensure_user` |

### Docstring файла

```python
"""Интеграционные тесты Sql<Aggregate>Repository (реальная PostgreSQL)."""
```

```python
"""Интеграционные тесты <Handler> (реальные repos + реальные порты)."""
```

### Seed-хелперы vs inline создание

| ✅ Seed-хелпер | ❌ Inline |
|---|---|
| `user = await make_user()` | `user = User.register(...); await repo.add(user)` |
| Переиспользуемый, FK-безопасный | Дублирование, можно забыть `_ensure_user` |

Inline допустим только если нужен **нестандартный** setup, которого нет в seed-хелпере.

### `clear_domain_events()` в seed-хелперах

Всегда вызывается **в seed-хелпере**, не в тесте:

```python
# ✅ В seed-хелпере
user = User.register(...)
user.clear_domain_events()  # ← здесь
await user_repo.add(user)

# ❌ В тесте
user = await make_user()
user.clear_domain_events()  # ← поздно, seed-хелпер уже должен был очистить
```

### Rollback-изоляция

- `db_session` откатывается после каждого теста — данные не утекают.
- **Не** делайте `await session.commit()` в тестах — это сломает изоляцию.
- Repository'и внутри используют `session.flush()` — данные видны в рамках сессии, но не коммитятся.

### Фикстуры handler — внутри класса

Handler-фикстуры определяются **внутри тест-класса**, а не в conftest:

```python
@pytest.mark.integration
class TestLoginUserHandler:
    @pytest.fixture
    def event_bus(self, kafka_producer) -> BrokerDomainEventBus:
        ...

    @pytest.fixture
    def handler(self, user_repo, event_bus, ...) -> LoginUserHandler:
        return LoginUserHandler(...)
```

**Почему**: handler-фикстуры специфичны для конкретного handler'а. В conftest попадают только переиспользуемые вещи (repos, seed-хелперы).

### Антипаттерны

| ❌ Не делать | ✅ Делать |
|---|---|
| `session.commit()` в тесте | Полагаться на rollback в `db_session` фикстуре |
| Raw SQL для setup данных | Seed-хелперы (`make_user`, `make_role`) |
| Один огромный тест на весь handler | Отдельные тесты: success, error case, edge case |
| Мокать repository в integration-тесте | Использовать реальный SQL-repository |
| scope="session" для `db_session` | scope="function" (иначе данные утекают) |
| Хардкодить email/имена | `uuid.uuid4().hex[:8]` для уникальности |
| Забыть `@pytest.mark.integration` | Тест будет пропущен autouse-фикстурой |
| Пропускать `_ensure_user` в seed-хелперах | FK constraint violation в рантайме |

### Типизация

Все тестовые методы аннотируются `-> None`:

```python
async def test_register_user_success(self, handler: RegisterUserHandler, user_repo) -> None:
    ...
```

---

## 13. Чеклист нового BC

### Подготовка

- [ ] Создать `tests/integration/<bc_name>/` со структурой из раздела 2
- [ ] Добавить `__init__.py` в каждый подпакет (`repositories/`, `commands/`, `queries/`, `event_handlers/`, `adapters/`)
- [ ] Создать `tests/integration/<bc_name>/conftest.py`

### Conftest

- [ ] Mapper-фикстуры: `<entity>_mapper()` для каждого mapper'а
- [ ] Repository-фикстуры: `<entity>_repo(db_session, mapper)` для каждого repo
- [ ] `_ensure_user` — если BC зависит от User через FK
- [ ] Seed-хелперы: `make_<entity>()` для каждого агрегата
- [ ] Seed-хелперы вызывают `clear_domain_events()`
- [ ] Seed-хелперы генерируют уникальные данные (`uuid.uuid4().hex[:8]`)

### Repositories (`repositories/`)

- [ ] Один файл на repository: `test_sql_<aggregate>_repository.py`
- [ ] Тесты `add()` + `get_by_id()` — round-trip
- [ ] Тесты поиска: `get_by_email()`, `get_by_*()`, `search()`
- [ ] Тесты пагинации: `get_paginated()`, `get_all(offset, limit)`
- [ ] Тесты обновления: `update()` → `get_by_id()` → проверка
- [ ] Тесты дочерних коллекций (если есть): add, update, delete child entities
- [ ] Тесты удаления: `delete()` → `get_by_id()` → `None`
- [ ] Тесты not found: возврат `None` / пустой список

### Command Handlers (`commands/`)

- [ ] Один файл на command: `test_<command_name>.py`
- [ ] Фикстура `handler` внутри тест-класса
- [ ] Фикстура `event_bus` через `KafkaMessageBrokerAdapter` + `BrokerDomainEventBus`
- [ ] Стабирование `PermissionCheckerPort` (если есть RBAC)
- [ ] Тест success: seed → command → проверка результата + БД
- [ ] Тест error: дублирование, not found, бизнес-правила → `pytest.raises`

### Query Handlers (`queries/`)

- [ ] Один файл на query: `test_<query_name>.py`
- [ ] Фикстура `handler` внутри тест-класса (обычно только repo)
- [ ] Тест success: seed → query → проверка DTO
- [ ] Тест empty: query без данных → пустой результат
- [ ] Тест not found: несуществующий ID → exception
- [ ] Тесты фильтров и пагинации (если есть)

### Event Handlers (`event_handlers/`)

- [ ] Один файл на event handler: `test_on_<event>_<action>.py`
- [ ] Фикстура `handler` внутри тест-класса
- [ ] Тест creates entity: событие → side-effect в БД
- [ ] Тест идемпотентности: повторный вызов → без ошибки
- [ ] Тест фильтрации: чужой event_type → noop

### Adapters (`adapters/`)

- [ ] Один файл на adapter: `test_<adapter_name>.py`
- [ ] TOTP: generate, verify valid/invalid, provisioning URI
- [ ] OAuth: exchange code, get user info, error cases (через `respx`)
- [ ] SMTP: send → проверка через MailHog API
- [ ] S3: upload, download, delete (через реальный MinIO)

### Cross-context (`cross_context/`)

- [ ] Создать `tests/integration/cross_context/conftest.py` (если ещё нет)
- [ ] Добавить mapper/repo/seed-хелпер фикстуры для нового BC
- [ ] Тест outbound provider: `get_<entity>()` → DTO
- [ ] Тест inbound adapter: adapter → dict/DTO
- [ ] Тесты not found / empty cases

### Проверки

- [ ] Каждый тест-класс помечен `@pytest.mark.integration`
- [ ] Каждый тестовый метод — `async def` с аннотацией `-> None`
- [ ] Нет `session.commit()` в тестах
- [ ] Все seed-хелперы используют `_ensure_user` для FK
- [ ] `pytest -m integration` проходит без ошибок
