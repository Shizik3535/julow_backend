# Гайд: E2E-тестирование

## Содержание

1. [Обзор](#1-обзор)
2. [Структура директорий](#2-структура-директорий)
3. [Конфигурация pytest](#3-конфигурация-pytest)
4. [Conftest: App и Client](#4-conftest-app-и-client)
5. [Conftest: Helper-функции](#5-conftest-helper-функции)
6. [Conftest: Фикстуры](#6-conftest-фикстуры)
7. [Тесты Auth-эндпоинтов](#7-тесты-auth-эндпоинтов)
8. [Тесты Account-эндпоинтов](#8-тесты-account-эндпоинтов)
9. [Тесты Security-эндпоинтов](#9-тесты-security-эндпоинтов)
10. [Тесты Admin-эндпоинтов](#10-тесты-admin-эндпоинтов)
11. [Тесты Profile-эндпоинтов](#11-тесты-profile-эндпоинтов)
12. [Scenario-тесты](#12-scenario-тесты)
13. [Конвенции и антипаттерны](#13-конвенции-и-антипаттерны)
14. [Чеклист нового контроллера / BC](#14-чеклист-нового-контроллера--bc)

---

## 1. Обзор

E2E-тесты проверяют **полный стек приложения** через HTTP-запросы: от presentation-слоя (контроллеры, схемы, валидация) через application и domain до infrastructure (реальная PostgreSQL). Используется `httpx.AsyncClient` с `ASGITransport` — запросы отправляются напрямую в FastAPI без поднятия сервера.

### Отличие от unit и integration

| Уровень | Что тестируем | HTTP | Заглушки | Скорость |
|---|---|---|---|---|
| **Unit** | Domain-логика | Нет | Всё замокано | Миллисекунды |
| **Integration** | Repos, handlers, adapters | Нет | Только авторизация | Секунды |
| **E2E** | HTTP API (full stack) | Да | Kafka, OAuth | Секунды–минуты |

### Принципы

- **Чёрный ящик**: тесты работают только с HTTP-запросами и JSON-ответами. Нет прямого доступа к repos/handlers.
- **Реальная БД**: PostgreSQL с DDL + seed system roles.
- **In-memory заглушки**: Kafka заменяется на `InMemoryMessageBrokerAdapter`, OAuth — на `InMemoryOAuthAdapter`. Остальное — реальное.
- **Изоляция через уникальные данные**: каждый тест создаёт пользователя с уникальным email через `_unique_email()`.
- **Маркер `@pytest.mark.e2e`**: обязателен для каждого тест-класса.
- **Async**: все тесты — `async def`, работают через `pytest-asyncio`.

### Что тестируем

| Аспект | Пример |
|---|---|
| **HTTP-коды** | 200, 201, 401, 403, 404, 409, 422 |
| **Валидация** | Невалидный email → 422, короткий пароль → 422 |
| **Авторизация** | Без токена → 401, обычный user → 403 |
| **Бизнес-ошибки** | Дубликат email → 409, несуществующий user → 404 |
| **Success-кейсы** | Корректный запрос → правильная структура ответа |
| **Сценарии** | Многошаговые бизнес-флоу (register → login → refresh) |

---

## 2. Структура директорий

```
tests/e2e/
├── __init__.py
├── conftest.py                  # App, client, helpers, fixtures, marker
├── auth/                        # AuthController endpoints
│   ├── __init__.py
│   ├── test_register.py
│   ├── test_login.py
│   ├── test_refresh.py
│   ├── test_confirm_email.py
│   ├── test_password_reset_request.py
│   └── test_password_reset_confirm.py
├── account/                     # AccountController endpoints
│   ├── __init__.py
│   ├── test_get_me.py
│   ├── test_change_password.py
│   ├── test_get_sessions.py
│   ├── test_get_role.py
│   ├── test_get_roles.py
│   ├── test_terminate_session.py
│   ├── test_terminate_all_sessions.py
│   ├── test_disable_account.py
│   ├── test_reactivate_account.py
│   ├── test_request_deletion.py
│   └── test_cancel_deletion.py
├── security/                    # SecurityController endpoints
│   ├── __init__.py
│   ├── test_get_auth_status.py
│   ├── test_enable_auth_factor.py
│   ├── test_disable_auth_factor.py
│   ├── test_generate_backup_codes.py
│   ├── test_get_trusted_devices.py
│   ├── test_add_trusted_device.py
│   ├── test_remove_trusted_device.py
│   ├── test_link_oauth.py
│   ├── test_get_oauth_links.py
│   └── ...
├── admin/                       # AdminController endpoints
│   ├── __init__.py
│   ├── test_assign_role.py
│   ├── test_remove_role.py
│   └── test_unlock_account.py
├── profile/                     # ProfileController endpoints
│   ├── __init__.py
│   ├── test_get_profile.py
│   ├── test_update_appearance.py
│   ├── test_update_personal_info.py
│   ├── test_update_notifications.py
│   └── test_update_privacy.py
└── scenarios/                   # Многошаговые бизнес-сценарии
    ├── __init__.py
    ├── test_auth_flow.py
    ├── test_2fa_flow.py
    ├── test_oauth_flow.py
    ├── test_trusted_devices_flow.py
    ├── test_backup_codes_flow.py
    ├── test_profile_settings_flow.py
    ├── test_account_deletion_flow.py
    └── test_account_disable_flow.py
```

### Принцип группировки

| Директория | Что содержит | Соответствие |
|---|---|---|
| `auth/` | Регистрация, логин, refresh, confirm-email, password-reset | `AuthController` |
| `account/` | Управление аккаунтом текущего пользователя | `AccountController` |
| `security/` | 2FA, backup codes, trusted devices, OAuth | `SecurityController` |
| `admin/` | Административные операции (assign role, unlock) | `AdminController` |
| `profile/` | Профиль пользователя (get, update настроек) | `ProfileController` |
| `scenarios/` | Многошаговые бизнес-флоу через несколько endpoint'ов | Не привязан к одному контроллеру |

### Правило именования файлов

| Категория | Имя файла | Пример |
|---|---|---|
| Endpoint-тест | `test_<action>.py` | `test_register.py`, `test_get_me.py` |
| Scenario-тест | `test_<name>_flow.py` | `test_auth_flow.py`, `test_2fa_flow.py` |

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
pytest -m e2e                              # все E2E-тесты
pytest tests/e2e                           # по директории
pytest tests/e2e/auth                      # один контроллер
pytest tests/e2e/scenarios                 # только сценарии
pytest tests/e2e/auth/test_register.py     # один файл
```

### Autouse marker (`tests/e2e/conftest.py`)

```python
@pytest.fixture(autouse=True)
def _e2e_marker(request):
    """Проверяет, что тест помечен как e2e."""
    if not request.node.get_closest_marker("e2e"):
        pytest.skip("Test not marked as e2e")
```

**Важно**: если забыть `@pytest.mark.e2e`, тест будет пропущен.

---

## 4. Conftest: App и Client

Файл `tests/e2e/conftest.py` — единственный conftest для E2E-тестов (нет BC-level conftest'ов).

### 4.1. In-memory заглушки

#### InMemoryMessageBrokerAdapter (заменяет Kafka)

```python
class InMemoryMessageBrokerAdapter(MessageBrokerPort):
    """Заглушка брокера — не требует Kafka."""

    def __init__(self) -> None:
        self.published: list[dict[str, Any]] = []
        self._handlers: dict[str, MessageHandler] = {}

    async def publish(self, topic: str, message: dict[str, Any], key: str | None = None) -> None:
        self.published.append({"topic": topic, "message": message, "key": key})
        handler = self._handlers.get(topic)
        if handler is not None:
            await handler(topic, message)

    async def subscribe(self, topic: str, group_id: str, handler: MessageHandler) -> None:
        self._handlers[topic] = handler

    async def start(self) -> None:
        pass

    async def stop(self) -> None:
        pass
```

**Назначение**: Kafka не требуется для E2E-тестов. Брокер сохраняет сообщения в `self.published` и немедленно вызывает подписчиков — event handlers срабатывают **синхронно** внутри теста.

#### InMemoryOAuthAdapter (заменяет Google/GitHub)

```python
class InMemoryOAuthAdapter(OAuthPort):
    """Заглушка OAuth — не делает реальных HTTP-запросов."""

    async def exchange_code(self, provider: str, code: str, redirect_uri: str) -> str:
        return f"mock-access-token-{provider}"

    async def get_user_info(self, provider: str, access_token: str) -> OAuthUserInfo:
        return OAuthUserInfo(
            provider_user_id=f"mock-user-id-{provider}",
            email=f"mock@{provider}.example.com",
            display_name=f"Mock User ({provider})",
        )
```

**Назначение**: OAuth-тесты проверяют контроллер и handler, а не реальный Google/GitHub API.

### 4.2. App-фикстура

```python
@pytest.fixture(scope="session")
def app():
    """Создаёт FastAPI приложение для e2e-тестов."""
    application = create_app()
    container = application.state.container
    container.message_broker_port.override(InMemoryMessageBrokerAdapter())
    container.oauth_port.override(InMemoryOAuthAdapter())
    return application
```

**Ключевые моменты:**
- **scope="session"** — приложение создаётся один раз.
- **DI override** — подменяет `message_broker_port` и `oauth_port` через DI-контейнер.
- Всё остальное (DB, Auth, Repos) — реальное.

### 4.3. DB Tables + Seed

```python
@pytest_asyncio.fixture(scope="session")
async def _db_tables(app):
    """Создаёт таблицы в тестовой БД, удаляет после."""
    # 1. Создать тестовую БД если не существует
    db = settings.db
    conn = await asyncpg.connect(host=db.host, ...)
    if not exists:
        await conn.execute(f'CREATE DATABASE "{db.name}"')

    # 2. DDL: create_all
    engine = app.state.container.db_engine()
    async with engine.begin() as conn:
        await conn.run_sync(BaseORMModel.metadata.create_all)

    # 3. Seed system roles (ON CONFLICT DO NOTHING)
    async with engine.begin() as _conn:
        for _role in SYSTEM_ROLES:
            await _conn.execute(text("INSERT INTO roles ... ON CONFLICT (name) DO NOTHING"), {...})

    # 4. Wire messaging (ASGITransport не вызывает lifespan)
    broker = app.state.container.message_broker_port()
    await broker.start()
    await wire_messaging(app.state.container)

    yield

    await broker.stop()
    async with engine.begin() as conn:
        await conn.run_sync(BaseORMModel.metadata.drop_all)
```

**Важно**: `httpx.ASGITransport` **не вызывает ASGI lifespan** — `startup`/`shutdown` события не выполняются. Поэтому `wire_messaging()` вызывается вручную, иначе event handlers не будут зарегистрированы.

### 4.4. HTTP Client

```python
API = "/api/v1"

@pytest_asyncio.fixture
async def client(app, _db_tables) -> AsyncGenerator[AsyncClient, Any]:
    """Async HTTP-клиент для тестирования."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
```

- **scope="function"** (по умолчанию) — новый клиент на каждый тест.
- Зависит от `_db_tables` — гарантирует наличие таблиц и seed'а.
- `base_url="http://test"` — условный URL, запросы не выходят из процесса.
- Константа `API = "/api/v1"` — используется во всех тестах для формирования URL.

---

## 5. Conftest: Helper-функции

Helper-функции — обычные `async def` (не фикстуры), импортируемые в тестах через `from tests.e2e.conftest import ...`.

### 5.1. `register_user()` — регистрация

```python
DEFAULT_PASSWORD = "StrongP@ss1"

async def register_user(
    client: AsyncClient,
    *,
    email: str | None = None,
    password: str = DEFAULT_PASSWORD,
) -> dict:
    """
    Регистрирует нового пользователя.

    Возвращает:
        {"email": ..., "password": ..., "user_id": ..., "response": ...}
    """
    email = email or _unique_email()
    resp = await client.post(f"{API}/auth/register", json={"email": email, "password": password})
    data = resp.json()
    user_id = data.get("data", {}).get("id", "")
    return {"email": email, "password": password, "user_id": user_id, "response": resp}
```

### 5.2. `login_user()` — логин

```python
async def login_user(
    client: AsyncClient,
    *,
    email: str,
    password: str = DEFAULT_PASSWORD,
) -> dict:
    """
    Логинит пользователя.

    Возвращает:
        {"access_token": ..., "refresh_token": ..., "user": ..., "response": ...}
    """
    resp = await client.post(f"{API}/auth/login", json={"email": email, "password": password})
    data = resp.json().get("data", {})
    return {
        "access_token": data.get("access_token", ""),
        "refresh_token": data.get("refresh_token", ""),
        "user": data.get("user", {}),
        "response": resp,
    }
```

### 5.3. `register_and_login()` — регистрация + логин

```python
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
```

### 5.4. `register_admin_and_login()` — admin setup

```python
async def register_admin_and_login(
    client: AsyncClient,
    *,
    email: str | None = None,
    password: str = DEFAULT_PASSWORD,
) -> dict:
    """
    Регистрирует пользователя, назначает роль admin через прямой SQL,
    и логинит. Используется для тестов admin-эндпоинтов.
    """
    reg = await register_user(client, email=email, password=password)
    user_id = reg["user_id"]

    # Назначаем роль admin через прямой SQL (обход RBAC для тестового сетапа)
    engine = create_async_engine(settings.db.url)
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
        "email": reg["email"], "password": password, "user_id": user_id,
        "access_token": log["access_token"], "refresh_token": log["refresh_token"],
    }
```

**Почему прямой SQL**: в E2E нет доступа к repos. Для тестового admin-setup допускается обход RBAC через SQL.

### 5.5. `auth_headers()` — заголовки авторизации

```python
def auth_headers(token: str) -> dict[str, str]:
    """Возвращает заголовки авторизации."""
    return {"Authorization": f"Bearer {token}"}
```

### 5.6. `_unique_email()` — уникальный email

```python
def _unique_email() -> str:
    return f"e2e-{uuid.uuid4().hex[:12]}@example.com"
```

### Таблица helpers

| Функция | Когда использовать |
|---|---|
| `register_user()` | Нужен только зарегистрированный пользователь (без токенов) |
| `login_user()` | Уже есть email, нужны токены |
| `register_and_login()` | Нужен полный пользователь с токенами |
| `register_admin_and_login()` | Тесты admin-эндпоинтов (assign role, unlock) |
| `auth_headers()` | Формирование `Authorization: Bearer <token>` |

---

## 6. Conftest: Фикстуры

### `registered_user` — готовый пользователь

```python
@pytest_asyncio.fixture
async def registered_user(client) -> dict:
    """
    Зарегистрированный и залогиненный пользователь.

    Возвращает:
        {"email", "password", "user_id", "access_token", "refresh_token"}
    """
    return await register_and_login(client)
```

### `auth_client` — авторизованный клиент

```python
@pytest_asyncio.fixture
async def auth_client(client, registered_user) -> AsyncClient:
    """
    Авторизованный HTTP-клиент.
    Устанавливает заголовок Authorization с JWT access-токеном.
    """
    client.headers["Authorization"] = f"Bearer {registered_user['access_token']}"
    return client
```

### Когда что использовать

| Фикстура | Когда |
|---|---|
| `client` | Публичные эндпоинты или тесты 401 |
| `auth_client` | Защищённые эндпоинты — простой read/update для текущего пользователя |
| `registered_user` + `auth_headers()` | Нужен доступ к данным пользователя (email, user_id) + ручное управление заголовками |
| `register_and_login()` + `auth_headers()` | Нужно несколько пользователей в одном тесте |
| `register_admin_and_login()` + `auth_headers()` | Admin-эндпоинты |

---

## 7. Тесты Auth-эндпоинтов

Тесты в `tests/e2e/auth/` покрывают `AuthController`:

| Endpoint | Файл | Методы |
|---|---|---|
| `POST /auth/register` | `test_register.py` | success, duplicate_email, invalid_email, short_password, missing_fields |
| `POST /auth/login` | `test_login.py` | success, wrong_password, nonexistent_user, remember_me |
| `POST /auth/refresh` | `test_refresh.py` | success, invalid_token |
| `POST /auth/confirm-email` | `test_confirm_email.py` | success, invalid_token, no_auth |
| `POST /auth/password-reset/request` | `test_password_reset_request.py` | success, nonexistent_email |
| `POST /auth/password-reset/confirm` | `test_password_reset_confirm.py` | success, invalid_token |

### Шаблон: публичный endpoint

```python
"""E2E-тесты: POST /auth/register."""

import pytest

from tests.e2e.conftest import API, register_user


@pytest.mark.e2e
class TestRegister:
    """Регистрация нового пользователя."""

    async def test_register_success(self, client) -> None:
        """201 — успешная регистрация."""
        result = await register_user(client)
        resp = result["response"]

        assert resp.status_code == 201
        body = resp.json()
        assert body["data"]["id"]
        assert body["data"]["email"] == result["email"]

    async def test_register_duplicate_email(self, client) -> None:
        """409 — повторная регистрация с тем же email."""
        result = await register_user(client)
        assert result["response"].status_code == 201

        duplicate = await register_user(client, email=result["email"])
        assert duplicate["response"].status_code == 409

    async def test_register_invalid_email(self, client) -> None:
        """422 — невалидный email."""
        resp = await client.post(
            f"{API}/auth/register",
            json={"email": "not-an-email", "password": "StrongP@ss1"},
        )
        assert resp.status_code == 422

    async def test_register_short_password(self, client) -> None:
        """422 — пароль менее 8 символов."""
        resp = await client.post(
            f"{API}/auth/register",
            json={"email": "short@example.com", "password": "123"},
        )
        assert resp.status_code == 422

    async def test_register_missing_fields(self, client) -> None:
        """422 — отсутствуют обязательные поля."""
        resp = await client.post(f"{API}/auth/register", json={})
        assert resp.status_code == 422
```

### Что тестировать

| Аспект | HTTP-код | Пример |
|---|---|---|
| **Success** | 200 / 201 | Корректные данные → `data` в ответе |
| **Валидация** | 422 | Невалидный email, короткий пароль, пустой body |
| **Бизнес-конфликт** | 409 | Дубликат email |
| **Неверные credentials** | 401 | Неправильный пароль, несуществующий пользователь |
| **Response body** | — | `data.id`, `data.email`, `data.access_token` |

---

## 8. Тесты Account-эндпоинтов

Тесты в `tests/e2e/account/` покрывают `AccountController`:

| Endpoint | Файл | Ключевые кейсы |
|---|---|---|
| `GET /account/me` | `test_get_me.py` | success (auth_client), no_auth (401) |
| `POST /account/me/change-password` | `test_change_password.py` | success, wrong_current, no_auth, short_new |
| `GET /account/sessions` | `test_get_sessions.py` | success, no_auth |
| `GET /account/roles` | `test_get_roles.py` | success, no_auth |
| `GET /account/roles/{id}` | `test_get_role.py` | success, not_found, no_auth |
| `POST /account/me/disable` | `test_disable_account.py` | success, no_auth |
| `POST /account/me/reactivate` | `test_reactivate_account.py` | success, conflict (409) |
| `POST /account/me/request-deletion` | `test_request_deletion.py` | success, no_auth |
| `POST /account/me/cancel-deletion` | `test_cancel_deletion.py` | success, conflict (409), no_auth |
| `DELETE /account/sessions/{id}` | `test_terminate_session.py` | success, no_auth |
| `DELETE /account/sessions` | `test_terminate_all_sessions.py` | success, no_auth |

### Шаблон: защищённый endpoint с `auth_client`

```python
"""E2E-тесты: GET /account/me."""

import pytest

from tests.e2e.conftest import API


@pytest.mark.e2e
class TestGetMe:
    """Получение текущего пользователя."""

    async def test_get_me_success(self, auth_client, registered_user) -> None:
        """200 — возвращает данные текущего пользователя."""
        resp = await auth_client.get(f"{API}/account/me")

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["email"] == registered_user["email"]
        assert data["id"] == registered_user["user_id"]

    async def test_get_me_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.get(f"{API}/account/me")
        assert resp.status_code == 401
```

### Шаблон: endpoint с ручным setup

```python
"""E2E-тесты: POST /account/me/change-password."""

import pytest

from tests.e2e.conftest import API, DEFAULT_PASSWORD, auth_headers, register_and_login


@pytest.mark.e2e
class TestChangePassword:
    """Смена пароля."""

    async def test_change_password_success(self, client) -> None:
        """200 — успешная смена пароля."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/account/me/change-password",
            json={
                "current_password": DEFAULT_PASSWORD,
                "new_password": "NewStr0ngP@ss!",
            },
            headers=auth_headers(user["access_token"]),
        )
        assert resp.status_code == 200

    async def test_change_password_wrong_current(self, client) -> None:
        """401 — неверный текущий пароль."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/account/me/change-password",
            json={
                "current_password": "WrongP@ssword1",
                "new_password": "NewStr0ngP@ss!",
            },
            headers=auth_headers(user["access_token"]),
        )
        assert resp.status_code == 401
```

---

## 9. Тесты Security-эндпоинтов

Тесты в `tests/e2e/security/` покрывают `SecurityController`:

| Endpoint | Файл | Ключевые кейсы |
|---|---|---|
| `GET /account/security/status` | `test_get_auth_status.py` | success, no_auth |
| `POST /account/security/2fa/enable` | `test_enable_auth_factor.py` | totp_success, email_code, no_auth |
| `POST /account/security/2fa/disable` | `test_disable_auth_factor.py` | success, no_auth |
| `POST /account/security/2fa/backup-codes` | `test_generate_backup_codes.py` | success, no_auth |
| `POST /account/security/trusted-devices` | `test_add_trusted_device.py` | success, no_auth |
| `GET /account/security/trusted-devices` | `test_get_trusted_devices.py` | success, no_auth |
| `DELETE /account/security/trusted-devices/{fp}` | `test_remove_trusted_device.py` | success, no_auth |
| `POST /account/security/oauth/link` | `test_link_oauth.py` | success, no_auth |
| `GET /account/security/oauth` | `test_get_oauth_links.py` | success, no_auth |

### Шаблон: security endpoint

```python
"""E2E-тесты: POST /account/security/2fa/enable."""

import pytest

from tests.e2e.conftest import API


@pytest.mark.e2e
class TestEnableAuthFactor:
    """Включение фактора 2FA."""

    async def test_enable_totp_success(self, auth_client) -> None:
        """200 — TOTP-фактор включён, возвращает provisioning URI."""
        resp = await auth_client.post(
            f"{API}/account/security/2fa/enable",
            json={"method": "totp", "is_primary": True},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "provisioning_uri" in data or "method" in data

    async def test_enable_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(
            f"{API}/account/security/2fa/enable",
            json={"method": "totp", "is_primary": True},
        )
        assert resp.status_code == 401
```

---

## 10. Тесты Admin-эндпоинтов

Тесты в `tests/e2e/admin/` покрывают `AdminController`. Особенность — требуют admin-пользователя и проверяют RBAC (403 для обычных пользователей).

| Endpoint | Файл | Ключевые кейсы |
|---|---|---|
| `POST /admin/users/{uid}/roles/{rid}` | `test_assign_role.py` | admin_success, no_auth (401), forbidden (403), user_not_found (404) |
| `DELETE /admin/users/{uid}/roles/{rid}` | `test_remove_role.py` | admin_success, no_auth, forbidden, not_found |
| `POST /admin/users/{uid}/unlock` | `test_unlock_account.py` | admin_success, no_auth, forbidden, not_found |

### Шаблон: admin endpoint

```python
"""E2E-тесты: POST /admin/users/{user_id}/roles/{role_id}."""

import uuid

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login, register_admin_and_login


@pytest.mark.e2e
class TestAssignRole:
    """Назначение роли пользователю."""

    async def test_assign_role_success(self, client) -> None:
        """200 — роль назначена (admin-пользователь)."""
        admin = await register_admin_and_login(client)
        target = await register_and_login(client)
        headers = auth_headers(admin["access_token"])

        # Получаем список ролей
        roles_resp = await client.get(
            f"{API}/account/roles",
            headers=auth_headers(target["access_token"]),
        )
        roles = roles_resp.json()["data"]
        if len(roles) < 2:
            pytest.skip("Недостаточно ролей для теста")

        role_id = roles[1]["id"]
        resp = await client.post(
            f"{API}/admin/users/{target['user_id']}/roles/{role_id}",
            headers=headers,
        )
        assert resp.status_code == 200

    async def test_assign_role_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.post(
            f"{API}/admin/users/{uuid.uuid4()}/roles/{uuid.uuid4()}"
        )
        assert resp.status_code == 401

    async def test_assign_role_forbidden(self, client) -> None:
        """403 — обычный пользователь не может назначать роли."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/admin/users/{uuid.uuid4()}/roles/{uuid.uuid4()}",
            headers=auth_headers(user["access_token"]),
        )
        assert resp.status_code == 403

    async def test_assign_role_user_not_found(self, client) -> None:
        """404 — пользователь не найден."""
        admin = await register_admin_and_login(client)
        roles_resp = await client.get(
            f"{API}/account/roles",
            headers=auth_headers(admin["access_token"]),
        )
        roles = roles_resp.json()["data"]
        if not roles:
            pytest.skip("Нет ролей")

        resp = await client.post(
            f"{API}/admin/users/{uuid.uuid4()}/roles/{roles[0]['id']}",
            headers=auth_headers(admin["access_token"]),
        )
        assert resp.status_code == 404
```

### Паттерн: обязательные кейсы для admin-endpoints

Каждый admin-endpoint тестируется на **четыре кейса**:

1. **Success (200)** — `register_admin_and_login()` → запрос с admin-токеном
2. **No auth (401)** — запрос без `Authorization` header
3. **Forbidden (403)** — `register_and_login()` → запрос с обычным токеном
4. **Not found (404)** — admin-токен + несуществующий `user_id`

---

## 11. Тесты Profile-эндпоинтов

Тесты в `tests/e2e/profile/` покрывают `ProfileController`:

| Endpoint | Файл | Ключевые кейсы |
|---|---|---|
| `GET /profile/me` | `test_get_profile.py` | success, no_auth |
| `PUT /profile/me/appearance` | `test_update_appearance.py` | dark_theme, light_theme, invalid_color (422), no_auth |
| `PATCH /profile/me/personal-info` | `test_update_personal_info.py` | success, partial_update, no_auth |
| `PUT /profile/me/notifications` | `test_update_notifications.py` | success, no_auth |
| `PUT /profile/me/privacy` | `test_update_privacy.py` | success, no_auth |

### Шаблон: profile endpoint

```python
"""E2E-тесты: PUT /profile/me/appearance."""

import pytest

from tests.e2e.conftest import API


@pytest.mark.e2e
class TestUpdateAppearance:
    """Обновление настроек внешнего вида."""

    async def test_update_appearance_success(self, auth_client) -> None:
        """200 — настройки обновлены."""
        resp = await auth_client.put(
            f"{API}/profile/me/appearance",
            json={
                "theme": "dark",
                "accent_color": "#6366F1",
                "interface_density": "comfortable",
            },
        )
        assert resp.status_code == 200

    async def test_update_appearance_invalid_color(self, auth_client) -> None:
        """422 — невалидный формат цвета."""
        resp = await auth_client.put(
            f"{API}/profile/me/appearance",
            json={
                "theme": "dark",
                "accent_color": "not-a-color",
                "interface_density": "comfortable",
            },
        )
        assert resp.status_code == 422

    async def test_update_appearance_no_auth(self, client) -> None:
        """401 — без токена авторизации."""
        resp = await client.put(
            f"{API}/profile/me/appearance",
            json={"theme": "dark", "accent_color": "#6366F1", "interface_density": "comfortable"},
        )
        assert resp.status_code == 401
```

---

## 12. Scenario-тесты

Scenario-тесты в `tests/e2e/scenarios/` проверяют **многошаговые бизнес-флоу** — последовательность вызовов нескольких endpoint'ов, имитирующую реальное поведение пользователя.

### Список сценариев

| Файл | Сценарий | Шаги |
|---|---|---|
| `test_auth_flow.py` | Полный цикл аутентификации | register → login → /me → refresh → /me с новым токеном |
| `test_2fa_flow.py` | Цикл 2FA | enable TOTP → set-primary → disable |
| `test_oauth_flow.py` | Цикл OAuth | link → get links → unlink → get links (пусто) |
| `test_trusted_devices_flow.py` | Доверенные устройства | add → get list → remove → get list (пусто) |
| `test_backup_codes_flow.py` | Резервные коды | enable 2FA → generate codes → use code |
| `test_profile_settings_flow.py` | Настройки профиля | personal-info → appearance → notifications → privacy → get profile |
| `test_account_deletion_flow.py` | Удаление аккаунта | request-deletion → cancel-deletion → /me (доступен) |
| `test_account_disable_flow.py` | Деактивация | disable → reactivate → /me (доступен) |

### Шаблон: scenario-тест

```python
"""E2E-сценарий: <краткое описание шагов>."""

import pytest

from tests.e2e.conftest import API, auth_headers, register_and_login


@pytest.mark.e2e
class Test<Name>Flow:
    """<Описание цикла>."""

    async def test_<happy_path>(self, client) -> None:
        """<Шаг 1> → <Шаг 2> → ... → <финальная проверка>."""
        user = await register_and_login(client)
        headers = auth_headers(user["access_token"])

        # 1. Первый шаг
        resp1 = await client.post(f"{API}/...", headers=headers, json={...})
        assert resp1.status_code == 200

        # 2. Второй шаг
        resp2 = await client.get(f"{API}/...", headers=headers)
        assert resp2.status_code == 200
        # Проверяем, что результат первого шага виден

        # 3. Третий шаг (отмена / удаление)
        resp3 = await client.delete(f"{API}/...", headers=headers)
        assert resp3.status_code == 200

        # 4. Финальная проверка
        resp4 = await client.get(f"{API}/...", headers=headers)
        # Проверяем, что состояние корректное

    async def test_<negative_flow>(self, client) -> None:
        """<Негативный вариант> → <ожидаемая ошибка>."""
        user = await register_and_login(client)
        resp = await client.post(
            f"{API}/...",
            headers=auth_headers(user["access_token"]),
        )
        assert resp.status_code == 409  # или другой код ошибки
```

### Реальный пример: Auth Flow

```python
@pytest.mark.e2e
class TestAuthFlow:
    async def test_register_login_refresh_flow(self, client) -> None:
        """Регистрация → логин → refresh → использование нового access-токена."""
        # 1. Регистрация
        reg = await register_user(client)
        assert reg["response"].status_code == 201

        # 2. Логин
        login_resp = await client.post(
            f"{API}/auth/login",
            json={"email": reg["email"], "password": DEFAULT_PASSWORD},
        )
        assert login_resp.status_code == 200
        access_token = login_resp.json()["data"]["access_token"]
        refresh_token = login_resp.json()["data"]["refresh_token"]

        # 3. Проверяем access-токен
        me_resp = await client.get(f"{API}/account/me", headers=auth_headers(access_token))
        assert me_resp.status_code == 200

        # 4. Refresh
        refresh_resp = await client.post(
            f"{API}/auth/refresh", json={"refresh_token": refresh_token},
        )
        assert refresh_resp.status_code == 200
        new_access = refresh_resp.json()["data"]["access_token"]
        assert new_access != access_token

        # 5. Проверяем новый access-токен
        me_resp2 = await client.get(f"{API}/account/me", headers=auth_headers(new_access))
        assert me_resp2.status_code == 200
```

### Реальный пример: CRUD-цикл (Trusted Devices)

```python
@pytest.mark.e2e
class TestTrustedDevicesFlow:
    async def test_add_get_remove_device(self, client) -> None:
        """add → get (есть) → remove → get (нет)."""
        user = await register_and_login(client)
        headers = auth_headers(user["access_token"])
        fingerprint = uuid.uuid4().hex[:12]

        # 1. Добавляем
        add_resp = await client.post(
            f"{API}/account/security/trusted-devices",
            json={"device_fingerprint": fingerprint},
            headers=headers,
        )
        assert add_resp.status_code == 200

        # 2. Проверяем наличие
        list_resp = await client.get(f"{API}/account/security/trusted-devices", headers=headers)
        fingerprints = [d.get("device_fingerprint", "") for d in list_resp.json()["data"]]
        assert fingerprint in fingerprints

        # 3. Удаляем
        remove_resp = await client.delete(
            f"{API}/account/security/trusted-devices/{fingerprint}", headers=headers,
        )
        assert remove_resp.status_code == 200

        # 4. Проверяем отсутствие
        list_resp2 = await client.get(f"{API}/account/security/trusted-devices", headers=headers)
        fingerprints2 = [d.get("device_fingerprint", "") for d in list_resp2.json()["data"]]
        assert fingerprint not in fingerprints2
```

### Когда писать scenario-тест

| Критерий | Пример |
|---|---|
| **Многошаговый бизнес-процесс** | register → login → refresh |
| **CRUD-цикл** | create → list → delete → list (пусто) |
| **Конфликтные состояния** | disable → reactivate, request-deletion → cancel |
| **Зависимость между endpoint'ами** | enable 2FA → generate backup codes → use code |

---

## 13. Конвенции и антипаттерны

### Именование

| Элемент | Конвенция | Пример |
|---|---|---|
| **Файл** | `test_<action>.py` | `test_register.py`, `test_get_me.py` |
| **Файл (scenario)** | `test_<name>_flow.py` | `test_auth_flow.py` |
| **Класс** | `Test<Action>` | `TestRegister`, `TestGetMe`, `TestAuthFlow` |
| **Метод** | `test_<action>_<outcome>` | `test_register_success`, `test_login_wrong_password` |

### Docstring файла

```python
"""E2E-тесты: <HTTP_METHOD> <endpoint_path>."""
```

```python
"""E2E-сценарий: <краткое описание шагов>."""
```

### Docstring метода

```python
async def test_register_success(self, client) -> None:
    """201 — успешная регистрация."""
```

Формат: `"""<HTTP_CODE> — <описание>."""` — код ответа в начале для быстрого сканирования.

### Response envelope

Все endpoint'ы возвращают ответ в формате `SuccessResponse`:

```json
{
    "data": { ... }
}
```

Доступ к данным: `resp.json()["data"]`.

### Импорты из conftest

```python
from tests.e2e.conftest import API, register_user
from tests.e2e.conftest import API, DEFAULT_PASSWORD, auth_headers, register_and_login
from tests.e2e.conftest import API, auth_headers, register_and_login, register_admin_and_login
```

Импортируются **только** используемые в файле хелперы.

### `auth_client` vs `register_and_login`

| Использовать `auth_client` | Использовать `register_and_login()` |
|---|---|
| Простой GET/POST от текущего пользователя | Нужны данные пользователя (email, user_id) |
| Один пользователь в тесте | Несколько пользователей |
| Не нужен refresh_token | Нужен refresh_token |
| `test_get_me_success(self, auth_client)` | `test_change_password_success(self, client)` |

### Антипаттерны

| ❌ Не делать | ✅ Делать |
|---|---|
| Прямой доступ к repos/handlers | Только HTTP-запросы через `client` |
| Хардкодить email | `_unique_email()` или helpers |
| Проверять внутреннее состояние БД | Проверять HTTP-ответ (`resp.status_code`, `resp.json()`) |
| Один огромный тест на весь контроллер | Отдельный файл на endpoint |
| Забыть `@pytest.mark.e2e` | Тест будет пропущен autouse-фикстурой |
| `session.commit()` / raw SQL в тестах | Только через helpers (`register_admin_and_login` — единственное исключение) |
| Мокать repos или handlers | Только `InMemoryMessageBrokerAdapter` и `InMemoryOAuthAdapter` (в conftest) |
| Использовать `auth_client` + `register_and_login` одновременно | Выбрать один подход в тесте |
| Пропускать тест 401 (no_auth) | Каждый защищённый endpoint тестируется без токена |
| Тестировать бизнес-логику в E2E | Для этого есть unit и integration тесты |

### Типизация

Все тестовые методы аннотируются `-> None`:

```python
async def test_register_success(self, client) -> None:
    ...
```

---

## 14. Чеклист нового контроллера / BC

### Подготовка

- [ ] Определить, к какой группе относится контроллер (`auth/`, `account/`, `security/`, `admin/`, `profile/`, или новая)
- [ ] Создать директорию `tests/e2e/<group>/` с `__init__.py`

### Conftest (при необходимости)

- [ ] Если нужны новые In-memory заглушки — добавить в `tests/e2e/conftest.py`
- [ ] Override в DI-контейнере: `container.<port>.override(<InMemoryAdapter>())`
- [ ] Если нужны новые helper-функции — добавить в `tests/e2e/conftest.py`
- [ ] Если нужны новые фикстуры — добавить в `tests/e2e/conftest.py`

### Endpoint-тесты

- [ ] Один файл на endpoint: `test_<action>.py`
- [ ] Класс с `@pytest.mark.e2e`: `class Test<Action>:`
- [ ] Docstring файла: `"""E2E-тесты: <METHOD> <path>."""`
- [ ] Docstring методов: `"""<HTTP_CODE> — <описание>."""`

### Обязательные кейсы для каждого endpoint

#### Публичный endpoint (auth)
- [ ] **Success** (200/201) — корректные данные → правильный ответ
- [ ] **Validation** (422) — невалидный input
- [ ] **Business error** (409/400) — бизнес-конфликт

#### Защищённый endpoint (account, security, profile)
- [ ] **Success** (200) — `auth_client` или `register_and_login()` + `auth_headers()`
- [ ] **No auth** (401) — запрос через `client` без токена
- [ ] **Validation** (422) — если есть input validation
- [ ] **Not found** (404) — если применимо

#### Admin endpoint
- [ ] **Admin success** (200) — `register_admin_and_login()`
- [ ] **No auth** (401) — без токена
- [ ] **Forbidden** (403) — `register_and_login()` (обычный user)
- [ ] **Not found** (404) — несуществующий ID

### Scenario-тесты

- [ ] Если endpoint — часть многошагового процесса → scenario-тест в `tests/e2e/scenarios/`
- [ ] Имя файла: `test_<name>_flow.py`
- [ ] Happy path: полный цикл от начала до конца
- [ ] Negative path: ошибка при нарушении порядка шагов (409)

### Profile BC (если новый BC)

- [ ] Создать директорию `tests/e2e/<bc_name>/` с `__init__.py`
- [ ] Тесты для каждого endpoint контроллера
- [ ] Scenario-тест для полного цикла настроек (если есть)

### Проверки

- [ ] Каждый тест-класс помечен `@pytest.mark.e2e`
- [ ] Каждый тестовый метод — `async def` с аннотацией `-> None`
- [ ] Импорты из `tests.e2e.conftest` — только используемые
- [ ] Нет прямого доступа к repos/handlers
- [ ] Все assertions на `resp.status_code` и `resp.json()`
- [ ] `pytest -m e2e` проходит без ошибок
