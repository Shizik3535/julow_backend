# Гайд: Seeding (значения по умолчанию)

## Содержание

1. [Обзор](#1-обзор)
2. [Архитектура](#2-архитектура)
3. [Seed-модули](#3-seed-модули)
4. [Standalone-скрипты](#4-standalone-скрипты)
5. [Alembic: миграции и DDL](#5-alembic-миграции-и-ddl)
6. [Seed в тестах](#6-seed-в-тестах)
7. [Конвенции](#7-конвенции)
8. [Чеклист добавления нового seed](#8-чеклист-добавления-нового-seed)

---

## 1. Обзор

Seeding — механизм наполнения базы данных **начальными данными**, без которых приложение не может корректно работать. Seed-данные — это не пользовательский контент, а **системные справочники и конфигурация**.

### Какие данные сидируются

| Данные | Пример | Зачем |
|---|---|---|
| **Системные роли** | `super_admin`, `admin`, `supporter`, `user` | FK constraints, RBAC, назначение роли при регистрации |
| **Permissions** | `users.*`, `content.*`, `self.*` | Привязаны к ролям, проверяются при авторизации |

### Где используется seed

| Контекст | Механизм | Когда запускается |
|---|---|---|
| **Development** | `python -m scripts.seed_roles` | После `alembic upgrade head` |
| **Production** | Data migration в Alembic или standalone-скрипт | При деплое |
| **Integration-тесты** | Seed в `db_engine` фикстуре | При запуске тестов |
| **E2E-тесты** | Seed в `_db_tables` фикстуре | При запуске тестов |

### Принципы

- **Единый источник правды**: seed-данные определяются в одном месте — seed-модуле.
- **Идемпотентность**: `INSERT ... ON CONFLICT DO NOTHING` — безопасно запускать многократно.
- **Стабильные UUID**: системные сущности имеют фиксированные ID (`00000000-0000-0000-0000-000000000001`).
- **Без бизнес-логики**: seed не проходит через domain layer — это прямой SQL/ORM insert.

---

## 2. Архитектура

Механизм seeding состоит из трёх слоёв:

```
┌─────────────────────────────────────────────────────────────┐
│  Seed-модуль (данные)                                       │
│  app/context/<bc>/infrastructure/persistence/seed/          │
│  → Определяет ЧТО вставлять (list[dict])                    │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               ▼                              ▼
┌──────────────────────────┐   ┌──────────────────────────────┐
│  Standalone-скрипт       │   │  Test conftest                │
│  scripts/seed_roles.py   │   │  tests/{integration,e2e}/    │
│  → КАК вставлять (SQL)   │   │  conftest.py                 │
│  → Запуск: CLI            │   │  → Вставка в фикстуре        │
└──────────────────────────┘   └──────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Alembic                                                    │
│  alembic/env.py          → DDL (create/drop tables)         │
│  alembic/versions/*.py   → Schema + Data migrations         │
└─────────────────────────────────────────────────────────────┘
```

### Поток данных

1. **Seed-модуль** (`system_roles.py`) — единственное место, где определены данные.
2. **Потребители** импортируют `SYSTEM_ROLES` из модуля и вставляют через SQL.
3. **Alembic** управляет DDL (таблицы), а seed-скрипты — DML (данные).

---

## 3. Seed-модули

### Расположение

```
app/context/<bc>/infrastructure/persistence/seed/
├── __init__.py
└── system_roles.py       # ← seed-данные для Identity BC
```

Seed-модули размещаются в `infrastructure/persistence/seed/` соответствующего Bounded Context.

### Формат данных

```python
from __future__ import annotations

from uuid import UUID


SYSTEM_ROLES: list[dict[str, object]] = [
    {
        "id": UUID("00000000-0000-0000-0000-000000000001"),
        "name": "super_admin",
        "permissions": ["*"],
        "is_system": True,
        "description": "Полный доступ",
    },
    {
        "id": UUID("00000000-0000-0000-0000-000000000002"),
        "name": "admin",
        "permissions": ["users.*", "content.*", "settings.*"],
        "is_system": True,
        "description": "Управление пользователями и контентом",
    },
    {
        "id": UUID("00000000-0000-0000-0000-000000000003"),
        "name": "supporter",
        "permissions": ["users.read", "users.support", "content.read"],
        "is_system": True,
        "description": "Ограниченные права поддержки",
    },
    {
        "id": UUID("00000000-0000-0000-0000-000000000004"),
        "name": "user",
        "permissions": ["self.*"],
        "is_system": True,
        "description": "Базовый доступ к собственным данным",
    },
]
```

### Правила seed-модуля

| Правило | Пример |
|---|---|
| **Стабильные UUID** | `UUID("00000000-0000-0000-0000-000000000001")` — не `uuid4()` |
| **`list[dict]`** | Не domain-объекты, а plain dict — модуль не зависит от domain layer |
| **Все поля** | `id`, `name`, `permissions`, `is_system`, `description` — всё, что нужно для INSERT |
| **Константа верхнего уровня** | `SYSTEM_ROLES = [...]` — импортируется потребителями |
| **Без логики** | Только данные, без `async def`, без side-effects при импорте |

### Шаблон seed-модуля для нового BC

```python
"""
Seed-данные для <название сущности> (<BC> BC).

Используется в:
    - scripts/seed_<entities>.py
    - tests/integration/conftest.py
    - tests/e2e/conftest.py
"""
from __future__ import annotations

from uuid import UUID


SYSTEM_<ENTITIES>: list[dict[str, object]] = [
    {
        "id": UUID("00000000-0000-0000-0000-0000000000XX"),
        "name": "<name>",
        # ... остальные поля, соответствующие колонкам таблицы
    },
]
```

---

## 4. Standalone-скрипты

### Расположение

```
scripts/
├── __init__.py
└── seed_roles.py         # ← скрипт для вставки системных ролей
```

### Структура скрипта

```python
"""
Standalone script to seed system roles into the database.

Idempotent: uses INSERT ... ON CONFLICT (name) DO NOTHING,
so it's safe to run multiple times.

Usage:
    python -m scripts.seed_roles
    python scripts/seed_roles.py
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

# Ensure project root is on sys.path so `app` is importable
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.context.identity.infrastructure.persistence.seed.system_roles import SYSTEM_ROLES
from app.core.config.database_settings import DatabaseSettings


async def seed_roles() -> None:
    settings = DatabaseSettings()
    engine = create_async_engine(settings.url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        inserted = 0
        for role in SYSTEM_ROLES:
            result = await session.execute(
                text(
                    "INSERT INTO roles (id, name, permissions, is_system, description, created_at, updated_at) "
                    "VALUES (:id, :name, :permissions::jsonb, :is_system, :description, now(), now()) "
                    "ON CONFLICT (name) DO NOTHING"
                ),
                {
                    "id": str(role["id"]),
                    "name": role["name"],
                    "permissions": json.dumps(role["permissions"]),
                    "is_system": role["is_system"],
                    "description": role["description"],
                },
            )
            inserted += result.rowcount
        await session.commit()

        if inserted:
            print(f"✓ Inserted {inserted} system role(s)")
        else:
            print("✓ All system roles already exist — nothing to insert")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_roles())
```

### Ключевые элементы

| Элемент | Назначение |
|---|---|
| `sys.path` fixup | Позволяет запускать как `python scripts/seed_roles.py` из корня проекта |
| `DatabaseSettings()` | Читает `DB_HOST`, `DB_PORT`, ... из `.env` |
| `ON CONFLICT (name) DO NOTHING` | Идемпотентность — повторный запуск безопасен |
| `:permissions::jsonb` | PostgreSQL-специфичный cast для JSON-колонки |
| `result.rowcount` | Подсчёт реально вставленных строк |
| `await engine.dispose()` | Корректное закрытие пула соединений |

### Запуск

```bash
# Из корня проекта
python -m scripts.seed_roles

# Или напрямую
python scripts/seed_roles.py
```

### Шаблон standalone-скрипта для нового seed

```python
"""
Standalone script to seed <entities> into the database.

Idempotent: uses INSERT ... ON CONFLICT (<unique_column>) DO NOTHING.

Usage:
    python -m scripts.seed_<entities>
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.context.<bc>.infrastructure.persistence.seed.<module> import SYSTEM_<ENTITIES>
from app.core.config.database_settings import DatabaseSettings


async def seed_<entities>() -> None:
    settings = DatabaseSettings()
    engine = create_async_engine(settings.url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        inserted = 0
        for item in SYSTEM_<ENTITIES>:
            result = await session.execute(
                text(
                    "INSERT INTO <table> (<columns>) "
                    "VALUES (<params>) "
                    "ON CONFLICT (<unique_column>) DO NOTHING"
                ),
                {<param_dict>},
            )
            inserted += result.rowcount
        await session.commit()

        if inserted:
            print(f"✓ Inserted {inserted} <entity>(s)")
        else:
            print("✓ All <entities> already exist — nothing to insert")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_<entities>())
```

---

## 5. Alembic: миграции и DDL

### Конфигурация

#### `alembic.ini`

```ini
[alembic]
script_location = %(here)s/alembic
file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s
prepend_sys_path = .
timezone = UTC
revision_environment = true

# Fallback URL. Overridden by env.py from app settings.
sqlalchemy.url = postgresql+asyncpg://postgres:postgres@localhost:5432/julow

[post_write_hooks]
hooks = ruff
ruff.type = exec
ruff.executable = ruff
ruff.options = check --fix REVISION_SCRIPT_FILENAME
```

| Параметр | Значение |
|---|---|
| `file_template` | `YYYY_MM_DD_HHMM-<rev>_<slug>` — сортируемые по дате файлы |
| `prepend_sys_path = .` | Проект root в `sys.path` — можно импортировать `app.*` |
| `timezone = UTC` | Метки времени в UTC |
| `revision_environment = true` | `env.py` выполняется при `alembic revision` |
| `post_write_hooks` | Автоматический `ruff check --fix` при создании миграции |

#### `alembic/env.py`

```python
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from app.core.config import settings
from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel

# ORM models — импорт необходим, чтобы Alembic увидел таблицы в metadata
from app.context.identity.infrastructure.persistence.orm_models.user_orm import UserORM  # noqa: F401
from app.context.identity.infrastructure.persistence.orm_models.user_auth_orm import UserAuthORM  # noqa: F401
from app.context.identity.infrastructure.persistence.orm_models.session_orm import SessionORM  # noqa: F401
from app.context.identity.infrastructure.persistence.orm_models.role_orm import RoleORM  # noqa: F401
from app.context.profile.infrastructure.persistence.orm_models.user_profile_orm import UserProfileORM  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", settings.db.url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = BaseORMModel.metadata
```

**Ключевые моменты:**

- **ORM-импорты**: каждая ORM-модель должна быть импортирована, чтобы `BaseORMModel.metadata` содержала все таблицы для autogenerate.
- **`settings.db.url`**: URL берётся из конфигурации приложения (`.env`), а не из `alembic.ini`.
- **Async engine**: миграции запускаются через `asyncio.run(run_async_migrations())`.

### Работа с миграциями

#### Создание миграции (autogenerate)

```bash
alembic revision --autogenerate -m "описание изменений"
```

Alembic сравнивает `target_metadata` (из ORM-моделей) с текущей схемой БД и генерирует `upgrade()` / `downgrade()`.

#### Применение миграций

```bash
alembic upgrade head        # применить все
alembic upgrade +1          # одна вперёд
alembic downgrade -1        # откатить одну
alembic history             # история
alembic current             # текущая ревизия
```

### Data Migration (seed в миграции)

Для production-деплоя seed-данные можно вставить прямо в Alembic-миграцию:

```python
"""add system roles seed

Revision ID: abc123
"""
import json

from alembic import op
from sqlalchemy import text

from app.context.identity.infrastructure.persistence.seed.system_roles import SYSTEM_ROLES


def upgrade() -> None:
    for role in SYSTEM_ROLES:
        op.execute(
            text(
                "INSERT INTO roles (id, name, permissions, is_system, description, created_at, updated_at) "
                "VALUES (:id, :name, :permissions::jsonb, :is_system, :description, now(), now()) "
                "ON CONFLICT (name) DO NOTHING"
            ).bindparams(
                id=str(role["id"]),
                name=role["name"],
                permissions=json.dumps(role["permissions"]),
                is_system=role["is_system"],
                description=role["description"],
            )
        )


def downgrade() -> None:
    for role in SYSTEM_ROLES:
        op.execute(
            text("DELETE FROM roles WHERE id = :id").bindparams(id=str(role["id"]))
        )
```

**Когда использовать data migration vs standalone-скрипт:**

| Data migration (в Alembic) | Standalone-скрипт |
|---|---|
| Production: данные вставляются автоматически при `alembic upgrade head` | Development: ручной запуск после миграций |
| Гарантированный порядок: DDL → DML | Гибкость: можно запускать повторно |
| Необратимый (если нет downgrade) | Идемпотентный по умолчанию |

### Добавление ORM-модели нового BC в env.py

При создании нового BC с ORM-моделями — добавить импорт в `alembic/env.py`:

```python
# Новый BC
from app.context.<new_bc>.infrastructure.persistence.orm_models.<model>_orm import <Model>ORM  # noqa: F401
```

Без этого импорта `alembic revision --autogenerate` **не увидит** таблицы нового BC.

---

## 6. Seed в тестах

### Integration-тесты (`tests/integration/conftest.py`)

Seed system roles выполняется в `db_engine` фикстуре (scope="session"):

```python
@pytest_asyncio.fixture(scope="session")
async def db_engine(app_settings):
    # ... create engine, create_all ...

    # Seed system roles so FK constraints and role lookups work (PostgreSQL only)
    if pg_url is not None:
        import json as _json
        from sqlalchemy import text as _sa_text
        from app.context.identity.infrastructure.persistence.seed.system_roles import SYSTEM_ROLES as _ROLES
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

    yield engine
    # ... drop_all, dispose ...
```

**Зачем**: без системных ролей тесты, зависящие от FK на `roles` (например, `user_roles`), упадут с `ForeignKeyViolation`.

### E2E-тесты (`tests/e2e/conftest.py`)

Seed выполняется в `_db_tables` фикстуре (scope="session"):

```python
@pytest_asyncio.fixture(scope="session")
async def _db_tables(app):
    # ... create database, create_all ...

    import json as _json
    from sqlalchemy import text as _sa_text
    from app.context.identity.infrastructure.persistence.seed.system_roles import SYSTEM_ROLES as _ROLES
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

    yield
    # ... drop_all ...
```

### Дублирование seed-кода

Seed SQL дублируется в трёх местах (скрипт, integration conftest, e2e conftest). Это **осознанное решение**:

| Причина | Объяснение |
|---|---|
| Разные engine'ы | Скрипт создаёт свой engine, тесты используют тестовый |
| Разные scope | Скрипт — одноразовый, тесты — в рамках session-фикстуры |
| Простота | SQL seed — 10 строк, общий хелпер усложнит зависимости |

**Единый источник правды** — `SYSTEM_ROLES` из seed-модуля. SQL-шаблон одинаковый, но вызывается в разных контекстах.

---

## 7. Конвенции

### Стабильные UUID

Системные сущности используют **фиксированные UUID**, а не `uuid4()`:

```python
"id": UUID("00000000-0000-0000-0000-000000000001"),  # super_admin
"id": UUID("00000000-0000-0000-0000-000000000002"),  # admin
"id": UUID("00000000-0000-0000-0000-000000000003"),  # supporter
"id": UUID("00000000-0000-0000-0000-000000000004"),  # user
```

**Зачем:**
- Предсказуемость — можно ссылаться по ID в тестах и скриптах.
- Идемпотентность — повторная вставка не создаёт дубликаты.
- Согласованность — одинаковый ID на всех средах (dev, staging, prod).

### `ON CONFLICT DO NOTHING`

Каждый seed SQL использует `ON CONFLICT`:

```sql
INSERT INTO roles (id, name, ...) VALUES (:id, :name, ...)
ON CONFLICT (name) DO NOTHING
```

**Зачем**: безопасно запускать многократно. Если запись уже существует — пропускается без ошибки.

### Seed-модуль как единый источник правды

```
SYSTEM_ROLES (модуль)
    ↓ импорт
scripts/seed_roles.py
tests/integration/conftest.py
tests/e2e/conftest.py
alembic data migration
```

**Никогда** не хардкодить seed-данные в SQL или тестах. Всегда импортировать из seed-модуля.

### Порядок операций

```
1. alembic upgrade head     → DDL: таблицы созданы
2. python -m scripts.seed_* → DML: данные вставлены
```

Seed-скрипт **требует** существования таблиц. Запускать после миграций.

### Naming

| Элемент | Конвенция | Пример |
|---|---|---|
| Seed-модуль | `<entities>.py` | `system_roles.py` |
| Константа | `SYSTEM_<ENTITIES>` | `SYSTEM_ROLES` |
| Скрипт | `seed_<entities>.py` | `seed_roles.py` |
| Директория | `<bc>/infrastructure/persistence/seed/` | `identity/infrastructure/persistence/seed/` |

### Антипаттерны

| ❌ Не делать | ✅ Делать |
|---|---|
| `uuid4()` для системных сущностей | Фиксированные UUID в seed-модуле |
| Хардкодить данные в SQL миграции | Импортировать из seed-модуля |
| `INSERT ... VALUES ...` без `ON CONFLICT` | Всегда `ON CONFLICT DO NOTHING` |
| Seed через domain layer (`Role(...)`, `repo.add()`) | Прямой SQL — быстрее, без side-effects |
| Разные данные в dev и prod seed | Один seed-модуль для всех сред |
| Seed в `__init__.py` модуля (side-effects при импорте) | Отдельный файл, данные в константе |

---

## 8. Чеклист добавления нового seed

### 1. Seed-модуль

- [ ] Создать `app/context/<bc>/infrastructure/persistence/seed/` с `__init__.py`
- [ ] Создать `<entities>.py` с константой `SYSTEM_<ENTITIES>: list[dict[str, object]]`
- [ ] Каждая запись содержит `id` (стабильный `UUID`), все обязательные колонки таблицы
- [ ] Нет import'ов из domain layer — только `uuid.UUID` и стандартные типы

### 2. Standalone-скрипт

- [ ] Создать `scripts/seed_<entities>.py`
- [ ] Импортировать `SYSTEM_<ENTITIES>` из seed-модуля
- [ ] SQL: `INSERT ... ON CONFLICT (<unique_column>) DO NOTHING`
- [ ] `sys.path` fixup для запуска из корня проекта
- [ ] `DatabaseSettings()` для получения URL из `.env`
- [ ] Вывод: количество вставленных записей или "already exist"
- [ ] Запуск: `python -m scripts.seed_<entities>`
- [ ] Проверить, что скрипт идемпотентен (запустить дважды)

### 3. Alembic (при необходимости)

- [ ] Если добавлена новая ORM-модель — добавить импорт в `alembic/env.py`
- [ ] `alembic revision --autogenerate -m "<описание>"` — сгенерировать миграцию
- [ ] Проверить сгенерированный файл (`upgrade()` / `downgrade()`)
- [ ] `alembic upgrade head` — применить
- [ ] (Опционально) Data migration: добавить seed SQL в отдельную миграцию для production

### 4. Тесты: integration conftest

- [ ] В `tests/integration/conftest.py` → `db_engine` фикстуре: добавить seed SQL
- [ ] Импортировать `SYSTEM_<ENTITIES>` из seed-модуля
- [ ] SQL: `INSERT ... ON CONFLICT DO NOTHING` (аналогично скрипту)
- [ ] Проверить: `pytest -m integration` проходит

### 5. Тесты: e2e conftest

- [ ] В `tests/e2e/conftest.py` → `_db_tables` фикстуре: добавить seed SQL
- [ ] Импортировать `SYSTEM_<ENTITIES>` из seed-модуля
- [ ] SQL: `INSERT ... ON CONFLICT DO NOTHING` (аналогично скрипту)
- [ ] Проверить: `pytest -m e2e` проходит

### 6. Проверки

- [ ] UUID стабильные и уникальные
- [ ] `ON CONFLICT` на правильную колонку (обычно `name` или `id`)
- [ ] Скрипт запускается из корня проекта без ошибок
- [ ] Повторный запуск скрипта — без ошибок, 0 inserted
- [ ] Integration и E2E тесты проходят
- [ ] `alembic upgrade head` + `python -m scripts.seed_<entities>` на чистой БД — без ошибок
