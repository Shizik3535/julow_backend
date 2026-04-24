# Гайд: Presentation Layer для Bounded Context

## Содержание

1. [Обзор](#1-обзор)
2. [Структура директорий](#2-структура-директорий)
3. [Базовые классы (shared presentation)](#3-базовые-классы-shared-presentation)
4. [Schemas: Request](#4-schemas-request)
5. [Schemas: Response](#5-schemas-response)
6. [Controller](#6-controller)
7. [Dependencies](#7-dependencies)
8. [API Router и регистрация в приложении](#8-api-router-и-регистрация-в-приложении)
9. [Глобальная обработка ошибок](#9-глобальная-обработка-ошибок)
10. [Пакетные `__init__.py`](#10-пакетные-__init__py)
11. [Чеклист нового BC](#11-чеклист-нового-bc)

---

## 1. Обзор

Presentation Layer — точка входа HTTP-запросов. Отвечает за:

- Приём и валидацию входных данных (request schemas).
- Преобразование request → Command/Query.
- Вызов handler'а из application layer.
- Преобразование DTO → response schema.
- Формирование стандартизированного HTTP-ответа.

**Зависимости**: presentation зависит от application layer своего BC, `app.shared.presentation` и `app.core.di`. **Не** зависит от domain и infrastructure напрямую (кроме получения зависимостей через DI).

**Не содержит** бизнес-логики — только маршрутизация, валидация ввода и форматирование вывода.

---

## 2. Структура директорий

### BC-уровень

```
app/context/<bc_name>/presentation/
├── __init__.py                      # Реэкспорт контроллеров
├── controllers/
│   ├── __init__.py                  # Реэкспорт всех контроллеров
│   └── <group>_controller.py        # Один контроллер = одна группа endpoint'ов
├── dependencies.py                  # FastAPI Depends-функции (DI-мост)
└── schemas/
    ├── __init__.py                  # Реэкспорт всех request + response схем
    ├── requests/
    │   ├── __init__.py              # Реэкспорт request-схем
    │   └── <action>_request.py      # Pydantic-модель тела запроса
    └── responses/
        ├── __init__.py              # Реэкспорт response-схем
        └── <entity>_response.py     # Pydantic-модель ответа
```

### Shared presentation

```
app/shared/presentation/
├── base_controller.py               # BaseController (ABC + router + error mapping)
├── base_presenter.py                # BasePresenter (DTO → response helpers)
├── requests/
│   └── paginated_request.py         # PaginatedRequest (page, page_size)
└── responses/
    ├── success_response.py          # SuccessResponse[T], MessageData, MessageResponse
    ├── error_response.py            # ErrorDetail, ErrorResponse
    └── paginated_response.py        # PaginatedResponse[T], PaginationMeta
```

### API Router (точка сборки)

```
app/api/
├── __init__.py
└── v1/
    ├── __init__.py                  # Реэкспорт api_v1_router
    └── router.py                    # Сборка роутеров всех BC
```

---

## 3. Базовые классы (shared presentation)

### Стандартные обёртки ответов

| Класс | Назначение |
|---|---|
| `SuccessResponse[T]` | `{ success: true, data: T }` |
| `MessageResponse` | `SuccessResponse[MessageData]` — `{ success: true, data: { message: "..." } }` |
| `ErrorResponse` | `{ success: false, error: ErrorDetail, details: [...] }` |
| `ErrorDetail` | `{ code: "...", message: "...", field?: "..." }` |
| `PaginatedResponse[T]` | `{ success: true, items: [...], pagination: {...} }` |
| `PaginationMeta` | `{ total, page, page_size, pages }` |

Все ответы — Pydantic-модели с `from_attributes=True`.

### BaseController

ABC для контроллеров. Предоставляет:

- `self._router` — `APIRouter` с prefix и tags.
- `_register_routes()` — абстрактный метод для регистрации маршрутов.
- `_handle_domain_exception()` — маппинг доменных исключений → `HTTPException`.

```python
class BaseController(ABC):
    def __init__(self, prefix: str, tags: list[str] | None = None, presenter: BasePresenter | None = None):
        self._router = APIRouter(prefix=prefix, tags=tags)
        self._presenter = presenter
        self._register_routes()

    @property
    def router(self) -> APIRouter: ...

    @abstractmethod
    def _register_routes(self) -> None: ...

    def _handle_domain_exception(self, exc: DomainException) -> HTTPException: ...
```

### BasePresenter

Утилитный класс для формирования ответов:

```python
class BasePresenter(ABC, Generic[TDTO]):
    @abstractmethod
    def present(self, dto: TDTO) -> dict[str, Any]: ...
    def present_list(self, dtos: list[TDTO]) -> list[dict[str, Any]]: ...

    @staticmethod
    def success(data=None) -> SuccessResponse: ...
    @staticmethod
    def message(message: str) -> MessageResponse: ...
    @staticmethod
    def paginated(items, total, page, page_size) -> PaginatedResponse: ...
    @staticmethod
    def error(code, message, field=None, details=None) -> ErrorResponse: ...
```

---

## 4. Schemas: Request

Request-схемы — Pydantic-модели, описывающие тело HTTP-запроса. Определяют контракт API.

### Правила

- Наследуются от `pydantic.BaseModel`.
- Один файл — одна схема (или тесно связанная группа).
- Имя: `<Action>Request` — `RegisterRequest`, `UpdateAppearanceRequest`, `LoginRequest`.
- Поля — только примитивы, с `Field(...)` для документации, валидации и примеров.
- `json_schema_extra` с `example` — для Swagger UI.
- Валидация (min_length, max_length, pattern, ge, le) — на уровне Pydantic, не в controller.
- **Не** импортируют из domain или application.

### Шаблон

```python
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DoSomethingRequest(BaseModel):
    """
    Тело запроса ...

    Атрибуты:
        field_1: Описание.
        field_2: Описание.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "field_1": "value",
                "field_2": 42,
            },
        },
    )

    field_1: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Описание поля",
        examples=["value"],
    )
    field_2: int = Field(
        default=0,
        ge=0,
        description="Числовое поле",
        examples=[42],
    )
```

### Паттерн: вложенные input-схемы

Для сложных запросов (например уведомления с каналами):

```python
class ChannelPreferenceInput(BaseModel):
    channel: str = Field(..., description="Канал")
    is_enabled: bool = Field(default=True)


class TypePreferenceInput(BaseModel):
    notification_type: str = Field(...)
    is_enabled: bool = Field(default=True)
    channels: list[ChannelPreferenceInput] = Field(default_factory=list)


class UpdateNotificationsRequest(BaseModel):
    type_preferences: list[TypePreferenceInput]
```

### Паттерн: partial update (PATCH)

Для частичного обновления — поля с `None` по умолчанию:

```python
class UpdatePersonalInfoRequest(BaseModel):
    bio: str | None = Field(default=None, max_length=1000)
    job_title: str | None = Field(default=None, max_length=255)
```

---

## 5. Schemas: Response

Response-схемы — Pydantic-модели, определяющие формат ответа клиенту.

### Правила

- Наследуются от `pydantic.BaseModel` (не от `BaseDTO`).
- `model_config = ConfigDict(from_attributes=True)` — для маппинга из DTO.
- Имя: `<Entity>Response` — `UserResponse`, `ProfileResponse`, `LoginResponse`.
- Каждое поле — с `Field(description=..., examples=[...])` для Swagger.
- Поля — только примитивы.
- **Не** совпадают 1:1 с DTO — response может скрывать поля, агрегировать, менять имена.

### Шаблон

```python
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MyEntityResponse(BaseModel):
    """
    Ответ с данными ...

    Атрибуты:
        id: UUID.
        ...
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        ...,
        description="UUID сущности",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    name: str = Field(..., description="Название", examples=["Example"])
    created_at: datetime = Field(..., description="Дата создания (UTC)")
    updated_at: datetime = Field(..., description="Дата последнего обновления (UTC)")
```

### Шаблон: составной response

```python
class LoginResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user: UserResponse = Field(..., description="Данные пользователя")
    access_token: str = Field(..., description="JWT access-токен")
    refresh_token: str = Field(..., description="JWT refresh-токен")
    access_expires_in: int = Field(..., description="TTL access-токена (секунды)")
    refresh_expires_in: int = Field(..., description="TTL refresh-токена (секунды)")
```

---

## 6. Controller

Controller — класс, группирующий связанные endpoint'ы. Наследует `BaseController`.

### Правила

- Один контроллер = одна группа endpoint'ов (auth, account, profile и т.д.).
- Конструктор: `super().__init__(prefix="/...", tags=["..."])`.
- `_register_routes()` — регистрирует все маршруты через `self._router.add_api_route(...)`.
- Endpoint-методы: `async def`.
- Зависимости через `Depends(...)` — repo, ports, event_bus, user_id.
- Внутри endpoint: **создать handler → создать command/query → вызвать handler → вернуть response**.
- **Не** содержит бизнес-логики.

### Шаблон: Controller

```python
from __future__ import annotations

from fastapi import Depends

from app.shared.presentation.base_controller import BaseController
from app.shared.presentation.responses import ErrorResponse, MessageResponse, SuccessResponse

from app.context.<bc_name>.application.commands.<use_case> import (
    DoSomethingCommand,
    DoSomethingHandler,
)
from app.context.<bc_name>.application.queries.<use_case> import (
    GetMyEntityHandler,
    GetMyEntityQuery,
)
from app.context.<bc_name>.presentation.dependencies import (
    get_current_user_id,
    get_<bc>_event_bus,
    get_<aggregate>_repository,
)
from app.context.<bc_name>.presentation.schemas.requests.<action>_request import DoSomethingRequest
from app.context.<bc_name>.presentation.schemas.responses.<entity>_response import MyEntityResponse


class MyController(BaseController):
    """
    Контроллер <BC_Name> BC.

    Endpoint'ы:
        GET    /<prefix>/me          — Получить свой <entity>
        POST   /<prefix>/me/<action> — Выполнить действие
    """

    def __init__(self) -> None:
        super().__init__(prefix="/<prefix>", tags=["<BC_Name>"])

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/me",
            self.get_my_entity,
            methods=["GET"],
            response_model=SuccessResponse[MyEntityResponse],
            summary="Получить ...",
            description="Подробное описание ...",
            responses={
                200: {"description": "Успех"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                404: {"description": "Не найден", "model": ErrorResponse},
            },
        )
        self._router.add_api_route(
            "/me/<action>",
            self.do_something,
            methods=["POST"],
            response_model=MessageResponse,
            summary="Выполнить ...",
            description="Подробное описание ...",
            responses={
                200: {"description": "Успех"},
                401: {"description": "Не аутентифицирован", "model": ErrorResponse},
                422: {"description": "Ошибка валидации", "model": ErrorResponse},
            },
        )

    async def get_my_entity(
        self,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_<aggregate>_repository),
    ) -> SuccessResponse[MyEntityResponse]:
        """Получить <entity> текущего пользователя."""
        handler = GetMyEntityHandler(repo=repo)
        query = GetMyEntityQuery(user_id=user_id)
        dto = await handler.handle(query)
        return SuccessResponse(data=MyEntityResponse.model_validate(dto.model_dump()))

    async def do_something(
        self,
        body: DoSomethingRequest,
        user_id: str = Depends(get_current_user_id),
        repo=Depends(get_<aggregate>_repository),
        event_bus=Depends(get_<bc>_event_bus),
    ) -> MessageResponse:
        """Выполнить действие."""
        handler = DoSomethingHandler(repo=repo, event_bus=event_bus)
        command = DoSomethingCommand(
            user_id=user_id,
            field_1=body.field_1,
            field_2=body.field_2,
        )
        await handler.handle(command)
        return SuccessResponse(data={"message": "Операция выполнена"})
```

### Паттерн: маппинг DTO → Response

DTO из application layer → Response schema через `model_validate`:

```python
dto = await handler.handle(query)
return SuccessResponse(data=MyEntityResponse.model_validate(dto.model_dump()))
```

Для составных DTO:

```python
dto = await handler.handle(command)
user_resp = UserResponse.model_validate(dto.user.model_dump())
login_resp = LoginResponse(
    user=user_resp,
    access_token=dto.access_token,
    ...
)
return SuccessResponse(data=login_resp)
```

### Паттерн: извлечение данных из Request

IP и User-Agent извлекаются из `fastapi.Request`:

```python
from fastapi import Request

async def login(self, body: LoginRequest, request: Request, ...):
    command = LoginUserCommand(
        email=body.email,
        ip=request.client.host if request.client else "127.0.0.1",
        user_agent=request.headers.get("user-agent", "unknown"),
    )
```

### Паттерн: Query-параметры (GET с фильтрацией)

```python
from fastapi import Query

async def get_roles(
    self,
    name: str | None = Query(default=None, description="Фильтр по имени"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    user_id: str = Depends(get_current_user_id),
    role_repo=Depends(get_role_repository),
):
    handler = GetRolesHandler(role_repo=role_repo)
    query = GetRolesQuery(name=name, offset=offset, limit=limit)
    dto = await handler.handle(query)
    roles = [RoleResponse.model_validate(r.model_dump()) for r in dto.items]
    return SuccessResponse(data=roles)
```

### Паттерн: Path-параметры

```python
async def get_role(self, role_id: str, ...):
    query = GetRoleByIdQuery(role_id=role_id)
    ...
```

### Регистрация маршрутов: `add_api_route`

Ключевые параметры:

| Параметр | Назначение |
|---|---|
| `path` | Путь (относительно prefix контроллера) |
| `endpoint` | Async-метод контроллера |
| `methods` | `["GET"]`, `["POST"]`, `["PUT"]`, `["PATCH"]`, `["DELETE"]` |
| `response_model` | Тип ответа для Swagger (`SuccessResponse[MyResponse]`) |
| `status_code` | HTTP-код (по умолчанию 200; 201 для создания) |
| `summary` | Краткое описание для OpenAPI |
| `description` | Подробное описание |
| `responses` | Словарь дополнительных кодов ответа с `model` |

---

## 7. Dependencies

`dependencies.py` — мост между FastAPI DI (`Depends`) и DI-контейнером приложения (`Container`).

### Правила

- Один файл на BC: `<bc_name>/presentation/dependencies.py`.
- Все функции — `def` / `async def`, вызываются через `Depends(...)`.
- `get_container(request: Request)` → извлечь `Container` из `app.state`.
- `get_db_session(container)` → per-request `AsyncSession` с commit/rollback.
- `get_<repo>(session, container)` → репозиторий из контейнера с текущей session.
- `get_<port>(container)` → shared порт (Singleton) из контейнера.
- `get_<bc>_event_bus(container)` → DomainEventBus для этого BC.
- `get_current_user_id(credentials, auth_token_port)` → JWT → user_id.

### Шаблон

```python
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
    """Извлечь DI-контейнер из FastAPI state."""
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
# <BcName> BC — Repositories
# ---------------------------------------------------------------------------

def get_<aggregate>_repository(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
):
    """Получить <Aggregate>Repository из DI-контейнера."""
    return container.<bc>_repo(session=session)


# ---------------------------------------------------------------------------
# Shared ports
# ---------------------------------------------------------------------------

def get_auth_token_port(container: Container = Depends(get_container)):
    """Получить AuthTokenPort из DI-контейнера."""
    return container.auth_token_port()


def get_<bc>_event_bus(container: Container = Depends(get_container)):
    """Получить DomainEventBus <BcName> BC из DI-контейнера."""
    return container.<bc>_event_bus()


# ---------------------------------------------------------------------------
# Auth — текущий пользователь
# ---------------------------------------------------------------------------

def get_current_user_id(
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
```

### Дублирование get_db_session и get_current_user_id

Каждый BC определяет собственные `get_db_session` и `get_current_user_id` — это **нормально**. FastAPI Depends работает per-module, и это обеспечивает изоляцию. При переходе на микросервисы каждый BC будет иметь свой независимый dependencies-модуль.

### Integration ports в dependencies

Если BC потребляет данные от другого BC (inboard-порт):

```python
def get_identity_user_port(container: Container = Depends(get_container)):
    """Получить IdentityUserPort (inboard) из DI-контейнера."""
    return container.profile_identity_user_port()
```

---

## 8. API Router и регистрация в приложении

### `app/api/v1/router.py`

Единая точка сборки всех endpoint'ов API v1. Каждый BC регистрирует свои контроллеры:

```python
from fastapi import APIRouter

api_v1_router = APIRouter()

# Identity BC
from app.context.identity.presentation.controllers import AuthController, AccountController

_auth_controller = AuthController()
_account_controller = AccountController()

api_v1_router.include_router(_auth_controller.router)
api_v1_router.include_router(_account_controller.router)

# Profile BC
from app.context.profile.presentation.controllers import ProfileController

_profile_controller = ProfileController()

api_v1_router.include_router(_profile_controller.router)

# ← Добавить новый BC:
# from app.context.<bc_name>.presentation.controllers import MyController
#
# _my_controller = MyController()
# api_v1_router.include_router(_my_controller.router)
```

### `app/main.py`

Роутер подключается к FastAPI-приложению с API-префиксом:

```python
app.include_router(api_v1_router, prefix=settings.app.api_prefix)
```

Результирующие URL: `<api_prefix>/<controller_prefix>/<route_path>`, например `/api/v1/auth/register`.

### Lifecycle

```
create_app()
├── Container()               — создание DI-контейнера
├── app.state.container = ...  — сохранение в state
├── middleware                  — correlation ID, logging, CORS
├── register_exception_handlers — глобальные обработчики ошибок
└── include_router(api_v1_router, prefix=...)

lifespan(app)
├── broker.start()             — запуск Kafka producer
├── wire_messaging(container)  — подписка на топики
├── yield                      — приложение работает
├── broker.stop()              — остановка Kafka
```

---

## 9. Глобальная обработка ошибок

Файл `app/core/exception_handlers.py` регистрирует глобальные обработчики, перехватывающие все исключения и возвращающие унифицированный `ErrorResponse`.

### Маппинг исключений → HTTP-коды

| Исключение | HTTP-код | `code` |
|---|---|---|
| `EntityNotFoundException` | 404 | `NOT_FOUND` |
| `ValidationException` | 422 | `VALIDATION_ERROR` |
| `BusinessRuleViolationException` | 409 | `BUSINESS_RULE_VIOLATION` |
| `DomainException` (прочие) | 400 | `DOMAIN_ERROR` |
| `RequestValidationError` (Pydantic) | 422 | `VALIDATION_ERROR` + details по полям |
| `StarletteHTTPException` | по коду | `HTTP_ERROR` |
| `Exception` (unhandled) | 500 | `INTERNAL_ERROR` |

Благодаря глобальным обработчикам, контроллеры **не нужно оборачивать в try/except** — исключения из handler'ов автоматически конвертируются в ответ.

### ApplicationException

Application-исключения (`ApplicationException`) обрабатываются через `DomainException` → 400 (т.к. `ApplicationException` наследует общий базовый класс). При необходимости можно добавить отдельный handler:

```python
@app.exception_handler(ApplicationException)
async def app_exception_handler(request, exc):
    return _json_response(400, ErrorResponse(
        error=ErrorDetail(code="APPLICATION_ERROR", message=str(exc)),
    ))
```

---

## 10. Пакетные `__init__.py`

### `presentation/__init__.py`

```python
from app.context.<bc_name>.presentation.controllers import MyController

__all__ = [
    "MyController",
]
```

### `controllers/__init__.py`

```python
from app.context.<bc_name>.presentation.controllers.<group>_controller import MyController

__all__ = [
    "MyController",
]
```

### `schemas/__init__.py`

Реэкспорт всех request + response:

```python
from app.context.<bc_name>.presentation.schemas.requests import (
    DoSomethingRequest,
    UpdateFieldRequest,
)
from app.context.<bc_name>.presentation.schemas.responses import (
    MyEntityResponse,
)

__all__ = [
    "DoSomethingRequest",
    "MyEntityResponse",
    "UpdateFieldRequest",
]
```

### `schemas/requests/__init__.py`, `schemas/responses/__init__.py`

Полный реэкспорт всех классов.

---

## 11. Чеклист нового BC

Для создания presentation layer нового Bounded Context `<bc_name>`:

### Schemas

- [ ] Создать `schemas/requests/` — по одному файлу на action (POST/PUT/PATCH body)
- [ ] Создать `schemas/responses/` — по одному файлу на entity/result response
- [ ] Каждое поле — с `Field(description=..., examples=[...])`
- [ ] Request-схемы — с `json_schema_extra` для Swagger example
- [ ] Response-схемы — с `ConfigDict(from_attributes=True)`

### Controllers

- [ ] Создать `controllers/<group>_controller.py` — наследник `BaseController`
- [ ] Определить prefix и tags в конструкторе
- [ ] Реализовать `_register_routes()` — все endpoint'ы через `add_api_route`
- [ ] Каждый endpoint: `summary`, `description`, `response_model`, `responses`
- [ ] Каждый endpoint: request → command/query → handler → response

### Dependencies

- [ ] Создать `dependencies.py` с функциями для FastAPI `Depends`
- [ ] `get_container`, `get_db_session` — базовые
- [ ] `get_<repo>` — для каждого репозитория BC
- [ ] `get_<bc>_event_bus` — DomainEventBus нового BC
- [ ] `get_current_user_id` — JWT-аутентификация
- [ ] При необходимости — `get_<port>` для shared и integration портов

### API Router

- [ ] Зарегистрировать контроллеры в `app/api/v1/router.py`
- [ ] Инстанцировать контроллер и `include_router`

### Проверки

- [ ] Presentation layer не импортирует из domain или infrastructure напрямую
- [ ] Все endpoint'ы документированы для Swagger
- [ ] Ответы обёрнуты в `SuccessResponse[T]` или `MessageResponse`
- [ ] Ошибки обрабатываются глобально — контроллеры не содержат try/except
