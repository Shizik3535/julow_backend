# Гайд: Application Layer для Bounded Context

## Содержание

1. [Обзор](#1-обзор)
2. [Структура директорий](#2-структура-директорий)
3. [Базовые классы (shared application)](#3-базовые-классы-shared-application)
4. [Command + CommandHandler](#4-command--commandhandler)
5. [Query + QueryHandler](#5-query--queryhandler)
6. [DTO](#6-dto)
7. [Event Handler](#7-event-handler)
8. [Application Exception](#8-application-exception)
9. [Ports: интеграционные порты между BC](#9-ports-интеграционные-порты-между-bc)
10. [Ports: BC-специфичные порты](#10-ports-bc-специфичные-порты)
11. [Ports: shared-порты инфраструктуры](#11-ports-shared-порты-инфраструктуры)
12. [Messaging: публикация и подписки](#12-messaging-публикация-и-подписки)
13. [Пакетные `__init__.py`](#13-пакетные-__init__py)
14. [Чеклист нового BC](#14-чеклист-нового-bc)

---

## 1. Обзор

Application Layer оркестрирует бизнес-операции. Он **не** содержит бизнес-логики — делегирует её доменному слою. Отвечает за:

- Приём команд (Command) и запросов (Query) от presentation layer.
- Загрузку и сохранение агрегатов через репозитории.
- Публикацию доменных событий через `DomainEventBus`.
- Маппинг доменных объектов в DTO.
- Реакцию на события из других BC через event handler'ы.
- Объявление интеграционных портов для межконтекстного взаимодействия.

**Зависимости**: application layer зависит от `app.shared.application`, `app.shared.domain` и domain layer своего BC. **Не** зависит от infrastructure и presentation.

---

## 2. Структура директорий

```
app/context/<bc_name>/application/
├── __init__.py                    # Реэкспорт подпакетов
├── commands/
│   ├── __init__.py                # Реэкспорт Command + Handler
│   └── <use_case>.py              # Command + CommandHandler в одном файле
├── queries/
│   ├── __init__.py                # Реэкспорт Query + Handler
│   └── <use_case>.py              # Query + QueryHandler в одном файле
├── dto/
│   ├── __init__.py                # Реэкспорт всех DTO
│   └── <entity>_dto.py            # Один файл — один DTO (или группа)
├── event_handlers/
│   ├── __init__.py                # Реэкспорт всех event handler'ов
│   └── on_<event>_<action>.py     # Один файл — один handler
├── exceptions/
│   ├── __init__.py                # Реэкспорт всех app-исключений
│   └── <aggregate>_app_exceptions.py
├── ports/
│   ├── __init__.py                # Реэкспорт всех портов (integration + BC-specific)
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── inboard/               # Порты, от которых МЫ зависим
│   │   │   ├── __init__.py
│   │   │   └── <source_bc>_<data>_port.py
│   │   └── outboard/              # Порты, которые МЫ предоставляем
│   │       ├── __init__.py
│   │       └── <our_bc>_<data>_provider.py
│   └── <concern>/                 # BC-специфичные порты (по аналогии с shared kernel)
│       ├── __init__.py
│       └── <concern>_port.py      # ABC-интерфейс для внешнего сервиса
└── messaging.py                   # Конфигурация DomainEventBus + подписки
```

**Конвенция**: Command и его Handler лежат в **одном файле** (например `register_user.py` содержит `RegisterUserCommand` + `RegisterUserHandler`). Аналогично для Query.

---

## 3. Базовые классы (shared application)

Все building blocks application layer наследуются от базовых классов из `app.shared.application`:

| Базовый класс | Назначение | Наследуется от |
|---|---|---|
| `BaseUseCase[TInput, TOutput]` | Общий предок всех handler'ов | `ABC` |
| `BaseCommand` | Команда (запрос на мутацию) | `pydantic.BaseModel` (frozen) |
| `BaseCommandHandler[TCmd, TResult]` | Обработчик команды | `BaseUseCase` |
| `BaseQuery` | Запрос (чтение данных) | `pydantic.BaseModel` (frozen) |
| `BaseQueryHandler[TQuery, TResult]` | Обработчик запроса | `BaseUseCase` |
| `BaseEventHandler[TEvent]` | Обработчик события | `BaseUseCase` |
| `BaseDTO` | Data Transfer Object | `pydantic.BaseModel` |
| `ApplicationException` | Базовое app-исключение | `Exception` |

### BaseUseCase

Общий предок. Предоставляет:
- `_logger` — structlog-логгер, привязанный к имени класса.
- `execute(input_) -> output` — единый интерфейс вызова.

```python
class BaseUseCase(ABC, Generic[TInput, TOutput]):
    def __init__(self) -> None:
        self._logger = get_logger(self.__class__.__name__)

    @abstractmethod
    async def execute(self, input_: TInput) -> TOutput: ...
```

`BaseCommandHandler`, `BaseQueryHandler`, `BaseEventHandler` наследуют `BaseUseCase` и добавляют абстрактный `handle()`, в который делегирует `execute()`.

---

## 4. Command + CommandHandler

Command — запрос на **изменение** состояния домена.

### Правила

- `Command` — Pydantic-модель (`BaseCommand`), **frozen**, поля — примитивы (`str`, `int`, `bool`).
- Имя — повелительное наклонение: `RegisterUser`, `UpdateAppearance`, `TerminateSession`.
- `CommandHandler` — наследник `BaseCommandHandler[TCommand, TResult]`.
- Один файл = одна пара `Command + Handler`.
- Handler не содержит бизнес-логики — делегирует агрегату.
- Паттерн: **загрузить → вызвать → сохранить → опубликовать события**.
- Зависимости инжектируются через `__init__`.

### Шаблон

```python
from __future__ import annotations

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.domain.value_objects.id_vo import Id
from app.context.<bc_name>.domain.repositories.<aggregate>_repository import MyAggregateRepository
from app.context.<bc_name>.domain.exceptions.<aggregate>_exceptions import MyAggregateNotFoundException


class DoSomethingCommand(BaseCommand):
    """
    Команда ...

    Атрибуты:
        user_id: ID пользователя.
        ...
    """

    user_id: str
    # ... поля — только примитивы ...


class DoSomethingHandler(BaseCommandHandler[DoSomethingCommand, None]):
    """
    Обработчик ...

    Загружает агрегат, вызывает доменный метод, сохраняет.
    """

    def __init__(
        self,
        repo: MyAggregateRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = repo
        self._event_bus = event_bus

    async def handle(self, command: DoSomethingCommand) -> None:
        # 1. Загрузить агрегат
        aggregate = await self._repo.get_by_user_id(Id.from_string(command.user_id))
        if aggregate is None:
            raise MyAggregateNotFoundException(command.user_id)

        # 2. Вызвать доменный метод (бизнес-логика в агрегате)
        aggregate.do_something(...)

        # 3. Сохранить
        await self._repo.update(aggregate)

        # 4. Опубликовать доменные события
        await self._event_bus.publish_all(aggregate.clear_domain_events())
```

### Handler, возвращающий результат

Некоторые handler'ы возвращают DTO (например при создании):

```python
class RegisterUserHandler(BaseCommandHandler[RegisterUserCommand, UserDTO]):
    async def handle(self, command: RegisterUserCommand) -> UserDTO:
        user = User.register(...)
        await self._user_repo.add(user)
        await self._event_bus.publish_all(user.clear_domain_events())
        return UserDTO(id=str(user.id), email=user.email.value, ...)
```

### Handler без event bus

Если операция не порождает событий — `event_bus` не нужен:

```python
class TerminateSessionHandler(BaseCommandHandler[TerminateSessionCommand, None]):
    def __init__(self, session_repo: SessionRepository) -> None:
        super().__init__()
        self._session_repo = session_repo

    async def handle(self, command: TerminateSessionCommand) -> None:
        session = await self._session_repo.get_by_id(Id.from_string(command.session_id))
        if session is None:
            raise SessionNotFoundException(command.session_id)
        session.terminate()
        await self._session_repo.update(session)
```

### Паттерн: работа с несколькими агрегатами

Если use case затрагивает несколько агрегатов **в одном BC**, handler оркестрирует их и публикует события от каждого:

```python
# register_user.py — создаёт User + UserAuth
await self._user_repo.add(user)
await self._user_auth_repo.add(user_auth)
await self._event_bus.publish_all(user.clear_domain_events())
await self._event_bus.publish_all(user_auth.clear_domain_events())
```

### Паттерн: конвертация примитивов в VO

Handler конвертирует примитивы из Command в доменные Value Objects:

```python
async def handle(self, command: UpdateAppearanceCommand) -> None:
    settings = AppearanceSettings(
        theme=Theme(command.theme),
        accent_color=Color(command.accent_color),
        interface_density=InterfaceDensity(command.interface_density),
    )
    profile.update_appearance(settings)
```

---

## 5. Query + QueryHandler

Query — запрос на **чтение** данных. Не изменяет состояние.

### Правила

- `Query` — Pydantic-модель (`BaseQuery`), **frozen**.
- Имя: `GetUserById`, `GetRoles`, `GetProfile`.
- `QueryHandler` — наследник `BaseQueryHandler[TQuery, TResult]`, где `TResult` наследует `BaseDTO`.
- Handler загружает данные через репозиторий и маппит в DTO.
- **Никогда** не мутирует агрегаты и не публикует события.

### Шаблон

```python
from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.<bc_name>.application.dto.<entity>_dto import MyDTO
from app.context.<bc_name>.domain.exceptions.<aggregate>_exceptions import MyNotFoundException
from app.context.<bc_name>.domain.repositories.<aggregate>_repository import MyRepository


class GetMyEntityQuery(BaseQuery):
    """
    Запрос ...

    Атрибуты:
        entity_id: Идентификатор.
    """

    entity_id: str


class GetMyEntityHandler(BaseQueryHandler[GetMyEntityQuery, MyDTO]):
    """Обработчик запроса ..."""

    def __init__(self, repo: MyRepository) -> None:
        super().__init__()
        self._repo = repo

    async def handle(self, query: GetMyEntityQuery) -> MyDTO:
        entity = await self._repo.get_by_id(Id.from_string(query.entity_id))
        if entity is None:
            raise MyNotFoundException(query.entity_id)

        return MyDTO(
            id=str(entity.id),
            # ... маппинг доменных полей в примитивы ...
        )
```

### Запросы с пагинацией/фильтрацией

```python
class GetRolesQuery(BaseQuery):
    system_only: bool = False
    offset: int = 0
    limit: int = 100

class GetRolesHandler(BaseQueryHandler[GetRolesQuery, RoleListDTO]):
    async def handle(self, query: GetRolesQuery) -> RoleListDTO:
        if query.system_only:
            roles = await self._role_repo.get_system_roles()
        else:
            roles = await self._role_repo.search(offset=query.offset, limit=query.limit)
        items = [RoleDTO(id=str(r.id), name=r.name, ...) for r in roles]
        return RoleListDTO(items=items, total=len(items))
```

---

## 6. DTO

DTO — объект для передачи данных между слоями. Не содержит бизнес-логики.

### Правила

- Наследуется от `BaseDTO` (Pydantic, `from_attributes=True`).
- Поля — **только примитивы** (`str`, `int`, `bool`, `datetime`, `list[str]`).
- Нет доменных типов (`Id`, `Email`, etc.) — всё конвертируется в строки.
- Один файл — один DTO (или тесно связанная группа).

### Виды DTO

| Вид | Пример | Назначение |
|---|---|---|
| **Entity DTO** | `UserDTO`, `ProfileDTO`, `SessionDTO` | Представление одного агрегата |
| **Result DTO** | `AuthResultDTO` | Составной результат (вложенные DTO) |
| **List DTO** | `RoleListDTO`, `SessionListDTO` | Обёртка для списка с `total` |
| **Settings DTO** | `ProfileSettingsDTO` | Проекция настроек для интеграции |

### Шаблон: Entity DTO

```python
from __future__ import annotations

from datetime import datetime

from app.shared.application.base_dto import BaseDTO


class MyEntityDTO(BaseDTO):
    """
    DTO ... (<BC_Name> BC).

    Атрибуты:
        id: Идентификатор.
        ...
    """

    id: str
    user_id: str
    # ... только примитивы ...
    created_at: datetime
    updated_at: datetime
```

### Шаблон: Составной DTO

```python
class AuthResultDTO(BaseDTO):
    user: UserDTO
    access_token: str
    refresh_token: str
    access_expires_in: int
    refresh_expires_in: int
```

### Шаблон: List DTO

```python
class RoleListDTO(BaseDTO):
    items: list[RoleDTO]
    total: int
```

---

## 7. Event Handler

Event Handler — реакция на доменное событие. Два сценария:

| Сценарий | Пример | Тип события |
|---|---|---|
| **Intra-BC** (внутри одного BC) | `OnUserLoggedInCreateSession` | Типизированный доменный класс |
| **Cross-BC** (между BC) | `OnUserRegisteredCreateProfile` | `dict[str, Any]` |

### Правила

- Наследуется от `BaseEventHandler[TEvent]`.
- Один handler — одно действие.
- Имя: `On<Event><Action>` — `OnUserRegisteredCreateProfile`.
- Cross-BC handler принимает `dict[str, Any]` — **не** импортирует типы из чужого BC.
- Обеспечивает **идемпотентность** — проверяет, не обработано ли событие ранее.

### Шаблон: Cross-BC handler

```python
from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.<bc_name>.domain.aggregates.<aggregate> import MyAggregate
from app.context.<bc_name>.domain.repositories.<aggregate>_repository import MyAggregateRepository


class OnSomeEventDoSomething(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события <EventName> из <Source> BC.

    Подписывается на топик «<source>.events».
    """

    def __init__(self, repo: MyAggregateRepository) -> None:
        super().__init__()
        self._repo = repo

    async def handle(self, event: dict[str, Any]) -> None:
        # 1. Проверить тип события
        event_type = event.get("event_type")
        if event_type != "ExpectedEventName":
            return

        # 2. Извлечь данные из payload
        payload = event.get("payload", {})
        user_id_str = payload.get("user_id")
        if not user_id_str:
            self._logger.warning("Event missing user_id", event=event)
            return

        user_id = Id.from_string(user_id_str)

        # 3. Идемпотентность: проверить, не обработано ли
        existing = await self._repo.get_by_user_id(user_id)
        if existing is not None:
            self._logger.warning("Already processed, skipping", user_id=user_id_str)
            return

        # 4. Выполнить действие
        aggregate = MyAggregate.create(user_id=user_id)
        await self._repo.add(aggregate)
```

### Шаблон: Intra-BC handler

```python
from app.shared.application.base_event_handler import BaseEventHandler
from app.context.<bc_name>.domain.events.<events> import SomeEvent


class OnSomeEventDoSomething(BaseEventHandler[SomeEvent]):
    """Межагрегатное взаимодействие внутри <BC_Name> BC."""

    def __init__(self, repo: SomeRepository) -> None:
        super().__init__()
        self._repo = repo

    async def handle(self, event: SomeEvent) -> None:
        aggregate = SomeAggregate.create(
            user_id=Id.from_string(event.user_id),
            ...
        )
        await self._repo.add(aggregate)
```

---

## 8. Application Exception

App-исключения — ошибки, специфичные для application layer. Отличаются от доменных: это ошибки оркестрации, а не бизнес-правил.

### Правила

- Наследуются от `ApplicationException`.
- Группировка: один файл = исключения одного агрегата/use case.
- Типичные случаи: дубликат при создании, блокировка аккаунта, невалидный токен.

### Когда app-exception vs domain-exception?

| Ситуация | Тип |
|---|---|
| Нарушение инварианта агрегата | `DomainException` (domain layer) |
| Сущность не найдена | `EntityNotFoundException` (domain layer) |
| Дубликат при регистрации | `ApplicationException` (app layer) |
| Аккаунт заблокирован | `ApplicationException` (app layer) |
| Невалидный refresh-токен | `ApplicationException` (app layer) |

### Шаблон

```python
from __future__ import annotations

from app.shared.application.application_exceptions import ApplicationException


class MyEntityAlreadyExistsException(ApplicationException):
    """Описание ошибки."""

    def __init__(self, identifier: str) -> None:
        super().__init__(f"<Entity> с {identifier} уже существует")
        self.identifier = identifier


class OperationNotAllowedException(ApplicationException):
    """Операция невозможна в текущем состоянии."""

    def __init__(self, reason: str = "") -> None:
        msg = "Операция невозможна"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)
```

---

## 9. Ports: интеграционные порты между BC

Интеграционные порты обеспечивают **синхронный** обмен данными между BC (в дополнение к асинхронному через события).

### Два направления

```
┌─────────────────────┐                    ┌─────────────────────┐
│     Identity BC      │                    │     Profile BC       │
│                     │                    │                     │
│  outboard/          │   DI-инъекция      │  inboard/           │
│  IdentityUserProvider│ ─────────────→    │  IdentityUserPort   │
│  (мы предоставляем) │                    │  (мы потребляем)    │
│                     │                    │                     │
│  inboard/           │   DI-инъекция      │  outboard/          │
│  (пусто)            │ ←─────────────     │  ProfileUserProvider│
│                     │                    │  (мы предоставляем) │
└─────────────────────┘                    └─────────────────────┘
```

| Тип порта | Директория | Кто определяет | Кто реализует | Кто использует |
|---|---|---|---|---|
| **Outboard** | `ports/integration/outboard/` | BC-владелец данных | Infrastructure BC-владельца | Другие BC |
| **Inboard** | `ports/integration/inboard/` | BC-потребитель | Infrastructure BC-потребителя (адаптер) | BC-потребитель |

### Outboard-порт (мы предоставляем данные)

Определяется в BC, который **владеет** данными. Возвращает DTO своего BC.

```python
# identity/application/ports/integration/outboard/identity_user_provider.py

from abc import ABC, abstractmethod
from app.context.identity.application.dto.user_dto import UserDTO


class IdentityUserProvider(ABC):
    """Outboard-порт: предоставляет данные пользователей другим BC."""

    @abstractmethod
    async def get_user(self, user_id: str) -> UserDTO | None: ...

    @abstractmethod
    async def get_users(self, user_ids: list[str]) -> list[UserDTO]: ...
```

### Inboard-порт (мы потребляем данные)

Определяется в BC, который **потребляет** данные. Возвращает `dict` или собственные типы — **не** DTO чужого BC.

```python
# profile/application/ports/integration/inboard/identity_user_port.py

from abc import ABC, abstractmethod
from typing import Any


class IdentityUserPort(ABC):
    """Inboard-порт: получение данных пользователя из Identity BC."""

    @abstractmethod
    async def get_user(self, user_id: str) -> dict[str, Any] | None: ...

    @abstractmethod
    async def user_exists(self, user_id: str) -> bool: ...
```

### Связь: Outboard ↔ Inboard

DI-контейнер связывает `IdentityUserPort` (inboard в Profile) с адаптером, который делегирует в `IdentityUserProvider` (outboard в Identity). Маппинг `UserDTO → dict` происходит в адаптере (infrastructure layer).

### Шаблон: Outboard Provider

```python
from __future__ import annotations

from abc import ABC, abstractmethod

from app.context.<bc_name>.application.dto.<entity>_dto import MyEntityDTO


class <BcName><Entity>Provider(ABC):
    """Outboard-порт: предоставляет данные ... другим BC."""

    @abstractmethod
    async def get_<entity>(self, <id>: str) -> MyEntityDTO | None: ...

    @abstractmethod
    async def get_<entities>(self, <ids>: list[str]) -> list[MyEntityDTO]: ...
```

### Шаблон: Inboard Port

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class <SourceBc><Entity>Port(ABC):
    """Inboard-порт: получение данных ... из <Source> BC."""

    @abstractmethod
    async def get_<entity>(self, <id>: str) -> dict[str, Any] | None: ...
```

---

## 10. Ports: BC-специфичные порты

Если Bounded Context нуждается в собственных абстракциях для внешних сервисов (не покрытых shared-портами из `app.shared.application.ports`), они размещаются в `ports/<concern>/` — по аналогии со структурой shared kernel.

### Когда создавать BC-специфичный порт

- Внешний сервис или технология используется **только** этим BC.
- Shared-порт существует, но BC нужен **расширенный** интерфейс (наследование от shared-порта или новый порт).
- BC требует интеграцию с уникальной внешней системой (платёжный шлюз, SMS-провайдер, специализированный API).

### Структура (зеркало shared kernel)

```
# Shared kernel (app/shared/application/ports/)
ports/
├── auth/                     # PasswordPort, AuthTokenPort
├── cache/                    # CachePort
├── messaging/                # MessageBrokerPort
├── file_storage/             # FileStoragePort
├── notification/             # EmailPort, PushPort
└── background_tasks/         # BackgroundTasksPort

# BC-специфичные порты (app/context/<bc_name>/application/ports/)
ports/
├── integration/              # Inter-BC порты (inboard/outboard)
├── <concern>/                # Группа по concern
│   ├── __init__.py
│   └── <concern>_port.py     # ABC-интерфейс
└── <another_concern>/
    ├── __init__.py
    └── <concern>_port.py
```

### Шаблон: BC-специфичный порт

```python
# <bc_name>/application/ports/payment/payment_gateway_port.py

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class PaymentResult:
    transaction_id: str
    status: str
    amount: float


class PaymentGatewayPort(ABC):
    """Порт для взаимодействия с платёжным шлюзом."""

    @abstractmethod
    async def charge(self, user_id: str, amount: float, currency: str) -> PaymentResult: ...

    @abstractmethod
    async def refund(self, transaction_id: str) -> bool: ...
```

Реализация (адаптер) этого порта размещается в infrastructure слое BC: `infrastructure/<concern>/` (см. гайд 02-infrastructure-layer).

---

## 11. Ports: shared-порты инфраструктуры

Общие инфраструктурные порты лежат в `app.shared.application.ports`. Они не специфичны для BC — используются любым BC:

| Порт | Модуль | Назначение |
|---|---|---|
| `PasswordPort` | `ports/auth/` | Хеширование и проверка паролей |
| `AuthTokenPort` | `ports/auth/` | Генерация и валидация JWT |
| `MessageBrokerPort` | `ports/messaging/` | Публикация/подписка на сообщения |
| `CachePort` | `ports/cache/` | Key-value кэш |
| `FileStoragePort` | `ports/file_storage/` | Загрузка/скачивание файлов |
| `EmailPort` | `ports/notification/` | Отправка email |
| `PushPort` | `ports/notification/` | Отправка push-уведомлений |
| `BackgroundTasksPort` | `ports/background_tasks/` | Запуск фоновых задач |

Handler инжектирует нужные порты через `__init__`:

```python
class RegisterUserHandler(BaseCommandHandler[RegisterUserCommand, UserDTO]):
    def __init__(
        self,
        user_repo: UserRepository,
        password_port: PasswordPort,      # shared port
        event_bus: DomainEventBus,
    ) -> None: ...
```

---

## 12. Messaging: публикация и подписки

Каждый BC имеет файл `messaging.py`, описывающий:
- В какой **топик** BC публикует свои события.
- На какие **топики** других BC он подписан.

### Компоненты

| Класс | Модуль | Назначение |
|---|---|---|
| `DomainEventBus` | `shared/application/messaging/` | ABC шины событий |
| `BrokerDomainEventBus` | `shared/application/messaging/` | Реализация через `MessageBrokerPort` |
| `Subscription` | `shared/application/messaging/` | Декларация подписки (topic + group_id + builder) |
| `subscribe_with_uow` | `shared/application/messaging/` | Подписка с UoW-обёрткой (session + commit/rollback) |

### Формат события (envelope)

`BrokerDomainEventBus` оборачивает каждое `BaseDomainEvent` в envelope:

```json
{
  "event_type": "UserRegistered",
  "event_id": "uuid",
  "occurred_at": "2026-04-22T12:00:00+00:00",
  "payload": { "user_id": "uuid", "email": "...", ... }
}
```

### Шаблон: messaging.py для нового BC

```python
"""
Messaging-конфигурация <BcName> BC.

BC описывает:
- в какой топик публикует свои доменные события;
- на какие топики других BC он подписан.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.application.messaging.broker_domain_event_bus import BrokerDomainEventBus
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.messaging.subscription import MessageHandlerFn, Subscription
from app.shared.application.ports.messaging.message_broker_port import MessageBrokerPort

if TYPE_CHECKING:
    from app.core.di.container import Container


# --- Публикация ---

<BC_NAME>_EVENTS_TOPIC = "<bc_name>.events"


def build_<bc_name>_event_bus(broker: MessageBrokerPort) -> DomainEventBus:
    """Создать DomainEventBus <BcName> BC."""
    return BrokerDomainEventBus(broker=broker, topic=<BC_NAME>_EVENTS_TOPIC)


# --- Подписки ---

<BC_NAME>_CONSUMER_GROUP = "<bc_name>-bc"


def <bc_name>_subscriptions(container: "Container") -> list[Subscription]:
    """Подписки <BcName> BC на топики других BC."""

    # Пример подписки на событие из другого BC:
    #
    # from app.context.<source_bc>.application.messaging import <SOURCE>_EVENTS_TOPIC
    # from app.context.<bc_name>.application.event_handlers.on_event_do import OnEventDo
    #
    # def _build_handler(session: AsyncSession) -> MessageHandlerFn:
    #     repo = container.<bc_name>_repo(session=session)
    #     handler = OnEventDo(repo=repo)
    #
    #     async def _run(message: dict[str, Any]) -> None:
    #         await handler.handle(message)
    #
    #     return _run
    #
    # return [
    #     Subscription(
    #         topic=<SOURCE>_EVENTS_TOPIC,
    #         group_id=<BC_NAME>_CONSUMER_GROUP,
    #         build_handler=_build_handler,
    #     ),
    # ]

    return []
```

### Реальный пример: Profile BC подписан на Identity BC

```python
# profile/application/messaging.py

from app.context.identity.application.messaging import IDENTITY_EVENTS_TOPIC

PROFILE_EVENTS_TOPIC = "profile.events"
PROFILE_CONSUMER_GROUP = "profile-bc"


def profile_subscriptions(container: "Container") -> list[Subscription]:
    def _build_on_user_registered(session: AsyncSession) -> MessageHandlerFn:
        profile_repo = container.profile_repo(session=session)
        handler = OnUserRegisteredCreateProfile(profile_repo=profile_repo)

        async def _run(message: dict[str, Any]) -> None:
            await handler.handle(message)

        return _run

    return [
        Subscription(
            topic=IDENTITY_EVENTS_TOPIC,
            group_id=PROFILE_CONSUMER_GROUP,
            build_handler=_build_on_user_registered,
        ),
    ]
```

### UoW: транзакционная обёртка

`subscribe_with_uow` оборачивает каждый входящий message в сессию БД с commit/rollback:

```
Message → AsyncSession → build_handler(session) → handler(message) → commit/rollback
```

---

## 13. Пакетные `__init__.py`

### `application/__init__.py`

```python
from app.context.<bc_name>.application import commands, dto, event_handlers, exceptions, ports, queries

__all__ = [
    "commands",
    "dto",
    "event_handlers",
    "exceptions",
    "ports",
    "queries",
]
```

### `commands/__init__.py`

Реэкспортирует **обе** пары — `Command` + `Handler`:

```python
from app.context.<bc_name>.application.commands.do_something import (
    DoSomethingCommand,
    DoSomethingHandler,
)

__all__ = [
    "DoSomethingCommand",
    "DoSomethingHandler",
]
```

### `queries/__init__.py`, `dto/__init__.py`, `event_handlers/__init__.py`, `exceptions/__init__.py`

Аналогично — полный реэкспорт всех публичных классов.

### `ports/__init__.py`

Реэкспортирует integration-порты и BC-специфичные порты:

```python
from app.context.<bc_name>.application.ports.integration import (
    SomeInboardPort,
    SomeOutboardProvider,
)
from app.context.<bc_name>.application.ports.<concern> import (
    SomeConcernPort,
)

__all__ = [
    "SomeConcernPort",
    "SomeInboardPort",
    "SomeOutboardProvider",
]
```

---

## 14. Чеклист нового BC

Для создания application layer нового Bounded Context `<bc_name>`:

- [ ] Создать `app/context/<bc_name>/application/` со структурой из раздела 2
- [ ] Определить Commands + Handlers — по одной паре на мутирующий use case, в `commands/`
- [ ] Определить Queries + Handlers — по одной паре на read use case, в `queries/`
- [ ] Определить DTO — результаты запросов и ответы handler'ов, в `dto/`
- [ ] Определить Event Handlers — реакции на события (свои и чужие BC), в `event_handlers/`
- [ ] Определить Application Exceptions — ошибки оркестрации, в `exceptions/`
- [ ] Определить Outboard-порты — данные, которые BC предоставляет другим, в `ports/integration/outboard/`
- [ ] Определить Inboard-порты — данные, которые BC потребляет от других, в `ports/integration/inboard/`
- [ ] При необходимости — определить BC-специфичные порты в `ports/<concern>/`
- [ ] Создать `messaging.py` — топик публикации + список подписок
- [ ] Написать `__init__.py` для каждого подпакета с полным реэкспортом
- [ ] Написать корневой `application/__init__.py`
- [ ] Убедиться, что application layer не импортирует из infrastructure или presentation
- [ ] Убедиться, что cross-BC event handler'ы не импортируют domain-типы чужого BC
