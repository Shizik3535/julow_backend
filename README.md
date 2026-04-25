# Julow Backend

**Julow** (TaskFlow) — серверная часть платформы управления задачами и проектами. Предназначена для широкого спектра пользователей: от индивидуальных разработчиков и фрилансеров до крупных компаний и государственного сектора.

Система разворачивается как:
- **SaaS** — облачное решение для индивидуальных пользователей и команд
- **Self-hosted** — Docker/Kubernetes для бизнеса
- **On-premise** — bare-metal / закрытый контур для гос. сектора и военных предприятий

### Ключевые возможности

- Аутентификация: email + пароль, OAuth 2.0 (Google, GitHub), 2FA (TOTP, email), доверенные устройства
- Организации: участники, команды, подразделения, роли, приглашения, SSO-интеграции
- Профили: аватар, bio, настройки (внешний вид, локализация, уведомления, приватность, горячие клавиши)
- Workspace, Project, Task, Sprint, Comment, File, Time Tracking, Notification — в разработке

Спецификация домена: [`spec/`](spec/) · Справочник API: [`docs/api/api-reference.md`](docs/api/api-reference.md)

---

## Архитектура и стек

### Стек технологий

| Категория | Технология |
|-----------|-----------|
| Язык | Python 3.12 |
| Фреймворк | FastAPI |
| БД | PostgreSQL 16 + SQLAlchemy (async) + asyncpg |
| Миграции | Alembic |
| Кэш | Redis 7 |
| Месседжинг | Apache Kafka (KRaft, без Zookeeper) |
| Хранилище файлов | MinIO (S3-совместимое) |
| Фоновые задачи | Celery |
| DI | dependency-injector |
| Логирование | structlog |
| Аутентификация | PyJWT + passlib (argon2) + pyOTP |
| Шифрование | cryptography (Fernet) |
| SMTP (dev) | MailHog |
| Линтинг | Ruff |
| Типизация | mypy (strict) |
| Тестирование | pytest + pytest-asyncio + factory-boy |

### Архитектура: Domain-Driven Design

Система строится по принципам DDD. Каждый Bounded Context — изолированный домен с собственными агрегатами, сущностями и событиями.

```
┌─────────────────────────────────────────────────────────────────┐
│                        Julow Platform                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │   Identity    │  │   System     │  │    Organization      │   │
│  │   Context     │──│   Roles      │──│    Context           │   │
│  └──────┬───────┘  └──────────────┘  └──────────┬───────────┘   │
│         │                                        │               │
│         │           ┌──────────────┐             │               │
│         └──────────│  Workspace   │─────────────┘               │
│                     │  Context     │                              │
│                     └──────┬───────┘                              │
│                            │                                      │
│              ┌─────────────┼─────────────┐                       │
│              │             │             │                        │
│       ┌──────┴──────┐ ┌───┴────┐ ┌──────┴──────┐               │
│       │   Project    │ │  Task  │ │   Sprint    │               │
│       │   Context    │ │Context │ │   Context   │               │
│       └──────┬───────┘ └───┬────┘ └─────────────┘               │
│              │             │                                      │
│    ┌─────────┼─────────────┼──────────────┐                      │
│    │         │             │              │                       │
│ ┌──┴───┐ ┌──┴──────┐ ┌───┴────┐ ┌───────┴──────┐              │
│ │Comment│ │  File   │ │  Time  │ │ Notification │              │
│ │Context│ │ Context │ │Tracking│ │   Context    │              │
│ └──────┘ └─────────┘ │Context │ └──────────────┘              │
│                       └────────┘                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Паттерны

- **CQRS** — разделение на Commands и Queries с отдельными хендлерами
- **Domain Events** — контексты обмениваются событиями через Kafka
- **Repository** — абстракция доступа к агрегатам через порты (ports) и адаптеры (infrastructure)
- **DI Container** — централизованная конфигурация зависимостей (dependency-injector)
- **Port & Adapter** — инфраструктура за портами, легко заменяемыми (PostgreSQL ↔ SQLite, Redis ↔ in-memory, MinIO ↔ S3)

---

## Быстрый старт

### Требования

- Python 3.12+
- Docker + Docker Compose

### 1. Клонирование

```bash
git clone <repo-url> && cd backend
```

### 2. Переменные окружения

```bash
cp .env.example .env
```

Для локальной разработки значения по умолчанию подходят как есть.

### 3. Запуск инфраструктуры

```bash
docker compose -f docker-compose.dev.yml up -d
```

Поднимаются: PostgreSQL (5432), Redis (6379), Kafka (9092), MinIO (9000/9001), MailHog (1025/8025).

### 4. Установка зависимостей

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

### 5. Миграции БД

```bash
alembic upgrade head
```

### 6. Запуск сервера

```bash
uvicorn app.main:app --reload
```

### Проверка

- Swagger UI: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- ReDoc: [http://localhost:8000/api/v1/redoc](http://localhost:8000/api/v1/redoc)

### Остановка инфраструктуры

```bash
docker compose -f docker-compose.dev.yml down
```

---

## Структура проекта и разработка

### Структура каталогов

```
backend/
├── alembic/                  # Миграции БД
│   └── versions/
├── app/
│   ├── api/v1/               # Роуты API v1 (сборка всех BC)
│   ├── context/              # Bounded Context'ы
│   │   ├── identity/         #   Аутентификация, аккаунт, безопасность
│   │   ├── profile/          #   Профиль пользователя, настройки
│   │   ├── organization/     #   Организации, участники, команды, роли
│   │   ├── workspace/        #   Рабочие пространства
│   │   ├── project/          #   Проекты
│   │   ├── task/             #   Задачи
│   │   ├── communication/    #   Комментарии, мессенджер
│   │   ├── filestorage/      #   Файловое хранилище
│   │   ├── analytics/        #   Аналитика
│   │   ├── notification/     #   Уведомления
│   │   ├── security/         #   Безопасность
│   │   └── timetracking/     #   Учёт времени
│   ├── core/                 # Ядро приложения
│   │   ├── config/           #   Настройки (pydantic-settings)
│   │   ├── di/               #   DI-контейнер и провайдеры
│   │   ├── logging/          #   structlog конфигурация
│   │   ├── middleware/        #   CORS, correlation ID, request logging
│   │   └── exception_handlers.py  # Глобальные обработчики ошибок
│   └── shared/               # Общий код между контекстами
│       ├── domain/           #   Базовые классы: Aggregate, Entity, VO, DomainEvent, Repository
│       ├── application/      #   Command/Query хендлеры, DTO, порты (ports), messaging
│       ├── infrastructure/   #   Адаптеры: БД, Redis, S3, Kafka, SMTP, auth
│       └── presentation/     #   Базовый контроллер, presenter, responses
├── docs/                     # Документация
├── scripts/                  # Скрипты сидирования (роли)
├── spec/                     # Спецификация домена
├── tests/                    # Тесты
│   ├── unit/                 #   Unit-тесты (без внешних зависимостей)
│   ├── integration/          #   Интеграционные (БД, Redis)
│   └── e2e/                  #   End-to-end (полный HTTP-стек)
├── .env.example
├── docker-compose.dev.yml
├── pyproject.toml            # pytest, ruff, mypy, coverage
├── requirements.txt
└── requirements-dev.txt
```

### Структура Bounded Context'а

Каждый контекст следует четырёхслойной архитектуре:

```
context/<bc>/
├── domain/            # Агрегаты, сущности, value objects, доменные события, интерфейсы репозиториев
├── application/       # Command/Query хендлеры, DTO, бизнес-правила
├── infrastructure/    # Реализация репозиториев (SQLAlchemy), маппинг ORM-моделей
└── presentation/      # Контроллеры (FastAPI), запросы/ответы
```

### Команды разработки

```bash
# Линтинг
ruff check .

# Форматирование
ruff format .

# Типизация
mypy app/

# Тесты (по маркерам)
pytest -m unit          # Unit-тесты
pytest -m integration   # Интеграционные
pytest -m e2e           # End-to-end

# Тесты с покрытием
pytest --cov=app --cov-report=term-missing

# Миграции
alembic revision --autogenerate -m "описание"
alembic upgrade head
alembic downgrade -1
```

### Соглашения

- **Ruff**: target Python 3.12, line-length 120, правила E/F/I/N/UP/B/SIM
- **mypy**: strict mode, Python 3.12
- **pytest**: маркеры `unit`, `integration`, `e2e`; asyncio_mode = auto
- **Код**: комментарии и документация на русском языке
