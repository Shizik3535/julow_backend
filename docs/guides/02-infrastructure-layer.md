# Гайд: Infrastructure Layer для Bounded Context

## Содержание

1. [Обзор](#1-обзор)
2. [Структура директорий](#2-структура-директорий)
3. [Базовые классы (shared infrastructure)](#3-базовые-классы-shared-infrastructure)
4. [ORM Model](#4-orm-model)
5. [Data Mapper](#5-data-mapper)
6. [Repository (реализация)](#6-repository-реализация)
7. [Integration Adapters](#7-integration-adapters)
8. [BC-специфичные адаптеры](#8-bc-специфичные-адаптеры)
9. [Shared-адаптеры инфраструктуры](#9-shared-адаптеры-инфраструктуры)
10. [DI: регистрация в контейнере](#10-di-регистрация-в-контейнере)
11. [Alembic: миграции](#11-alembic-миграции)
12. [Пакетные `__init__.py`](#12-пакетные-__init__py)
13. [Чеклист нового BC](#13-чеклист-нового-bc)

---

## 1. Обзор

Infrastructure Layer — реализация портов (интерфейсов), определённых в domain и application слоях. Содержит:

- **Persistence**: ORM-модели, Data Mapper'ы, SQLAlchemy-репозитории.
- **Integration**: адаптеры inter-BC портов (inboard и outboard).

Зависимости: infrastructure зависит от domain, application, `app.shared.infrastructure` и `app.core`. **Не** зависит от presentation.

Ключевой принцип — **Dependency Inversion**: domain и application определяют интерфейсы (порты), infrastructure реализует их (адаптеры). DI-контейнер (`app.core.di`) связывает всё воедино.

---

## 2. Структура директорий

```
app/context/<bc_name>/infrastructure/
├── __init__.py                         # Реэкспорт ключевых адаптеров
├── persistence/
│   ├── __init__.py                     # Реэкспорт mapper'ов, repo, orm
│   ├── orm_models/
│   │   ├── __init__.py                 # Реэкспорт всех ORM-классов
│   │   └── <aggregate>_orm.py          # ORM-модели для одного агрегата
│   ├── mappers/
│   │   ├── __init__.py                 # Реэкспорт всех mapper'ов
│   │   └── <aggregate>_mapper.py       # Data Mapper для одного агрегата
│   └── repositories/
│       ├── __init__.py                 # Реэкспорт всех репозиториев
│       └── sql_<aggregate>_repository.py  # Реализация RepositoryPort
├── integration/
│   ├── __init__.py                     # Реэкспорт всех inter-BC адаптеров
│   ├── inboard/                        # Адаптеры для портов, от которых МЫ зависим
│   │   ├── __init__.py
│   │   └── <source_bc>_<data>_adapter.py
│   └── outboard/                       # Адаптеры для портов, которые МЫ предоставляем
│       ├── __init__.py
│       └── <data>_provider_adapter.py
└── <concern>/                          # BC-специфичные адаптеры (по аналогии с shared kernel)
    ├── __init__.py                     # Реэкспорт адаптеров этого concern
    └── <concern>_adapter.py            # Реализация BC-специфичного порта
```

**Shared infrastructure** (`app/shared/infrastructure/`):

```
app/shared/infrastructure/
├── persistence/
│   ├── sqlalchemy_base_orm_model.py    # BaseORMModel (id, created_at, updated_at)
│   ├── sqlalchemy_base_mapper.py       # BaseMapper[TAggregate, TORMModel]
│   └── sqlalchemy_repository.py        # SqlAlchemyRepository, SoftDeleteSqlAlchemyRepository
├── auth/                               # Argon2PasswordAdapter, JwtAuthAdapter
├── cache/                              # RedisCacheAdapter
├── messaging/                          # KafkaMessageBrokerAdapter
├── file_storage/                       # S3FileStorageAdapter
├── notification/                       # SmtpEmailAdapter, NtfyPushAdapter
└── background_tasks/                   # CeleryBackgroundTasksAdapter
```

---

## 3. Базовые классы (shared infrastructure)

| Класс | Модуль | Назначение |
|---|---|---|
| `BaseORMModel` | `persistence/sqlalchemy_base_orm_model` | Базовая ORM: `id`, `created_at`, `updated_at` |
| `BaseMapper[T, M]` | `persistence/sqlalchemy_base_mapper` | ABC Data Mapper (Domain ↔ ORM) |
| `SqlAlchemyRepository[T, M]` | `persistence/sqlalchemy_repository` | Базовый async-репозиторий |
| `SoftDeleteSqlAlchemyRepository` | `persistence/sqlalchemy_repository` | + soft delete / restore |

### BaseORMModel

Все ORM-модели наследуются от `BaseORMModel`, которая является `DeclarativeBase` и даёт:

```python
class BaseORMModel(DeclarativeBase):
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=...)
```

- Единый `metadata` для Alembic autogenerate.
- UUID PK по умолчанию.
- Автоматические timestamp'ы.

### BaseMapper

```python
class BaseMapper(ABC, Generic[TAggregate, TORMModel]):
    @abstractmethod
    def to_domain(self, orm_model: TORMModel) -> TAggregate: ...
    @abstractmethod
    def to_orm(self, aggregate: TAggregate) -> TORMModel: ...

    def _map_id(self, value: uuid.UUID | str) -> Id: ...    # UUID → Id
    def _map_uuid(self, id: Id) -> uuid.UUID: ...            # Id → UUID
```

### SqlAlchemyRepository

Реализует `RepositoryPort[T]` — CRUD из одного класса:

| Метод | Назначение |
|---|---|
| `get_by_id(id)` | Поиск по PK |
| `get_all(offset, limit, filters)` | Список с фильтрацией |
| `get_paginated(page, page_size, filters)` | Пагинация + total |
| `add(aggregate)` | Вставка (flush) |
| `update(aggregate)` | Обновление всех колонок кроме id/created_at |
| `delete(id)` | Физическое удаление |

Конструктор: `session: AsyncSession`, `mapper: BaseMapper`, `orm_model_class: type[TORMModel]`.

---

## 4. ORM Model

ORM-модель — представление таблицы БД. **Не** является доменным объектом.

### Правила

- Наследуется от `BaseORMModel`.
- `__tablename__` — snake_case, множественное число: `users`, `sessions`, `user_profiles`.
- Типы колонок: `String`, `Boolean`, `Integer`, `DateTime(timezone=True)`, `JSON`, `Text`, `Float`.
- FK: `ForeignKey("<table>.id", ondelete="CASCADE")` + `index=True`.
- Все nullable-поля явно: `nullable=True` / `nullable=False`.
- Value Objects, встроенные в агрегат, «разворачиваются» в скалярные колонки (нет вложенных моделей).
- Дочерние коллекции (Entity) — через `relationship` с `cascade="all, delete-orphan"` и `lazy="selectin"`.
- Один файл ORM может содержать несколько связанных моделей (агрегат + его дочерние сущности).

### Шаблон: простой агрегат

```python
from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


class MyAggregateORM(BaseORMModel):
    """ORM-модель таблицы my_aggregates."""

    __tablename__ = "my_aggregates"

    user_id: Mapped[uuid.UUID] = mapped_column(
        nullable=False, unique=True, index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
```

### Шаблон: агрегат с дочерними сущностями

```python
class MyAggregateORM(BaseORMModel):
    __tablename__ = "my_aggregates"

    user_id: Mapped[uuid.UUID] = mapped_column(nullable=False, unique=True, index=True)
    # ... скалярные поля ...

    # Дочерние сущности
    items: Mapped[list[MyItemORM]] = relationship(
        back_populates="aggregate",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class MyItemORM(BaseORMModel):
    __tablename__ = "my_aggregate_items"

    aggregate_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("my_aggregates.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    # ... скалярные поля ...

    aggregate: Mapped[MyAggregateORM] = relationship(back_populates="items")
```

### Шаблон: Association Table (many-to-many)

```python
from sqlalchemy import Column, ForeignKey, Table

user_roles_table = Table(
    "user_roles",
    BaseORMModel.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)
```

### Паттерн: Embedded Value Objects → скалярные колонки

Доменный VO `AppearanceSettings(theme, accent_color, interface_density)` разворачивается в колонки корневой ORM:

```python
# UserProfileORM — колонки вместо вложенного VO
theme: Mapped[str] = mapped_column(String(30), nullable=False, default="system")
accent_color: Mapped[str] = mapped_column(String(30), nullable=False, default="#6366F1")
interface_density: Mapped[str] = mapped_column(String(30), nullable=False, default="comfortable")
```

---

## 5. Data Mapper

Data Mapper — двунаправленное преобразование Domain ↔ ORM. Изолирует доменную модель от структуры БД.

### Правила

- Наследуется от `BaseMapper[TAggregate, TORMModel]`.
- Один mapper = один агрегат.
- `to_domain()`: ORM → Aggregate (конструирует VO, Entity, восстанавливает коллекции).
- `to_orm()`: Aggregate → ORM (извлекает примитивы из VO, собирает дочерние ORM).
- Для дочерних Entity — приватные методы `_<entity>_to_orm()`, `_<entity>_orm_to_domain()`.
- Используйте `self._map_id()` / `self._map_uuid()` для Id ↔ UUID.

### Шаблон: простой mapper

```python
from __future__ import annotations

from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper
from app.context.<bc_name>.domain.aggregates.<aggregate> import MyAggregate
from app.context.<bc_name>.domain.value_objects.<vo> import MyStatus
from app.context.<bc_name>.infrastructure.persistence.orm_models.<aggregate>_orm import MyAggregateORM


class MyAggregateMapper(BaseMapper[MyAggregate, MyAggregateORM]):
    """Data Mapper: MyAggregate ↔ MyAggregateORM."""

    def to_domain(self, orm_model: MyAggregateORM) -> MyAggregate:
        return MyAggregate(
            id=self._map_id(orm_model.id),
            user_id=self._map_id(orm_model.user_id),
            name=orm_model.name,
            status=MyStatus(orm_model.status),
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: MyAggregate) -> MyAggregateORM:
        return MyAggregateORM(
            id=self._map_uuid(aggregate.id),
            user_id=self._map_uuid(aggregate.user_id),
            name=aggregate.name,
            status=aggregate.status.value,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
```

### Шаблон: mapper с дочерними сущностями

```python
class MyAggregateMapper(BaseMapper[MyAggregate, MyAggregateORM]):

    def to_domain(self, orm_model: MyAggregateORM) -> MyAggregate:
        items = [
            MyItem(
                id=self._map_id(item.id),
                name=item.name,
            )
            for item in orm_model.items
        ]

        return MyAggregate(
            id=self._map_id(orm_model.id),
            items=items,
            ...
        )

    def to_orm(self, aggregate: MyAggregate) -> MyAggregateORM:
        orm = MyAggregateORM(
            id=self._map_uuid(aggregate.id),
            ...
        )
        orm.items = [self._item_to_orm(i, aggregate.id) for i in aggregate.items]
        return orm

    def _item_to_orm(self, item: MyItem, aggregate_id: Id) -> MyItemORM:
        return MyItemORM(
            id=self._map_uuid(item.id),
            aggregate_id=self._map_uuid(aggregate_id),
            name=item.name,
        )
```

### Паттерн: маппинг Embedded VO → скалярные колонки

В `to_domain`: собрать VO из нескольких колонок ORM:
```python
appearance = AppearanceSettings(
    theme=Theme(orm_model.theme),
    accent_color=Color(orm_model.accent_color),
    interface_density=InterfaceDensity(orm_model.interface_density),
)
```

В `to_orm`: развернуть VO в скаляры:
```python
orm = UserProfileORM(
    theme=aggregate.appearance.theme.value,
    accent_color=str(aggregate.appearance.accent_color),
    interface_density=aggregate.appearance.interface_density.value,
)
```

---

## 6. Repository (реализация)

Конкретный репозиторий наследует одновременно `SqlAlchemyRepository` (реализация) и `<Aggregate>Repository` (доменный порт).

### Правила

- Двойное наследование: `SqlAlchemyRepository[T, M]` + доменный порт.
- Конструктор: `session: AsyncSession`, `mapper: <Mapper>`.
- Базовые CRUD-методы наследуются из `SqlAlchemyRepository`.
- Нужно реализовать **только специфичные** методы из доменного порта (`get_by_email`, `search`, `get_by_user_id`, ...).
- Все запросы через `select(ORM).where(...)`.
- Конвертация результатов через `self._mapper.to_domain()`.

### Шаблон: простой репозиторий

```python
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.id_vo import Id
from app.shared.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyRepository
from app.context.<bc_name>.domain.aggregates.<aggregate> import MyAggregate
from app.context.<bc_name>.domain.repositories.<aggregate>_repository import MyAggregateRepository
from app.context.<bc_name>.infrastructure.persistence.mappers.<aggregate>_mapper import MyAggregateMapper
from app.context.<bc_name>.infrastructure.persistence.orm_models.<aggregate>_orm import MyAggregateORM


class SqlMyAggregateRepository(SqlAlchemyRepository[MyAggregate, MyAggregateORM], MyAggregateRepository):
    """SQLAlchemy-реализация MyAggregateRepository."""

    def __init__(self, session: AsyncSession, mapper: MyAggregateMapper) -> None:
        super().__init__(session=session, mapper=mapper, orm_model_class=MyAggregateORM)

    async def get_by_user_id(self, user_id: Id) -> MyAggregate | None:
        uuid_val = self._mapper._map_uuid(user_id)
        stmt = select(MyAggregateORM).where(MyAggregateORM.user_id == uuid_val)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm else None

    async def search(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[MyAggregate]:
        stmt = select(MyAggregateORM)
        stmt = self._apply_filters(stmt, filters)
        stmt = stmt.offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return [self._mapper.to_domain(o) for o in result.scalars().all()]
```

### Паттерн: переопределение add/update для дочерних коллекций

Если агрегат содержит дочерние Entity (коллекции), нужно переопределить `add()` и `update()` для синхронизации:

```python
async def update(self, aggregate: MyAggregate) -> MyAggregate:
    """Обновляет агрегат с полной синхронизацией дочерних сущностей."""
    uuid_val = self._mapper._map_uuid(aggregate.id)
    stmt = select(MyAggregateORM).where(MyAggregateORM.id == uuid_val)
    result = await self._session.execute(stmt)
    orm_model = result.scalar_one_or_none()
    if orm_model is None:
        raise EntityNotFoundException(entity_type="MyAggregate", id=aggregate.id)

    # Обновить скалярные поля
    updated_orm = self._mapper.to_orm(aggregate)
    for column in MyAggregateORM.__table__.columns:
        col_name = column.name
        if col_name in ("id", "created_at"):
            continue
        setattr(orm_model, col_name, getattr(updated_orm, col_name, None))

    # Синхронизация дочерних: delete old + insert new
    await self._session.execute(
        MyItemORM.__table__.delete().where(MyItemORM.aggregate_id == uuid_val)
    )
    for item in updated_orm.items:
        item.aggregate_id = uuid_val
        self._session.add(item)

    await self._session.flush()
    return aggregate
```

### Паттерн: association table (many-to-many)

```python
async def add(self, aggregate: User) -> User:
    orm_model = self._mapper.to_orm(aggregate)
    self._session.add(orm_model)
    for role_id in aggregate.role_ids:
        await self._session.execute(
            user_roles_table.insert().values(user_id=orm_model.id, role_id=self._mapper._map_uuid(role_id))
        )
    await self._session.flush()
    return aggregate
```

---

## 7. Integration Adapters

Адаптеры реализуют inter-BC порты, определённые в application layer.

### Два направления

```
Identity BC                                    Profile BC
┌──────────────────────────────┐              ┌──────────────────────────────┐
│ application/ports/           │              │ application/ports/           │
│   outboard/                  │              │   inboard/                   │
│     IdentityUserProvider     │              │     IdentityUserPort         │
│     (ABC, возвращает DTO)    │              │     (ABC, возвращает dict)   │
│                              │              │                              │
│ infrastructure/integration/  │   DI-инъект  │ infrastructure/integration/  │
│   outboard/                  │ ◄──────────► │   inboard/                   │
│     UserProviderAdapter      │              │     IdentityUserAdapter      │
│     (impl → repo → DTO)     │              │     (impl → Provider → dict) │
└──────────────────────────────┘              └──────────────────────────────┘
```

### Outboard Adapter (мы предоставляем данные)

Реализует outboard-порт из своего BC. Делегирует в репозиторий и маппит в DTO.

```python
from app.context.<bc_name>.application.dto.<entity>_dto import MyEntityDTO
from app.context.<bc_name>.application.ports.integration.outboard.<provider> import MyEntityProvider
from app.context.<bc_name>.domain.repositories.<aggregate>_repository import MyAggregateRepository


class MyEntityProviderAdapter(MyEntityProvider):
    """Реализация MyEntityProvider (outboard)."""

    def __init__(self, repo: MyAggregateRepository) -> None:
        self._repo = repo

    async def get_entity(self, entity_id: str) -> MyEntityDTO | None:
        aggregate = await self._repo.get_by_id(Id.from_string(entity_id))
        if aggregate is None:
            return None
        return MyEntityDTO(
            id=str(aggregate.id),
            # ... маппинг ...
        )
```

### Inboard Adapter (мы потребляем данные)

Реализует inboard-порт своего BC. Принимает outboard-порт чужого BC через конструктор (DI). Маппит DTO чужого BC в `dict`.

```python
from typing import Any

from app.context.<source_bc>.application.ports.integration.outboard.<provider> import SourceProvider
from app.context.<bc_name>.application.ports.integration.inboard.<port> import SourcePort


class SourceAdapter(SourcePort):
    """Реализация SourcePort (inboard) — делегирует в SourceProvider из <Source> BC."""

    def __init__(self, source_provider: SourceProvider) -> None:
        self._provider = source_provider

    async def get_data(self, id: str) -> dict[str, Any] | None:
        dto = await self._provider.get_entity(id)
        if dto is None:
            return None
        return {
            "id": dto.id,
            "name": dto.name,
            # ... маппинг DTO → dict ...
        }
```

**Важно**: inboard-адаптер импортирует ABC outboard-порта из чужого BC (application слой), но **не** импортирует из infrastructure чужого BC. Связывание через DI.

### Реальный пример: Profile BC потребляет данные из Identity BC

```
IdentityUserProvider (ABC, identity/application)
       │
       ▼
UserProviderAdapter (identity/infrastructure)  ← реализация, работает с UserRepository
       │
       ▼  DI-инъекция
IdentityUserAdapter (profile/infrastructure)   ← inboard-адаптер, маппит DTO → dict
       │
       ▼
IdentityUserPort (ABC, profile/application)    ← порт, используемый use case'ами Profile BC
```

---

## 8. BC-специфичные адаптеры

Если BC определил собственные порты в `application/ports/<concern>/` (см. гайд 01-application-layer, раздел 10), их реализации размещаются в `infrastructure/<concern>/` — зеркально структуре shared kernel.

### Структура (зеркало shared kernel)

```
# Shared kernel (app/shared/infrastructure/)
app/shared/infrastructure/
├── auth/                               # Argon2PasswordAdapter, JwtAuthAdapter
├── cache/                              # RedisCacheAdapter
├── messaging/                          # KafkaMessageBrokerAdapter
├── file_storage/                       # S3FileStorageAdapter
├── notification/                       # SmtpEmailAdapter, NtfyPushAdapter
└── background_tasks/                   # CeleryBackgroundTasksAdapter

# BC-специфичные адаптеры (app/context/<bc_name>/infrastructure/)
app/context/<bc_name>/infrastructure/
├── persistence/                        # всегда есть
├── integration/                        # всегда есть
├── <concern>/                          # адаптер для ports/<concern>/
│   ├── __init__.py
│   └── <concern>_adapter.py
└── <another_concern>/
    ├── __init__.py
    └── <concern>_adapter.py
```

### Шаблон: BC-специфичный адаптер

```python
# <bc_name>/infrastructure/payment/stripe_payment_adapter.py

from __future__ import annotations

import stripe

from app.core.logging import get_logger
from app.context.<bc_name>.application.ports.payment.payment_gateway_port import (
    PaymentGatewayPort,
    PaymentResult,
)

logger = get_logger(__name__)


class StripePaymentAdapter(PaymentGatewayPort):
    """
    Реализация PaymentGatewayPort на основе Stripe API.
    """

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    async def charge(self, user_id: str, amount: float, currency: str) -> PaymentResult:
        # ... Stripe API call ...
        logger.info("Payment charged", user_id=user_id, amount=amount)
        return PaymentResult(transaction_id="...", status="succeeded", amount=amount)

    async def refund(self, transaction_id: str) -> bool:
        # ... Stripe API call ...
        logger.info("Payment refunded", transaction_id=transaction_id)
        return True
```

### Правила

- Имя папки `infrastructure/<concern>/` совпадает с именем папки `application/ports/<concern>/`.
- Адаптер импортирует ABC-порт из application, не наоборот.
- Регистрация в DI: фабричная функция в `app/core/di/providers/<bc_name>_provider.py`, регистрация в `Container`.
- Конфигурация (ключи API, URL) — через `app.core.config` (собственный `<concern>_settings.py` при необходимости).

---

## 9. Shared-адаптеры инфраструктуры

Расположены в `app/shared/infrastructure/`. Реализуют shared-порты из `app/shared/application/ports/`.

| Порт (application) | Адаптер (infrastructure) | Технология |
|---|---|---|
| `PasswordPort` | `Argon2PasswordAdapter` | passlib + argon2 |
| `AuthTokenPort` | `JwtAuthAdapter` | PyJWT |
| `MessageBrokerPort` | `KafkaMessageBrokerAdapter` | aiokafka |
| `CachePort` | `RedisCacheAdapter` | redis.asyncio |
| `FileStoragePort` | `S3FileStorageAdapter` | aiobotocore (S3) |
| `EmailPort` | `SmtpEmailAdapter` | aiosmtplib |
| `PushPort` | `NtfyPushAdapter` | ntfy (httpx) |
| `BackgroundTasksPort` | `CeleryBackgroundTasksAdapter` | Celery |

Эти адаптеры **не** специфичны для BC — переиспользуются всеми контекстами. Конфигурируются через `app.core.config` и регистрируются в DI-контейнере как `Singleton`.

---

## 10. DI: регистрация в контейнере

Новый BC необходимо зарегистрировать в DI-контейнере (`app/core/di/`).

### Provider-модуль (`app/core/di/providers/<bc_name>_provider.py`)

Для каждого BC создаётся отдельный provider-модуль с фабричными функциями:

```python
# app/core/di/providers/<bc_name>_provider.py

from sqlalchemy.ext.asyncio import AsyncSession

from app.context.<bc_name>.domain.repositories.<aggregate>_repository import MyAggregateRepository
from app.context.<bc_name>.infrastructure.persistence.mappers.<aggregate>_mapper import MyAggregateMapper
from app.context.<bc_name>.infrastructure.persistence.repositories.sql_<aggregate>_repository import (
    SqlMyAggregateRepository,
)


# --- Mappers ---

def create_<aggregate>_mapper() -> MyAggregateMapper:
    """Создать MyAggregateMapper."""
    return MyAggregateMapper()


# --- Repositories ---

def create_<aggregate>_repository(
    session: AsyncSession,
    mapper: MyAggregateMapper,
) -> MyAggregateRepository:
    """Создать SqlMyAggregateRepository."""
    return SqlMyAggregateRepository(session=session, mapper=mapper)


# --- Integration adapters ---

def create_outboard_provider(repo: MyAggregateRepository) -> MyEntityProvider:
    """Создать outboard-адаптер."""
    return MyEntityProviderAdapter(repo=repo)

def create_inboard_adapter(source_provider: SourceProvider) -> SourcePort:
    """Создать inboard-адаптер."""
    return SourceAdapter(source_provider=source_provider)
```

### Регистрация в Container (`app/core/di/container.py`)

```python
# В Container:

# <BcName> BC - Mappers (Singleton — без состояния)
<bc>_mapper = providers.Singleton(create_<aggregate>_mapper)

# <BcName> BC - Repositories (Factory — с session)
<bc>_repo = providers.Factory(
    create_<aggregate>_repository,
    session=db_session_factory,
    mapper=<bc>_mapper,
)

# <BcName> BC - Event Bus (Singleton)
<bc>_event_bus = providers.Singleton(
    build_<bc>_event_bus,
    broker=message_broker_port,
)

# <BcName> BC - Integration outboard (Factory)
<bc>_<entity>_provider = providers.Factory(
    create_outboard_provider,
    repo=<bc>_repo,
)

# <BcName> BC - Integration inboard (Factory)
<bc>_<source>_port = providers.Factory(
    create_inboard_adapter,
    source_provider=<source>_provider,
)
```

### Подписки — wire_messaging()

Добавить подписки нового BC в `wire_messaging()`:

```python
async def wire_messaging(container: Container) -> None:
    broker = container.message_broker_port()
    session_factory = container.db_session_factory()

    subscriptions: list[Subscription] = [
        *identity_subscriptions(container),
        *profile_subscriptions(container),
        *<bc_name>_subscriptions(container),  # ← добавить
    ]

    for sub in subscriptions:
        await subscribe_with_uow(broker, session_factory, sub)
```

### Паттерн DI: Mapper vs Repository

| Компонент | Lifetime | Почему |
|---|---|---|
| **Mapper** | `Singleton` | Без состояния, реентрантный |
| **Repository** | `Factory` | Содержит `AsyncSession`, per-request |
| **EventBus** | `Singleton` | Без состояния, привязан к топику |
| **Integration adapter** | `Factory` | Зависит от репозитория (Factory) |

---

## 11. Alembic: миграции

### Регистрация ORM-модели

Чтобы Alembic autogenerate видел таблицы нового BC, ORM-модели **должны быть импортированы** в `alembic/env.py`:

```python
# alembic/env.py

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel

# Existing imports
from app.context.identity.infrastructure.persistence.orm_models.user_orm import UserORM  # noqa: F401
from app.context.identity.infrastructure.persistence.orm_models.user_auth_orm import UserAuthORM  # noqa: F401
from app.context.identity.infrastructure.persistence.orm_models.session_orm import SessionORM  # noqa: F401
from app.context.identity.infrastructure.persistence.orm_models.role_orm import RoleORM  # noqa: F401
from app.context.profile.infrastructure.persistence.orm_models.user_profile_orm import UserProfileORM  # noqa: F401

# ← Добавить импорт ORM нового BC
from app.context.<bc_name>.infrastructure.persistence.orm_models.<aggregate>_orm import MyAggregateORM  # noqa: F401

target_metadata = BaseORMModel.metadata
```

- Импорт `noqa: F401` — нужен только для side-effect (регистрация в metadata).
- Все ORM наследуются от `BaseORMModel` → попадают в один `metadata` → autogenerate видит все таблицы.

### Генерация миграции

```bash
alembic revision --autogenerate -m "<bc_name>_initial"
```

### Файл миграции

Миграции лежат в `alembic/versions/` с автоматическим именем:

```
alembic/versions/
├── 2026_04_22_1118-fd6013d644ae_initial.py
└── 2026_04_22_1500-<hash>_<bc_name>_initial.py   # ← новая
```

---

## 12. Пакетные `__init__.py`

### `infrastructure/__init__.py`

```python
from app.context.<bc_name>.infrastructure import integration, persistence

__all__ = [
    "integration",
    "persistence",
]
```

Или с явным реэкспортом ключевых классов (как в Profile BC):

```python
from app.context.<bc_name>.infrastructure.integration import (
    SourceAdapter,
    MyEntityProviderAdapter,
)
from app.context.<bc_name>.infrastructure.persistence import (
    SqlMyAggregateRepository,
    MyAggregateMapper,
)

__all__ = [
    "SourceAdapter",
    "MyEntityProviderAdapter",
    "SqlMyAggregateRepository",
    "MyAggregateMapper",
]
```

### `persistence/__init__.py`

```python
from app.context.<bc_name>.infrastructure.persistence.mappers import MyAggregateMapper
from app.context.<bc_name>.infrastructure.persistence.repositories import SqlMyAggregateRepository

__all__ = [
    "MyAggregateMapper",
    "SqlMyAggregateRepository",
]
```

### `persistence/orm_models/__init__.py`, `persistence/mappers/__init__.py`, `persistence/repositories/__init__.py`

По аналогии — полный реэкспорт всех классов.

### `integration/__init__.py`

```python
from app.context.<bc_name>.infrastructure.integration.inboard import SourceAdapter
from app.context.<bc_name>.infrastructure.integration.outboard import MyEntityProviderAdapter

__all__ = [
    "SourceAdapter",
    "MyEntityProviderAdapter",
]
```

---

## 13. Чеклист нового BC

Для создания infrastructure layer нового Bounded Context `<bc_name>`:

### Persistence

- [ ] Создать `infrastructure/persistence/orm_models/` — ORM-модель для каждого агрегата
- [ ] Если агрегат имеет дочерние Entity — ORM-модели в том же файле с `relationship`
- [ ] Создать `infrastructure/persistence/mappers/` — Data Mapper для каждого агрегата
- [ ] Создать `infrastructure/persistence/repositories/` — SQLAlchemy-репозиторий для каждого агрегата
- [ ] Реализовать только специфичные методы доменного порта (базовые CRUD наследуются)

### Integration

- [ ] Если BC предоставляет данные другим BC — создать outboard-адаптеры в `integration/outboard/`
- [ ] Если BC потребляет данные от других BC — создать inboard-адаптеры в `integration/inboard/`

### BC-специфичные адаптеры

- [ ] Если BC имеет собственные порты в `application/ports/<concern>/` — создать адаптеры в `infrastructure/<concern>/`
- [ ] Имя папки зеркалит concern из application/ports
- [ ] Зарегистрировать адаптер в DI-контейнере

### DI

- [ ] Создать `app/core/di/providers/<bc_name>_provider.py` с фабричными функциями
- [ ] Зарегистрировать mapper'ы, репозитории, адаптеры в `Container`
- [ ] Зарегистрировать `DomainEventBus` для нового BC
- [ ] Добавить подписки нового BC в `wire_messaging()`
- [ ] Импортировать фабричные функции в `app/core/di/providers/__init__.py`

### Alembic

- [ ] Добавить import ORM-модели в `alembic/env.py` (noqa: F401)
- [ ] Сгенерировать миграцию: `alembic revision --autogenerate -m "<bc_name>_initial"`
- [ ] Проверить сгенерированную миграцию

### `__init__.py`

- [ ] Написать `__init__.py` для каждого подпакета с полным реэкспортом
- [ ] Написать корневой `infrastructure/__init__.py`
