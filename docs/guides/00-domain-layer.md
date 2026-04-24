# Гайд: Domain Layer для Bounded Context

## Содержание

1. [Обзор](#1-обзор)
2. [Структура директорий](#2-структура-директорий)
3. [Базовые классы (shared kernel)](#3-базовые-классы-shared-kernel)
4. [Aggregate Root](#4-aggregate-root)
5. [Entity](#5-entity)
6. [Value Object](#6-value-object)
7. [Domain Event](#7-domain-event)
8. [Domain Exception](#8-domain-exception)
9. [Repository Port](#9-repository-port)
10. [Пакетные `__init__.py`](#10-пакетные-__init__py)
11. [Взаимодействие между BC](#11-взаимодействие-между-bc)
12. [Чеклист нового BC](#12-чеклист-нового-bc)

---

## 1. Обзор

Domain Layer — ядро Bounded Context. Содержит бизнес-логику, инварианты и доменные модели. **Не зависит** от инфраструктуры, фреймворков и внешних библиотек (кроме стандартной библиотеки Python и `app.shared.domain`).

Слой строится из шести пакетов: `aggregates`, `entities`, `value_objects`, `events`, `exceptions`, `repositories`.

---

## 2. Структура директорий

```
app/context/<bc_name>/domain/
├── __init__.py               # Реэкспорт подпакетов
├── aggregates/
│   ├── __init__.py           # Реэкспорт всех AR
│   └── <aggregate>.py        # Один файл — один Aggregate Root
├── entities/
│   ├── __init__.py           # Реэкспорт всех Entity
│   └── <entity>.py           # Один файл — одна Entity
├── value_objects/
│   ├── __init__.py           # Реэкспорт всех VO
│   └── <value_object>.py     # Один файл — один Value Object
├── events/
│   ├── __init__.py           # Реэкспорт всех событий
│   └── <aggregate>_events.py # Группировка событий по агрегату
├── exceptions/
│   ├── __init__.py           # Реэкспорт всех исключений
│   └── <aggregate>_exceptions.py  # Группировка по агрегату
└── repositories/
    ├── __init__.py           # Реэкспорт всех портов
    └── <aggregate>_repository.py  # Один порт — один AR
```

**Примеры из проекта:**

- Identity BC: `app/context/identity/domain/` — 4 агрегата (`User`, `UserAuth`, `Session`, `Role`), 6 сущностей, 15 VO, 3 группы событий, 3 группы исключений, 4 репозитория.
- Profile BC: `app/context/profile/domain/` — 1 агрегат (`UserProfile`), 2 сущности, 23 VO, 1 группа событий, 1 группа исключений, 1 репозиторий.

---

## 3. Базовые классы (shared kernel)

Все доменные примитивы наследуются от базовых классов из `app.shared.domain`:

| Базовый класс | Назначение | Импорт |
|---|---|---|
| `AggregateRoot` | Корень агрегата (с событиями) | `app.shared.domain.base_aggregate` |
| `BaseEntity` | Сущность с идентичностью (Id) | `app.shared.domain.base_entity` |
| `ValueObject` | Неизменяемый объект-значение | `app.shared.domain.base_value_object` |
| `BaseDomainEvent` | Доменное событие | `app.shared.domain.base_domain_event` |
| `DomainException` | Базовое доменное исключение | `app.shared.domain.base_exceptions` |
| `RepositoryPort[T]` | Порт репозитория (Generic) | `app.shared.domain.base_repository` |

**Shared Value Objects** (переиспользуются между BC): `Id`, `Email`, `Url`, `IpAddress`, `Color`, `DateRange`, `LanguageCode`, `Money`, `Percent`, `Timezone`.

**Shared Exceptions**: `EntityNotFoundException`, `BusinessRuleViolationException`, `ValidationException`.

---

## 4. Aggregate Root

Aggregate Root — точка входа и граница консистентности. Все изменения внутренних объектов проходят через AR.

### Правила

- Наследуется от `AggregateRoot` (→ `BaseEntity` → имеет `id: Id`).
- Декоратор `@dataclass`.
- Содержит **фабричный `@classmethod`** для создания (вместо голого `__init__`).
- Вся бизнес-логика — в методах AR.
- Регистрирует доменные события через `self._register_event(...)`.
- Обновляет `updated_at` при каждой мутации.
- Проверяет инварианты перед изменением состояния.

### Шаблон

```python
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id


@dataclass
class MyAggregate(AggregateRoot):
    """
    Корень агрегата ... (<BC_Name> BC).

    Атрибуты:
        user_id: Opaque ID из Identity BC (если привязан к пользователю).
        ...
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    user_id: Id = field(default_factory=Id.generate)
    # ... доменные атрибуты ...
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    # --- Фабричный метод ---

    @classmethod
    def create(cls, user_id: Id, ...) -> MyAggregate:
        """Создаёт агрегат с настройками по умолчанию."""
        aggregate = cls(user_id=user_id, ...)
        aggregate._register_event(
            MyAggregateCreated(user_id=str(user_id))
        )
        return aggregate

    # --- Бизнес-методы ---

    def do_something(self, ...) -> None:
        """Выполняет бизнес-операцию."""
        self._assert_some_invariant()
        # ... мутация ...
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(SomethingDone(...))

    # --- Приватные методы ---

    def _assert_some_invariant(self) -> None:
        """Проверяет инвариант."""
        if <condition>:
            raise SomeBusinessException()
```

### Реальные примеры

**Простой AR** — `Role` (Identity BC): только атрибуты, без бизнес-логики и событий.

**Средний AR** — `UserProfile` (Profile BC): фабричный метод, VO-группы настроек, коллекции сущностей, инварианты уникальности.

**Сложный AR** — `UserAuth` (Identity BC): множество фабричных методов, коллекции сущностей (2FA-факторы, OAuth-ссылки, доверенные устройства), политики блокировки, верификации.

### Паттерн: VO-группы настроек (Profile BC)

Когда AR имеет много связанных настроек, они группируются в composite VO:

```python
# В агрегате — одно поле:
appearance: AppearanceSettings = field(default_factory=AppearanceSettings)

# Метод заменяет всю группу целиком:
def update_appearance(self, settings: AppearanceSettings) -> None:
    changed = _changed_fields(self.appearance, settings)
    self.appearance = settings
    self.updated_at = datetime.now(tz=timezone.utc)
    if changed:
        self._register_event(
            AppearanceSettingsChanged(
                user_id=str(self.user_id),
                changed_fields=changed,
            )
        )
```

Преимущество: добавление новой настройки = новое поле в VO, а не новый метод на AR.

---

## 5. Entity

Entity — объект с идентичностью, принадлежащий агрегату. Загружается и сохраняется **только** через свой Aggregate Root.

### Правила

- Наследуется от `BaseEntity` (имеет `id: Id`).
- Декоратор `@dataclass` (мутабельный, **не** `frozen`).
- Минимум логики — только то, что касается самой сущности.
- Никогда не регистрирует доменные события (это делает AR).
- AR управляет коллекцией сущностей и обеспечивает инварианты.

### Шаблон

```python
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity


@dataclass
class MyEntity(BaseEntity):
    """
    Сущность ... .

    Принадлежит агрегату <AggregateName>.

    Атрибуты:
        ...
    """

    some_field: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
```

### Примеры

- `AuthFactor` (Identity BC) — имеет методы `enable()` / `disable()`, вызываемые из `UserAuth`.
- `SocialLink` (Profile BC) — чистый data-holder, логика управления в `UserProfile`.
- `PinnedItem` (Profile BC) — содержит `target_id: Id` (opaque ID из другого BC).
- `LoginAttempt` (Identity BC) — вычисляемое поле в `__post_init__`.

---

## 6. Value Object

Value Object — неизменяемый объект, определяемый значением, а не идентичностью.

### Виды VO

| Вид | Пример | Описание |
|---|---|---|
| **Enum VO** | `AccountStatus`, `Theme`, `SessionStatus` | Перечисление допустимых значений |
| **Simple VO** | `PasswordHash`, `RefreshToken` | Обёртка над примитивом с валидацией |
| **Composite VO** | `AppearanceSettings`, `NotificationSettings` | Группа связанных настроек |
| **Policy VO** | `PasswordPolicy`, `FailedLoginPolicy` | Конфигурация бизнес-правил |

### Правила

- Enum VO: наследуется от `Enum`.
- Остальные: наследуются от `ValueObject`, декоратор `@dataclass(frozen=True)`.
- Валидация — в `__post_init__`, бросает `ValidationException`.
- **Не** содержит бизнес-логику агрегата.

### Шаблон: Enum VO

```python
from __future__ import annotations

from enum import Enum


class MyStatus(Enum):
    """
    Статус ...

    Значения:
        ACTIVE: ...
        DISABLED: ...
    """

    ACTIVE = "active"
    DISABLED = "disabled"
```

### Шаблон: Simple VO с валидацией

```python
from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class MyValue(ValueObject):
    """
    Value Object для ...

    Атрибуты:
        value: ...
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValidationException(
                field="my_value",
                message="Значение не может быть пустым",
            )
```

### Шаблон: Composite VO

```python
from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject


@dataclass(frozen=True)
class MySettingsGroup(ValueObject):
    """
    Группа настроек ...

    Атрибуты:
        setting_a: ...
        setting_b: ...
    """

    setting_a: str = "default_a"
    setting_b: bool = True
```

---

## 7. Domain Event

Доменное событие фиксирует значимый факт в домене. Используется для:
- Коммуникации между агрегатами внутри BC.
- Коммуникации между Bounded Context'ами.
- Побочных эффектов (уведомления, аудит).

### Правила

- Наследуется от `BaseDomainEvent`.
- Декоратор `@dataclass(frozen=True)` — событие неизменяемо.
- Имя — **в прошедшем времени**: `UserRegistered`, `ProfileCreated`, `SessionTerminated`.
- Группировка: один файл = события одного агрегата (`user_events.py`, `session_events.py`).
- Поля — примитивы (`str`, `int`, `bool`) или Enum. **Не** доменные объекты.
- Поля `event_id`, `aggregate_id`, `aggregate_type`, `occurred_at`, `event_type` наследуются от базового класса автоматически.

### Шаблон

```python
from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_domain_event import BaseDomainEvent


@dataclass(frozen=True)
class SomethingHappened(BaseDomainEvent):
    """Описание того, что произошло."""

    user_id: str = ""
    # ... payload — только примитивы ...


@dataclass(frozen=True)
class SomethingElseHappened(BaseDomainEvent):
    """Описание."""

    user_id: str = ""
    changed_fields: list[str] = field(default_factory=list)
```

### Важно: payload событий для межконтекстного взаимодействия

Если событие будет обрабатываться другим BC, payload должен содержать **всё необходимое** для обработки. Другой BC не должен ходить в репозитории исходного BC.

Пример: `UserRegistered` содержит `user_id` и `email` — Profile BC использует `user_id` для создания профиля.

---

## 8. Domain Exception

Доменные исключения делятся на три категории:

| Тип | Базовый класс | Когда использовать |
|---|---|---|
| **Not Found** | `EntityNotFoundException` | Агрегат/сущность не найдена |
| **Business Rule** | `BusinessRuleViolationException` | Нарушен инвариант |
| **Validation** | `ValidationException` | Невалидное значение |
| **General Domain** | `DomainException` | Остальные доменные ошибки |

### Правила

- Группировка: один файл = исключения одного агрегата.
- Каждое исключение — отдельный класс с говорящим именем.
- `EntityNotFoundException`: принимает `entity_type` и `id`.
- `BusinessRuleViolationException`: принимает `rule` (имя правила) и `message`.
- `ValidationException`: принимает `field` и `message`.

### Шаблоны

```python
from __future__ import annotations

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import (
    BusinessRuleViolationException,
    EntityNotFoundException,
    ValidationException,
)


class MyAggregateNotFoundException(EntityNotFoundException):
    """Агрегат не найден."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="MyAggregate", id=id)


class DuplicateItemException(BusinessRuleViolationException):
    """Элемент уже существует."""

    def __init__(self, item_id: str) -> None:
        super().__init__(
            rule="UniqueItem",
            message=f"Элемент {item_id} уже существует",
        )


class InvalidFormatException(ValidationException):
    """Некорректный формат."""

    def __init__(self, value: str) -> None:
        super().__init__(
            field="my_field",
            message=f"Некорректный формат: {value}",
        )
        self.value = value


class SomeSpecificException(DomainException):
    """Описание специфичной ошибки."""

    def __init__(self) -> None:
        super().__init__("Описание ошибки")
```

---

## 9. Repository Port

Repository Port — абстрактный интерфейс доступа к хранилищу агрегата. Определяется в domain layer, реализуется в infrastructure layer.

### Правила

- Наследуется от `RepositoryPort[TAggregate]` (или `SoftDeleteRepositoryPort[TAggregate]` для soft-delete).
- Один репозиторий = один Aggregate Root.
- Базовые методы уже определены: `get_by_id`, `get_all`, `get_paginated`, `add`, `update`, `delete`.
- В порт добавляются **только специфичные для BC** методы поиска.
- Все методы — `async` и `abstractmethod`.

### Шаблон

```python
from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.<bc_name>.domain.aggregates.<aggregate> import MyAggregate


class MyAggregateRepository(RepositoryPort[MyAggregate]):
    """
    Порт репозитория для агрегата MyAggregate.

    Расширяет базовый RepositoryPort специфичными запросами
    для <BC_Name> BC.
    """

    @abstractmethod
    async def get_by_user_id(self, user_id: Id) -> MyAggregate | None:
        """Найти агрегат по user_id (opaque ID из Identity BC)."""

    @abstractmethod
    async def search(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[MyAggregate]:
        """Поиск агрегатов с фильтрацией."""
```

---

## 10. Пакетные `__init__.py`

Каждый подпакет domain layer имеет `__init__.py` с реэкспортом всех публичных символов.

### `domain/__init__.py`

```python
from app.context.<bc_name>.domain import aggregates, entities, events, exceptions, repositories, value_objects

__all__ = [
    "aggregates",
    "entities",
    "events",
    "exceptions",
    "repositories",
    "value_objects",
]
```

### `domain/aggregates/__init__.py`

```python
from app.context.<bc_name>.domain.aggregates.<aggregate> import MyAggregate

__all__ = [
    "MyAggregate",
]
```

Аналогично для `entities/`, `events/`, `exceptions/`, `repositories/`, `value_objects/` — перечисляются **все** публичные классы пакета.

---

## 11. Взаимодействие между BC

### Принцип: Bounded Context'ы изолированы

BC **никогда** не импортирует доменные объекты другого BC напрямую. Связь между контекстами — через доменные события и opaque ID.

### Opaque ID

Если агрегат ссылается на сущность из другого BC, он хранит только `Id` — без знания о типе:

```python
# Profile BC ссылается на пользователя из Identity BC
user_id: Id = field(default_factory=Id.generate)  # opaque, не User
```

```python
# PinnedItem ссылается на объект из любого BC
target_id: Id = field(default_factory=Id.generate)  # opaque
target_type: PinnedTargetType = PinnedTargetType.TASK  # enum-маркер
```

### Доменные события: межконтекстное взаимодействие

Основной механизм связи — **доменные события**. BC-источник порождает событие, BC-потребитель подписывается на него через event handler в application layer.

**Пример: Identity → Profile**

1. `User.register()` в Identity BC регистрирует событие `UserRegistered`.
2. После сохранения агрегата события публикуются в топик `identity.events`.
3. `OnUserRegisteredCreateProfile` в Profile BC подписан на этот топик.
4. Handler получает событие, извлекает `user_id` из payload и создаёт `UserProfile`.

```
Identity BC                          Profile BC
┌──────────────────────┐             ┌──────────────────────────────────┐
│ User.register()      │             │ OnUserRegisteredCreateProfile    │
│  → UserRegistered    │──event──→   │  → UserProfile.create(user_id)  │
│    { user_id, email }│             │  → profile_repo.add(profile)    │
└──────────────────────┘             └──────────────────────────────────┘
```

### Event Handler: межконтекстный (cross-BC)

Обработчик события из другого BC находится в `application/event_handlers/` потребляющего BC:

```python
from app.shared.application.base_event_handler import BaseEventHandler

class OnUserRegisteredCreateProfile(BaseEventHandler[dict[str, Any]]):
    """
    Обработчик события UserRegistered из Identity BC.
    Подписывается на топик «identity.events».
    """

    def __init__(self, profile_repo: UserProfileRepository) -> None:
        super().__init__()
        self._profile_repo = profile_repo

    async def handle(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type")
        if event_type != "UserRegistered":
            return

        payload = event.get("payload", {})
        user_id_str = payload.get("user_id")
        if not user_id_str:
            return

        user_id = Id.from_string(user_id_str)

        # Идемпотентность: проверяем, не создан ли уже профиль
        existing = await self._profile_repo.get_by_user_id(user_id)
        if existing is not None:
            return

        profile = UserProfile.create(user_id=user_id)
        await self._profile_repo.add(profile)
```

**Ключевые принципы:**

- Тип события — `dict[str, Any]` (десериализованный JSON), а не доменный класс из чужого BC.
- **Идемпотентность** — handler проверяет, не обработано ли событие ранее.
- Handler не импортирует ничего из domain layer источника.

### Event Handler: внутриконтекстный (intra-BC)

Обработчик событий внутри одного BC может типизировать событие напрямую:

```python
class OnUserLoggedInCreateSession(BaseEventHandler[UserLoggedIn]):
    """Межагрегатное взаимодействие внутри Identity BC: UserAuth → Session."""

    async def handle(self, event: UserLoggedIn) -> None:
        session = Session.create(
            user_id=Id.from_string(event.user_id),
            device_info=DeviceInfo(user_agent=event.device),
            ip_address=IpAddress(event.ip),
        )
        await self._session_repo.add(session)
```

### Сводка: что можно и что нельзя

| Действие | Можно? |
|---|---|
| Импортировать `app.shared.domain.*` | ✅ |
| Импортировать domain-объекты **своего** BC | ✅ |
| Импортировать domain-объекты **чужого** BC | ❌ |
| Ссылаться на чужой агрегат по `Id` (opaque) | ✅ |
| Подписаться на событие чужого BC (через `dict`) | ✅ |
| Типизировать событие классом из чужого BC | ❌ |
| Обращаться к репозиторию чужого BC | ❌ |

---

## 12. Чеклист нового BC

Для создания domain layer нового Bounded Context `<bc_name>`:

- [ ] Создать `app/context/<bc_name>/domain/` со структурой из раздела 2
- [ ] Определить Aggregate Root'ы — каждый в своём файле в `aggregates/`
- [ ] Определить Entity — элементы коллекций агрегатов, в `entities/`
- [ ] Определить Value Objects — enum'ы, simple VO, composite VO, в `value_objects/`
- [ ] Определить Domain Events — сгруппировать по агрегатам, в `events/`
- [ ] Определить Domain Exceptions — сгруппировать по агрегатам, в `exceptions/`
- [ ] Определить Repository Ports — один порт на каждый AR, в `repositories/`
- [ ] Написать `__init__.py` для каждого подпакета с полным реэкспортом
- [ ] Написать корневой `domain/__init__.py`
- [ ] Если BC реагирует на события другого BC — создать event handler в `application/event_handlers/`
- [ ] Убедиться, что domain layer не импортирует ничего кроме `app.shared.domain` и собственных модулей
