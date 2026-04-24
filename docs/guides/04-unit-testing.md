# Гайд: Unit-тестирование Domain Layer

## Содержание

1. [Обзор](#1-обзор)
2. [Структура директорий](#2-структура-директорий)
3. [Конфигурация pytest](#3-конфигурация-pytest)
4. [Фабрики (`tests/factories.py`)](#4-фабрики-testsfactoriespy)
5. [Conftest: фикстуры BC](#5-conftest-фикстуры-bc)
6. [Тестирование Aggregate Root](#6-тестирование-aggregate-root)
7. [Тестирование Entity](#7-тестирование-entity)
8. [Тестирование Value Object](#8-тестирование-value-object)
9. [Тестирование Domain Exception](#9-тестирование-domain-exception)
10. [Конвенции и антипаттерны](#10-конвенции-и-антипаттерны)
11. [Чеклист нового BC](#11-чеклист-нового-bc)

---

## 1. Обзор

Unit-тесты domain layer проверяют бизнес-логику в изоляции — без БД, сети и внешних сервисов. Тестируем **чистый домен**: агрегаты, сущности, Value Objects, доменные исключения и события.

### Принципы

- **Без моков**: domain layer не имеет зависимостей от инфраструктуры — моки не нужны.
- **Быстрые**: каждый тест — миллисекунды, вся suite — секунды.
- **Изолированные**: тест не зависит от порядка выполнения или состояния других тестов.
- **Читаемые**: имя теста описывает поведение, тело следует паттерну **Arrange → Act → Assert**.
- **Маркер `@pytest.mark.unit`**: обязателен для каждого тест-класса.

### Что тестируем

| Компонент | Что проверяем |
|---|---|
| **Aggregate Root** | Фабричные методы, бизнес-методы, инварианты, доменные события |
| **Entity** | Создание, методы, equality by id |
| **Value Object** | Валидация, immutability (frozen), equality by value, `clone()`, `__str__` |
| **Domain Exception** | Иерархия наследования, атрибуты (`message`, `field`, `rule`) |

---

## 2. Структура директорий

Тестовая структура **зеркалит** domain layer Bounded Context'а:

```
tests/unit/
├── __init__.py
├── conftest.py                          # autouse _unit_marker
├── test_shared_domain.py                # Тесты shared kernel (Id, Email, etc.)
├── <bc_name>/
│   ├── __init__.py
│   ├── conftest.py                      # BC-level фикстуры (агрегаты, VO)
│   ├── aggregates/
│   │   ├── __init__.py
│   │   └── test_<aggregate>.py          # Один файл — один агрегат
│   ├── entities/
│   │   ├── __init__.py
│   │   └── test_<entity>.py             # Один файл — одна сущность
│   ├── value_objects/
│   │   ├── __init__.py
│   │   └── test_<value_object>.py       # Один файл — один VO
│   └── exceptions/
│       ├── __init__.py
│       └── test_<aggregate>_exceptions.py  # Группа по агрегату
```

**Примеры из проекта:**

- Identity BC: `tests/unit/identity/` — 4 файла агрегатов, 6 файлов сущностей, 3 файла исключений.
- Profile BC: `tests/unit/profile/` — 1 файл агрегата, 2 файла сущностей, 15+ файлов VO, 1 файл исключений.

### Правило зеркала

| Domain layer | Unit tests |
|---|---|
| `app/context/<bc>/domain/aggregates/user.py` | `tests/unit/<bc>/aggregates/test_user.py` |
| `app/context/<bc>/domain/entities/auth_factor.py` | `tests/unit/<bc>/entities/test_auth_factor.py` |
| `app/context/<bc>/domain/value_objects/theme.py` | `tests/unit/<bc>/value_objects/test_theme.py` |
| `app/context/<bc>/domain/exceptions/user_exceptions.py` | `tests/unit/<bc>/exceptions/test_user_exceptions.py` |

---

## 3. Конфигурация pytest

### Маркеры (`pyproject.toml`)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
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
pytest -m unit                # все unit-тесты
pytest tests/unit             # по директории
pytest tests/unit/identity    # один BC
pytest tests/unit/identity/aggregates/test_user.py  # один файл
pytest tests/unit/identity/aggregates/test_user.py::TestUserRoles  # один класс
pytest tests/unit/identity/aggregates/test_user.py::TestUserRoles::test_assign_role  # один тест
```

### Глобальный conftest (`tests/conftest.py`)

Загружается pytest автоматически для **всех** типов тестов. Содержит:

- Установку тестового окружения (`APP_ENV=test`).
- Хелпер `make_id()` и фикстуру `any_id`.
- Фикстуру `anyio_backend` для asyncio.

```python
import os
import uuid

import pytest

from app.shared.domain.value_objects.id_vo import Id

os.environ["APP_ENV"] = "test"
os.environ["APP_DEBUG"] = "true"
os.environ["DB_NAME"] = "julow_test"


def make_id() -> Id:
    """Создать случайный Id."""
    return Id(value=uuid.uuid4())


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
def any_id() -> Id:
    return make_id()
```

### Unit conftest (`tests/unit/conftest.py`)

Содержит autouse-фикстуру, которая пропускает тесты без маркера `unit`:

```python
"""
Unit test conftest — фикстуры для unit-тестов.

Unit-тесты не зависят от внешних сервисов.
Все зависимости мокируются через pytest-mock.
"""

import pytest


@pytest.fixture(autouse=True)
def _unit_marker(request):
    """Проверяет, что тест помечен как unit."""
    if not request.node.get_closest_marker("unit"):
        pytest.skip("Test not marked as unit")
```

**Важно**: если забыть `@pytest.mark.unit` на тест-классе, тест будет пропущен, а не молча проигнорирован.

---

## 4. Фабрики (`tests/factories.py`)

Фабрики генерируют тестовые данные с помощью `factory_boy`. Используются в conftest-фикстурах и напрямую в тестах.

### Правила

- Фабрики для **shared VO** (Id, Email) — в корне `tests/factories.py`.
- Фабрики для **BC-специфичных VO** (PasswordHash, RefreshToken) — там же, сгруппированы по BC.
- Фабрика возвращает **доменный объект**, а не примитив.
- Вызов фабрики — как вызов функции: `IdFactory()`, `EmailFactory()`.

### Шаблон: shared-фабрика

```python
import factory
from uuid import uuid4

from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.email_vo import Email


class IdFactory(factory.Factory):
    """Фабрика для генерации доменных Id."""

    class Meta:
        model = Id

    value = factory.LazyFunction(uuid4)


class EmailFactory(factory.Factory):
    """Фабрика для генерации доменных Email."""

    class Meta:
        model = Email

    value = factory.Sequence(lambda n: f"user{n}@example.com")
```

### Шаблон: BC-специфичная фабрика

```python
from app.context.identity.domain.value_objects.password_hash import PasswordHash
from app.context.identity.domain.value_objects.refresh_token import RefreshToken


class PasswordHashFactory(factory.Factory):
    """Фабрика для генерации PasswordHash."""

    class Meta:
        model = PasswordHash

    value = factory.LazyFunction(lambda: f"$2b$12${uuid4().hex[:53]}")


class RefreshTokenFactory(factory.Factory):
    """Фабрика для генерации RefreshToken."""

    class Meta:
        model = RefreshToken

    value = factory.LazyFunction(lambda: uuid4().hex)
```

### Когда фабрика, а когда `pytest.fixture`?

| Ситуация | Решение |
|---|---|
| Нужен **случайный** VO в любом месте | Фабрика: `IdFactory()` |
| Нужен **переиспользуемый** объект в нескольких тестах модуля | Фикстура в conftest: `any_email` |
| Нужен **агрегат в определённом состоянии** | Фикстура-цепочка: `pending_user` → `active_user` |

---

## 5. Conftest: фикстуры BC

Каждый BC имеет свой `conftest.py` в `tests/unit/<bc_name>/`. Содержит фикстуры для переиспользования между тестовыми модулями.

### Структура BC conftest

```python
"""
<BcName> BC conftest — фикстуры для unit-тестов <BcName> BC.

Содержит фабричные фикстуры для агрегатов, VOs и политик,
используемых в нескольких тестовых модулях.
"""

import pytest

# 1. Импорт VO и агрегатов
# 2. Импорт фабрик

# ── Value Object фикстуры ─────────────────────────────────────────────────

@pytest.fixture
def any_<vo>() -> <VoType>:
    """Описание."""
    return <VoType>(...)

# ── Политики ──────────────────────────────────────────────────────────────

@pytest.fixture
def default_<policy>() -> <PolicyType>:
    """Описание."""
    return <PolicyType>(...)

# ── Агрегат <Name> ───────────────────────────────────────────────────────

@pytest.fixture
def <initial_state_aggregate>() -> <Aggregate>:
    """Агрегат в начальном состоянии."""
    return <Aggregate>.create(...)

@pytest.fixture
def <derived_state_aggregate>(<initial_state_aggregate>) -> <Aggregate>:
    """Агрегат в производном состоянии (после операции X)."""
    <initial_state_aggregate>.do_x()
    <initial_state_aggregate>.clear_domain_events()
    return <initial_state_aggregate>
```

### Реальный пример: Identity BC

```python
@pytest.fixture
def any_email() -> Email:
    """Случайный Email."""
    return EmailFactory()


@pytest.fixture
def any_password_hash() -> PasswordHash:
    """Случайный PasswordHash."""
    return PasswordHashFactory()


@pytest.fixture
def default_lockout_policy() -> FailedLoginPolicy:
    """Политика блокировки: 3 попытки → 15 мин, 5 попыток → 60 мин."""
    return FailedLoginPolicy(thresholds=[
        LockoutThreshold(failed_attempts=3, lock_duration_minutes=15),
        LockoutThreshold(failed_attempts=5, lock_duration_minutes=60),
    ])


@pytest.fixture
def pending_user(any_email: Email) -> User:
    """Пользователь со статусом PENDING_VERIFICATION."""
    return User.register(any_email, AuthProvider.EMAIL_PASSWORD)


@pytest.fixture
def active_user(pending_user: User) -> User:
    """Пользователь со статусом ACTIVE (email подтверждён)."""
    pending_user.confirm_email()
    pending_user.clear_domain_events()
    return pending_user
```

### Реальный пример: Profile BC

```python
@pytest.fixture
def new_profile() -> UserProfile:
    """Новый профиль со всеми настройками по умолчанию."""
    return UserProfile.create(IdFactory())


@pytest.fixture
def profile(new_profile: UserProfile) -> UserProfile:
    """Профиль с очищенными событиями (после создания)."""
    new_profile.clear_domain_events()
    return new_profile
```

### Паттерн: цепочка фикстур

Фикстуры строятся **цепочкой** — каждая следующая переводит агрегат в новое состояние:

```
pending_user  →  active_user  →  disabled_user
     ↑                ↑                ↑
  register()     confirm_email()    disable()
```

**Важно**: производная фикстура вызывает `clear_domain_events()` — чтобы тесты получали чистый список событий.

---

## 6. Тестирование Aggregate Root

Тесты агрегатов — основная часть unit-тестов. Проверяют бизнес-логику, инварианты и события.

### Организация: один класс — одна группа поведения

Тесты группируются в классы по **бизнес-операции** или **группе поведения**, разделённые визуальными секциями:

```python
"""Unit-тесты для агрегата <Aggregate> (<BC> BC)."""

import pytest

from app.context.<bc>.domain.aggregates.<aggregate> import MyAggregate
from app.context.<bc>.domain.events.<events> import (
    SomethingCreated,
    SomethingDone,
)
from app.context.<bc>.domain.exceptions.<exceptions> import (
    SomeBusinessException,
)


# ═══════════════════════════════════════════════════════════════════════════
# Создание
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestMyAggregateCreation:
    def test_create_with_defaults(self, my_aggregate: MyAggregate) -> None:
        assert my_aggregate.status == ...
        assert my_aggregate.user_id is not None

    def test_create_emits_event(self, my_aggregate: MyAggregate) -> None:
        events = my_aggregate.clear_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], SomethingCreated)


# ═══════════════════════════════════════════════════════════════════════════
# Бизнес-операция X
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestMyAggregateDoSomething:
    def test_do_something(self, my_aggregate: MyAggregate) -> None:
        my_aggregate.do_something(...)
        assert my_aggregate.field == expected

    def test_do_something_emits_event(self, my_aggregate: MyAggregate) -> None:
        my_aggregate.clear_domain_events()
        my_aggregate.do_something(...)
        events = my_aggregate.clear_domain_events()
        assert any(isinstance(e, SomethingDone) for e in events)

    def test_do_something_violating_invariant_raises(self, my_aggregate: MyAggregate) -> None:
        with pytest.raises(SomeBusinessException):
            my_aggregate.do_something_invalid(...)
```

### Что тестировать в каждом бизнес-методе

| Аспект | Пример |
|---|---|
| **Успешная мутация** | `assert user.status == AccountStatus.ACTIVE` |
| **Доменное событие** | `assert any(isinstance(e, EmailConfirmed) for e in events)` |
| **Payload события** | `assert event.user_id == str(user.id)` |
| **Нарушение инварианта** | `with pytest.raises(DuplicateRoleException)` |
| **Идемпотентность** | `user.confirm_email()` дважды — нет ошибки, нет дублей событий |
| **Граничные случаи** | Удаление несуществующего элемента — noop, без событий |
| **Обновление timestamp** | `assert profile.updated_at >= before` |

### Паттерн: тестирование событий

```python
# 1. Событие от фабричного метода — проверяем при создании
def test_create_emits_event(self, new_profile: UserProfile) -> None:
    events = new_profile.clear_domain_events()
    assert len(events) == 1
    assert isinstance(events[0], ProfileCreated)
    assert events[0].user_id == str(new_profile.user_id)

# 2. Событие от бизнес-метода — очищаем перед вызовом
def test_disable_emits_event(self, active_user: User) -> None:
    active_user.clear_domain_events()          # ← очистка
    active_user.disable()
    events = active_user.clear_domain_events()
    assert any(isinstance(e, AccountDisabled) for e in events)

# 3. Отсутствие события при noop
def test_no_change_no_event(self, profile: UserProfile) -> None:
    profile.update_appearance(profile.appearance)   # ← то же значение
    events = profile.clear_domain_events()
    assert not any(isinstance(e, AppearanceSettingsChanged) for e in events)

# 4. Проверка changed_fields в событии
def test_tracks_changed_fields(self, profile: UserProfile) -> None:
    new_settings = AppearanceSettings(theme=Theme.DARK)
    profile.update_appearance(new_settings)
    events = profile.clear_domain_events()
    event = next(e for e in events if isinstance(e, AppearanceSettingsChanged))
    assert "theme" in event.changed_fields
```

### Паттерн: тестирование инвариантов

```python
# Бизнес-правило: нельзя удалить последнюю системную роль
def test_remove_last_system_role_raises(self, active_user: User) -> None:
    role_id = Id.generate()
    active_user.assign_role(role_id)
    with pytest.raises(LastSystemRoleException):
        active_user.remove_role(role_id, is_system_role=True)

# Бизнес-правило: операции заблокированы при pending deletion
def test_operations_blocked_when_pending_deletion(self, active_user: User) -> None:
    active_user.request_account_deletion()
    with pytest.raises(AccountDeletionPendingException):
        active_user.assign_role(Id.generate())
```

### Паттерн: тестирование блокировки (lockout)

Для агрегатов с политиками — многошаговые сценарии:

```python
def test_lock_after_threshold(self, email_user_auth: UserAuth, default_lockout_policy: FailedLoginPolicy) -> None:
    for _ in range(3):
        email_user_auth.record_failed_login(default_lockout_policy)
    assert email_user_auth.locked_until is not None

def test_lock_emits_event(self, email_user_auth: UserAuth, default_lockout_policy: FailedLoginPolicy) -> None:
    for _ in range(2):
        email_user_auth.record_failed_login(default_lockout_policy)
    email_user_auth.clear_domain_events()
    email_user_auth.record_failed_login(default_lockout_policy)  # 3-я попытка → lock
    events = email_user_auth.clear_domain_events()
    assert any(isinstance(e, UserLockedOut) for e in events)
```

---

## 7. Тестирование Entity

Entity — сущность с идентичностью, принадлежащая агрегату. Тесты проще, чем для AR.

### Что тестировать

| Аспект | Пример |
|---|---|
| **Создание** | Проверка атрибутов по умолчанию |
| **Методы** | `enable()`, `disable()` — если есть |
| **Equality by id** | Два объекта с одинаковым `id` — равны |
| **Inequality** | Два объекта с разными `id` — не равны |

### Шаблон

```python
"""Unit-тесты для <EntityName>."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.<bc>.domain.entities.<entity> import MyEntity


@pytest.mark.unit
class TestMyEntity:
    def test_create(self) -> None:
        entity = MyEntity(field="value")
        assert entity.field == "value"
        assert entity.id is not None

    def test_method(self) -> None:
        entity = MyEntity(field="value")
        entity.do_something()
        assert entity.field == "new_value"

    def test_equality_by_id(self) -> None:
        shared_id = Id.generate()
        e1 = MyEntity(id=shared_id, field="a")
        e2 = MyEntity(id=shared_id, field="a")
        assert e1 == e2

    def test_inequality_different_id(self) -> None:
        e1 = MyEntity(field="a")
        e2 = MyEntity(field="a")
        assert e1 != e2
```

### Реальный пример: AuthFactor

```python
@pytest.mark.unit
class TestAuthFactor:
    def test_create_auth_factor(self) -> None:
        factor = AuthFactor(method=TwoFactorMethod.TOTP)
        assert factor.method == TwoFactorMethod.TOTP
        assert not factor.is_enabled
        assert not factor.is_primary

    def test_enable_factor(self) -> None:
        factor = AuthFactor(method=TwoFactorMethod.TOTP)
        secret = TwoFASecret(value="JBSWY3DPEHPK3PXP", method=TwoFactorMethod.TOTP)
        factor.enable(secret, is_primary=True)
        assert factor.is_enabled
        assert factor.is_primary
        assert factor.verified_at is not None

    def test_disable_factor(self) -> None:
        factor = AuthFactor(method=TwoFactorMethod.TOTP)
        secret = TwoFASecret(value="JBSWY3DPEHPK3PXP", method=TwoFactorMethod.TOTP)
        factor.enable(secret)
        factor.disable()
        assert not factor.is_enabled
        assert not factor.is_primary
```

---

## 8. Тестирование Value Object

VO — самая многочисленная группа тестов. Подход зависит от вида VO.

### 8.1. Enum VO

Enum VO обычно **не** тестируются отдельно — их значения проверяются в контексте агрегата. Исключение — если enum имеет вычисляемые свойства.

### 8.2. Simple VO (с валидацией)

Проверяем: создание, валидацию, `__str__`, equality, immutability.

```python
"""Unit-тесты для <ValueObject>."""

import pytest

from app.shared.domain.exceptions import ValidationException
from app.context.<bc>.domain.value_objects.<vo> import MyValue


@pytest.mark.unit
class TestMyValue:
    def test_valid_value(self) -> None:
        vo = MyValue("valid")
        assert vo.value == "valid"

    def test_invalid_value_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            MyValue("invalid")
        assert exc_info.value.field == "my_value"

    def test_normalization(self) -> None:
        vo = MyValue("  Mixed Case  ")
        assert vo.value == "mixed case"  # если VO нормализует

    def test_frozen(self) -> None:
        vo = MyValue("valid")
        with pytest.raises(AttributeError):
            vo.value = "changed"

    def test_equality_by_value(self) -> None:
        assert MyValue("a") == MyValue("a")

    def test_str_representation(self) -> None:
        assert str(MyValue("abc")) == "abc"
```

### Реальные примеры Simple VO

```python
# Email — нормализация + валидация
def test_valid_email_normalizes_to_lowercase(self) -> None:
    email = Email("User@Example.COM")
    assert email.value == "user@example.com"

def test_invalid_email_raises(self) -> None:
    with pytest.raises(ValidationException) as exc_info:
        Email("not-email")
    assert exc_info.value.field == "email"

# Color — формат + нормализация
def test_valid_color_normalizes_to_uppercase(self) -> None:
    color = Color("#ff5500")
    assert color.value == "#FF5500"

def test_invalid_color_name_raises(self) -> None:
    with pytest.raises(ValidationException) as exc_info:
        Color("red")
    assert exc_info.value.field == "color"

# IpAddress — IPv4/IPv6 + вычисляемые свойства
def test_valid_ipv4(self) -> None:
    ip = IpAddress("192.168.1.1")
    assert ip.is_ipv4
    assert not ip.is_ipv6
```

### 8.3. Composite VO (группы настроек)

Проверяем: значения по умолчанию, frozen, equality, `clone()`.

```python
@pytest.mark.unit
class TestAppearanceSettings:
    def test_defaults(self) -> None:
        settings = AppearanceSettings()
        assert settings.theme == Theme.SYSTEM
        assert settings.accent_color == Color("#6366F1")
        assert settings.interface_density == InterfaceDensity.COMFORTABLE

    def test_custom_values(self) -> None:
        custom = CustomTheme(name="Midnight", colors={"bg": Color("#000000")})
        settings = AppearanceSettings(theme=Theme.CUSTOM, custom_theme=custom)
        assert settings.custom_theme.name == "Midnight"

    def test_frozen(self) -> None:
        settings = AppearanceSettings()
        with pytest.raises(Exception):
            settings.theme = Theme.DARK

    def test_equality_by_value(self) -> None:
        assert AppearanceSettings() == AppearanceSettings()

    def test_clone_with_override(self) -> None:
        settings = AppearanceSettings()
        dark = settings.clone(theme=Theme.DARK)
        assert dark.theme == Theme.DARK
        assert settings.theme == Theme.SYSTEM  # оригинал не изменился
```

### 8.4. Policy VO

Policy VO — конфигурация бизнес-правил. Тестируется через conftest-фикстуру, проверяется в контексте агрегата (см. раздел 6, паттерн lockout).

---

## 9. Тестирование Domain Exception

Тесты исключений проверяют **иерархию наследования** и **атрибуты**.

### Шаблон

```python
"""Unit-тесты для исключений <Aggregate> aggregate (<BC> BC)."""

import pytest

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import (
    BusinessRuleViolationException,
    EntityNotFoundException,
)
from app.context.<bc>.domain.exceptions.<aggregate>_exceptions import (
    MyNotFoundException,
    MyBusinessRuleException,
    MySpecificException,
)


@pytest.mark.unit
class TestMyNotFoundException:
    def test_is_entity_not_found(self) -> None:
        exc = MyNotFoundException(id="abc-123")
        assert isinstance(exc, EntityNotFoundException)
        assert exc.entity_type == "MyAggregate"

    def test_message_contains_id(self) -> None:
        exc = MyNotFoundException(id="abc-123")
        assert "abc-123" in exc.message


@pytest.mark.unit
class TestMyBusinessRuleException:
    def test_is_business_rule(self) -> None:
        exc = MyBusinessRuleException()
        assert isinstance(exc, BusinessRuleViolationException)


@pytest.mark.unit
class TestMySpecificException:
    def test_is_domain(self) -> None:
        exc = MySpecificException()
        assert isinstance(exc, DomainException)

    def test_message(self) -> None:
        exc = MySpecificException()
        assert "ожидаемый текст" in exc.message.lower()
```

### Что тестировать

| Тип исключения | Проверяем |
|---|---|
| `EntityNotFoundException` | `isinstance`, `entity_type`, наличие ID в `message` |
| `BusinessRuleViolationException` | `isinstance`, `rule` |
| `ValidationException` | `isinstance`, `field`, `message` |
| `DomainException` | `isinstance`, `message` |

---

## 10. Конвенции и антипаттерны

### Именование

| Элемент | Конвенция | Пример |
|---|---|---|
| **Файл** | `test_<domain_object>.py` | `test_user.py`, `test_appearance_settings.py` |
| **Класс** | `Test<Object><Behavior>` | `TestUserRegistration`, `TestSessionRefresh` |
| **Метод** | `test_<action>` или `test_<action>_<outcome>` | `test_assign_role`, `test_assign_duplicate_role_raises` |

### Суффиксы методов

| Суффикс | Когда использовать | Пример |
|---|---|---|
| (нет суффикса) | Успешный сценарий | `test_create_session` |
| `_emits_event` | Проверка доменного события | `test_disable_emits_event` |
| `_raises` | Ожидаемое исключение | `test_lock_after_threshold_raises` |
| `_is_noop` | Идемпотентная операция | `test_confirm_email_already_confirmed_is_noop` |
| `_ignored` | Операция без эффекта | `test_remove_nonexistent_role_ignored` |

### Визуальные секции

Тест-классы в файле разделяются визуальными секциями для удобства навигации:

```python
# ═══════════════════════════════════════════════════════════════════════════
# Название секции
# ═══════════════════════════════════════════════════════════════════════════
```

### `clear_domain_events()`: когда и зачем

| Ситуация | Действие |
|---|---|
| Тест фабричного метода (`.create()`, `.register()`) | `events = aggregate.clear_domain_events()` — проверяем события создания |
| Тест бизнес-метода на фикстуре | `aggregate.clear_domain_events()` **перед** вызовом — изолируем от событий создания |
| Производная фикстура в conftest | `clear_domain_events()` **в фикстуре** — чтобы тесты получили чистый список |

### Антипаттерны

| ❌ Не делать | ✅ Делать |
|---|---|
| Мокировать доменные объекты | Использовать реальные доменные объекты |
| Тестировать приватные методы (`_assert_*`) | Тестировать через публичное API агрегата |
| Один большой тест на всё | Один тест — одно поведение |
| Зависимость от порядка тестов | Каждый тест создаёт собственный контекст через фикстуры |
| Хардкодить UUID в тестах | Использовать `IdFactory()` или `Id.generate()` |
| Пропускать проверку событий | Для каждого бизнес-метода — отдельный `test_*_emits_event` |
| `assert True` / `assert not False` | Проверять конкретные значения и свойства |

### Docstring файла

Каждый тестовый файл начинается с docstring, описывающего предмет тестирования:

```python
"""Unit-тесты для агрегата User (Identity BC)."""
```

### Типизация тестовых методов

Все тестовые методы аннотируются `-> None`:

```python
def test_register_user(self, pending_user: User) -> None:
    ...
```

---

## 11. Чеклист нового BC

Для создания unit-тестов domain layer нового Bounded Context `<bc_name>`:

### Подготовка

- [ ] Создать `tests/unit/<bc_name>/` со структурой из раздела 2
- [ ] Добавить `__init__.py` в каждый подпакет
- [ ] Создать `tests/unit/<bc_name>/conftest.py` с фикстурами BC

### Фабрики

- [ ] Добавить BC-специфичные фабрики в `tests/factories.py` (если есть новые VO)
- [ ] Фабрики генерируют валидные доменные объекты

### Фикстуры (conftest.py)

- [ ] VO-фикстуры (`any_email`, `any_device_info`) — для переиспользования
- [ ] Policy-фикстуры — если есть бизнес-политики
- [ ] Агрегатные фикстуры — цепочка состояний (`new_*` → `active_*` → ...)
- [ ] Производные фикстуры вызывают `clear_domain_events()`

### Агрегаты (`aggregates/`)

- [ ] Один файл на агрегат: `test_<aggregate>.py`
- [ ] Тесты фабричного метода: создание + событие + атрибуты по умолчанию
- [ ] Тесты каждого бизнес-метода: мутация + событие
- [ ] Тесты инвариантов: `pytest.raises(<DomainException>)`
- [ ] Тесты граничных случаев: noop, идемпотентность, дубликаты
- [ ] Секции `═══` для визуальной группировки

### Сущности (`entities/`)

- [ ] Один файл на сущность: `test_<entity>.py`
- [ ] Тест создания с дефолтными значениями
- [ ] Тесты методов (если есть)
- [ ] Тесты equality by id

### Value Objects (`value_objects/`)

- [ ] Один файл на VO: `test_<value_object>.py`
- [ ] Simple VO: валидация, нормализация, frozen, equality, `__str__`
- [ ] Composite VO: defaults, custom values, frozen, equality, `clone()`
- [ ] Enum VO: тестируются в контексте агрегата (опционально отдельный файл)

### Исключения (`exceptions/`)

- [ ] Один файл на группу: `test_<aggregate>_exceptions.py`
- [ ] Каждое исключение: `isinstance` от правильного базового класса
- [ ] `EntityNotFoundException`: `entity_type`, наличие ID в `message`
- [ ] `BusinessRuleViolationException`: `rule`
- [ ] `DomainException`: `message`

### Проверки

- [ ] Каждый тест-класс помечен `@pytest.mark.unit`
- [ ] Каждый тестовый метод аннотирован `-> None`
- [ ] Нет моков доменных объектов — только реальные инстансы
- [ ] Нет зависимости от внешних сервисов (БД, Redis, HTTP)
- [ ] `pytest -m unit` проходит без ошибок
