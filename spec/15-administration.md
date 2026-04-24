# 15. Administration — Администрирование

## Обзор

Контекст администрирования включает admin panel для SaaS-версии и конфигурацию для self-hosted/on-premise. Admin panel используется командой платформы для управления пользователями, workspace, тарифами, feature flags и системными настройками.

---

## Принципы расширяемости

1. **SystemSettings — AR** — иерархические настройки: global → organization → workspace. Нижний уровень переопределяет верхний.
2. **FeatureFlag — AR** — гибкие feature flags с targeting (org/ws/user/percentage) и conditions.
3. **FeatureFlagConditionType — enum** — `ORGANIZATION`, `WORKSPACE`, `USER`, `PERCENTAGE`, `DATE_RANGE`. Новые условия = значение enum + evaluator.
4. **TemplateType — enum** — типы шаблонов (project, workspace, email).
5. **EmailTemplateType — enum** — типы email-шаблонов.
6. **WebhookConfig — entity** — конфигурация webhooks.
7. **HealthCheck — entity** — проверка здоровья компонентов.

---

## 1. Функциональные требования

### 1.1. Admin Panel (SaaS)

| Функция | Super Admin | Admin | Supporter |
|---------|------------|-------|-----------|
| Управление пользователями (CRUD) | ✅ | ✅ | ⚡ read |
| Блокировка / деактивация | ✅ | ✅ | ❌ |
| Управление workspace | ✅ | ✅ | ⚡ read |
| Управление организациями | ✅ | ✅ | ⚡ read |
| Управление тарифами и подписками | ✅ | ✅ | ❌ |
| Статистика использования | ✅ | ✅ | ✅ |
| Feature flags | ✅ | ✅ | ❌ |
| Системные настройки | ✅ | ❌ | ❌ |
| Управление шаблонами | ✅ | ✅ | ❌ |
| Управление интеграциями | ✅ | ✅ | ❌ |
| Email-шаблоны | ✅ | ✅ | ❌ |
| Maintenance mode | ✅ | ❌ | ❌ |

### Статистика использования
- Общее число пользователей (по статусам)
- Активные пользователи за период (DAU, WAU, MAU)
- Количество workspace / организаций / проектов / задач
- Использование хранилища (общее, по workspace)
- Подписки (по тарифам)
- Revenue (MRR, ARR)

### Feature Flags
- Включение/выключение фич глобально
- Включение для конкретных организаций/workspace/пользователей
- Процентный rollout (X% пользователей)
- Scheduled activation/deactivation

### Email-шаблоны
- Кастомизация системных писем (verification, reset, invitation, notification)
- HTML-шаблоны с переменными
- Preview перед сохранением
- Возврат к default-шаблону

### Maintenance Mode
- Включение/выключение
- Custom message для пользователей
- Whitelist IP (для admin-доступа)
- Scheduled maintenance (с уведомлением заранее)

### 1.2. Self-Hosted конфигурация

| Функция | Business (Docker) | Enterprise (Docker/K8s/Bare Metal) |
|---------|-------------------|-------------------------------------|
| Docker Compose | ✅ | ✅ |
| Kubernetes (Helm charts) | ❌ | ✅ |
| Bare metal | ❌ | ✅ |
| Env variables конфигурация | ✅ | ✅ |
| Config file (YAML) | ✅ | ✅ |
| Web-based setup wizard | ✅ | ✅ |
| Управление БД | ⚡ | ✅ |
| Custom SMTP | ✅ | ✅ |
| LDAP / Active Directory | ❌ | ✅ |
| Мониторинг здоровья | ✅ | ✅ |
| Централизованное логирование | ⚡ | ✅ |
| Обновление версии | ✅ автоматич. | ✅ ручное/авто |

### Self-Hosted конфигурация (Environment Variables)

```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/taskflow
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://host:6379/0

# S3 Storage
S3_ENDPOINT=https://s3.amazonaws.com
S3_BUCKET=taskflow-files
S3_ACCESS_KEY=...
S3_SECRET_KEY=...
S3_REGION=eu-west-1

# SMTP
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=noreply@example.com
SMTP_PASSWORD=...
SMTP_FROM=TaskFlow <noreply@example.com>
SMTP_TLS=true

# Auth
JWT_SECRET=...
JWT_ACCESS_TTL=900
JWT_REFRESH_TTL=2592000
OAUTH_GOOGLE_CLIENT_ID=...
OAUTH_GOOGLE_CLIENT_SECRET=...
OAUTH_GITHUB_CLIENT_ID=...
OAUTH_GITHUB_CLIENT_SECRET=...

# LDAP (Enterprise)
LDAP_ENABLED=false
LDAP_URL=ldap://ldap.example.com:389
LDAP_BASE_DN=dc=example,dc=com
LDAP_BIND_DN=cn=admin,dc=example,dc=com
LDAP_BIND_PASSWORD=...
LDAP_USER_FILTER=(uid={{username}})
LDAP_GROUP_FILTER=(memberOf=cn={{group}},ou=groups,dc=example,dc=com)
LDAP_SYNC_INTERVAL=3600

# Application
APP_URL=https://taskflow.example.com
APP_SECRET=...
APP_ENV=production
APP_LOG_LEVEL=info

# Encryption
ENCRYPTION_KEY=...  # AES-256 key for encrypting secrets

# Monitoring
HEALTH_CHECK_ENABLED=true
METRICS_ENABLED=true
METRICS_PORT=9090

# License (self-hosted)
LICENSE_KEY=...
```

---

## 2. Доменная модель

### Value Objects

| VO | Тип | Описание |
|---|---|---|
| `SystemMode` | Enum | `NORMAL`, `MAINTENANCE`, `READ_ONLY` |
| `FeatureFlagStatus` | Enum | `ENABLED`, `DISABLED`, `SCHEDULED` |
| `RolloutPercentage` | frozen dataclass | value: int (0–100) |
| `FeatureFlagConditionType` | Enum | `ORGANIZATION`, `WORKSPACE`, `USER`, `PERCENTAGE`, `DATE_RANGE` |
| `TemplateType` | Enum | `PROJECT`, `WORKSPACE`, `TASK`, `SPRINT` |
| `EmailTemplateType` | Enum | `WELCOME`, `PASSWORD_RESET`, `INVITATION`, `VERIFICATION`, `NOTIFICATION` |
| `SettingsScope` | Enum | `GLOBAL`, `ORGANIZATION`, `WORKSPACE` |
| `WebhookEventType` | Enum | `TASK_CREATED`, `TASK_UPDATED`, `PROJECT_CREATED`, etc. |
| `WebhookStatus` | Enum | `ACTIVE`, `INACTIVE`, `FAILED` |
| `HealthCheckType` | Enum | `DATABASE`, `REDIS`, `S3`, `SMTP`, `LDAP` |
| `LanguageCode` | frozen dataclass | code: str (ISO 639-1) |

#### VO Groups

```python
class SmtpConfig:
    host: str
    port: int
    user: str
    password: str  # encrypted
    from_address: str
    tls: bool

class LdapConfig:
    url: str
    base_dn: str
    bind_dn: str
    bind_password: str  # encrypted
    user_filter: str
    group_filter: str
    sync_interval_seconds: int

class SsoConfig:
    provider: SsoProvider  # SAML, OIDC
    metadata_url: str | None
    client_id: str | None
    client_secret: str | None  # encrypted
    is_enabled: bool
```

### Entities

| Сущность | Поля | Описание |
|---|---|---|
| `FeatureFlagCondition` | condition_type: FeatureFlagConditionType, target_ids: list[Id] \| None, percentage: RolloutPercentage \| None, date_range: tuple[datetime, datetime] \| None | Условие флага |
| `EmailTemplate` | key: str, template_type: EmailTemplateType, subject, body_html, body_text, variables: list[str], is_custom: bool | Email-шаблон |
| `MaintenanceConfig` | is_active: bool, message: str, whitelist_ips: list[str], scheduled_start \| None, scheduled_end \| None | Конфиг maintenance |
| `WebhookConfig` | url: str, events: list[WebhookEventType], secret: str, status: WebhookStatus, last_delivery_at \| None | Webhook |
| `WebhookDelivery` | event_type, payload: dict, response_status: int \| None, delivered_at, error \| None | Доставка webhook |
| `HealthCheck` | check_type: HealthCheckType, status: str, response_time_ms: int \| None, checked_at | Проверка здоровья |

### Aggregates

#### SystemSettings (Aggregate Root)

Поля:
- scope: SettingsScope
- scope_id: Id | None (org_id / ws_id)
- settings: dict[str, Setting] — key → value, type, category, description, is_sensitive
- smtp: SmtpConfig | None
- ldap: LdapConfig | None
- sso: SsoConfig | None
- maintenance: MaintenanceConfig
- system_mode: SystemMode
- webhooks: list[WebhookConfig]
- updated_by: Id | None
- updated_at: datetime

Методы:
- `create(scope=GLOBAL)` → `SystemSettings` (factory, defaults)
- `set(key, value)` / `get(key)` / `delete(key)`
- `update_smtp(config)` / `update_ldap(config)` / `update_sso(config)`
- `activate_maintenance(message, whitelist_ips, scheduled_end=None)` / `deactivate_maintenance()`
- `add_webhook(url, events, secret)` / `remove_webhook(webhook_id)` / `update_webhook_status(webhook_id, status)`

Инварианты:
- Нижний scope переопределяет верхний (workspace > org > global)
- Sensitive settings маскируются в UI
- Maintenance mode: все API возвращают 503 кроме /health и /admin
- Settings кешируются в Redis

#### FeatureFlag (Aggregate Root)

Поля:
- key: str (unique)
- name: str
- description: str | None
- status: FeatureFlagStatus
- conditions: list[FeatureFlagCondition]
- scheduled_enable_at: datetime | None
- scheduled_disable_at: datetime | None
- created_by: Id
- created_at: datetime
- updated_at: datetime

Методы:
- `create(key, name, description=None)` → `FeatureFlag` (factory, status=DISABLED)
- `enable()` / `disable()`
- `add_condition(condition)` / `remove_condition(condition_id)`
- `schedule(enable_at=None, disable_at=None)`
- `evaluate(user_id, organization_id=None, workspace_id=None)` → bool
- `delete()`

Инварианты:
- key уникален глобально
- evaluate: status=ENABLED AND (хотя бы одно condition matched)
- Rollout: hash(user_id) % 100 < percentage

#### Template (Aggregate Root)

Поля:
- template_type: TemplateType
- name: str
- description: str | None
- config: dict
- is_system: bool
- created_by: Id
- created_at: datetime
- updated_at: datetime

Методы:
- `create(template_type, name, config, created_by)` → `Template` (is_system=False)
- `update(name=None, config=None)`
- `delete()` — только не-системные

Инварианты:
- Системные шаблоны нельзя удалять

---

## 3. Бизнес-правила

1. **Feature flags**: при проверке — enabled AND (rollout_percentage OR target match)
2. **Rollout**: hash(user_id) % 100 < rollout_percentage → enabled
3. **Maintenance mode**: все API возвращают 503 кроме /health и /admin; whitelist IPs проходят
4. **System settings**: кешируются в Redis; обновление инвалидирует кэш
5. **Email templates**: fallback на default если custom не задан
6. **License (self-hosted)**: проверяется при старте; expired → read-only mode через 14 дней
7. **Health check**: /health endpoint должен проверять DB, Redis, S3 connectivity
8. **LDAP sync**: периодическая синхронизация пользователей; disabled users в LDAP → деактивация

---

## 4. API Endpoints

### 4.1. Admin: Пользователи

*See 02-system-roles.md для управления пользователями*

### 4.2. Admin: Статистика

```
GET /api/v1/admin/stats/overview
```

**Response (200):**
```json
{
  "users": {"total": 5000, "active": 4200, "suspended": 50, "pending": 750},
  "organizations": {"total": 100},
  "workspaces": {"total": 500},
  "projects": {"total": 2000},
  "tasks": {"total": 150000},
  "storage": {"used_bytes": 524288000000, "total_bytes": 1099511627776},
  "subscriptions": {"free": 3000, "start": 1500, "business": 400, "enterprise": 100},
  "dau": 2100,
  "wau": 3500,
  "mau": 4200
}
```

---

```
GET /api/v1/admin/stats/usage
```

**Query params:** `metric` (users/tasks/storage), `period` (day/week/month), `from`, `to`

### 4.3. Feature Flags

```
GET /api/v1/admin/feature-flags
```

---

```
POST /api/v1/admin/feature-flags
```

**Request:**
```json
{
  "key": "messenger_v2",
  "name": "Messenger V2",
  "description": "New messenger with threads",
  "enabled": false,
  "rollout_percentage": 10,
  "target_organizations": ["org_uuid"],
  "scheduled_enable_at": "2025-03-01T00:00:00Z"
}
```

---

```
PATCH /api/v1/admin/feature-flags/{flag_id}
```

---

```
DELETE /api/v1/admin/feature-flags/{flag_id}
```

---

```
GET /api/v1/feature-flags
```
*Client endpoint: возвращает resolved flags для текущего пользователя*

**Response (200):**
```json
{
  "flags": {
    "messenger_v2": true,
    "scrum_module": true,
    "ai_assistant": false
  }
}
```

### 4.4. System Settings

```
GET /api/v1/admin/settings
```

**Query params:** `category`

---

```
PUT /api/v1/admin/settings/{key}
```

**Request:**
```json
{
  "value": "new_value"
}
```

### 4.5. Email Templates

```
GET /api/v1/admin/email-templates
```

---

```
GET /api/v1/admin/email-templates/{key}
```

---

```
PUT /api/v1/admin/email-templates/{key}
```

**Request:**
```json
{
  "subject": "Welcome to {{app_name}}!",
  "body_html": "<h1>Welcome, {{display_name}}!</h1>...",
  "body_text": "Welcome, {{display_name}}! ..."
}
```

---

```
POST /api/v1/admin/email-templates/{key}/preview
```

**Request:**
```json
{
  "variables": {
    "display_name": "John Doe",
    "app_name": "TaskFlow"
  }
}
```

---

```
POST /api/v1/admin/email-templates/{key}/reset
```
*Сброс к default*

### 4.6. Maintenance

```
GET /api/v1/admin/maintenance
```

---

```
PUT /api/v1/admin/maintenance
```

**Request:**
```json
{
  "is_active": true,
  "message": "Scheduled maintenance. We'll be back in 30 minutes.",
  "whitelist_ips": ["10.0.0.0/8"],
  "scheduled_end": "2025-02-01T03:00:00Z"
}
```

### 4.7. Health (public)

```
GET /health
```

**Response (200):**
```json
{
  "status": "healthy",
  "version": "1.5.0",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "s3": "ok"
  },
  "uptime_seconds": 86400
}
```

---

## 5. Схема БД

### Таблица: `feature_flags`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| key | VARCHAR(100) | UNIQUE, NOT NULL | |
| name | VARCHAR(100) | NOT NULL | |
| description | TEXT | NULLABLE | |
| enabled | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| rollout_percentage | INTEGER | NULLABLE | 0–100 |
| target_organizations | JSONB | NULLABLE | [UUID] |
| target_workspaces | JSONB | NULLABLE | [UUID] |
| target_users | JSONB | NULLABLE | [UUID] |
| scheduled_enable_at | TIMESTAMPTZ | NULLABLE | |
| scheduled_disable_at | TIMESTAMPTZ | NULLABLE | |
| created_by | UUID | FK → users.id, NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_ff_key` — UNIQUE на `key`

### Таблица: `system_settings`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| key | VARCHAR(100) | PK | |
| value | TEXT | NOT NULL | |
| type | VARCHAR(10) | NOT NULL | |
| category | VARCHAR(50) | NOT NULL | |
| description | TEXT | NOT NULL | |
| is_sensitive | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| updated_by | UUID | FK → users.id, NULLABLE | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

### Таблица: `email_templates`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| key | VARCHAR(50) | UNIQUE, NOT NULL | |
| name | VARCHAR(100) | NOT NULL | |
| subject | VARCHAR(200) | NOT NULL | |
| body_html | TEXT | NOT NULL | |
| body_text | TEXT | NOT NULL | |
| variables | JSONB | NOT NULL, DEFAULT '[]' | |
| is_custom | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| updated_by | UUID | FK → users.id, NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

### Таблица: `maintenance_windows`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| is_active | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| message | TEXT | NOT NULL | |
| whitelist_ips | JSONB | NOT NULL, DEFAULT '[]' | |
| scheduled_start | TIMESTAMPTZ | NULLABLE | |
| scheduled_end | TIMESTAMPTZ | NULLABLE | |
| activated_by | UUID | FK → users.id, NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

---

## 6. Доменные события

| Событие | Поля | Описание |
|---|---|---|
| `FeatureFlagCreated` | flag_id, key | Флаг создан |
| `FeatureFlagEnabled` | flag_id, key | Флаг включён |
| `FeatureFlagDisabled` | flag_id, key | Флаг выключен |
| `FeatureFlagConditionAdded` | flag_id, condition_type | Условие добавлено |
| `FeatureFlagConditionRemoved` | flag_id, condition_id | Условие удалено |
| `FeatureFlagDeleted` | flag_id, key | Флаг удалён |
| `FeatureFlagScheduled` | flag_id, enable_at \| None, disable_at \| None | Запланировано |
| `SystemSettingUpdated` | key, scope, old_value, new_value | Настройка обновлена |
| `SmtpConfigUpdated` | scope | SMTP обновлён |
| `LdapConfigUpdated` | scope | LDAP обновлён |
| `SsoConfigUpdated` | scope | SSO обновлён |
| `EmailTemplateUpdated` | key | Шаблон обновлён |
| `EmailTemplateReset` | key | Шаблон сброшен |
| `MaintenanceModeActivated` | message | Maintenance включён |
| `MaintenanceModeDeactivated` | | Maintenance выключен |
| `WebhookCreated` | webhook_id, url | Webhook создан |
| `WebhookDelivered` | webhook_id, event_type, response_status | Webhook доставлен |
| `WebhookFailed` | webhook_id, event_type, error | Webhook не удался |
| `TemplateCreated` | template_id, template_type, name | Шаблон создан |
| `TemplateUpdated` | template_id | Шаблон обновлён |
| `TemplateDeleted` | template_id | Шаблон удалён |

---

## 7. Exceptions

| Исключение | Описание |
|---|---|
| `FeatureFlagNotFoundException` | Флаг не найден |
| `DuplicateFeatureFlagKeyException` | Ключ уже существует |
| `SystemSettingNotFoundException` | Настройка не найдена |
| `InvalidSettingValueException` | Некорректное значение настройки |
| `EmailTemplateNotFoundException` | Email-шаблон не найден |
| `TemplateNotFoundException` | Шаблон не найден |
| `CannotDeleteSystemTemplateException` | Системный шаблон нельзя удалить |
| `WebhookNotFoundException` | Webhook не найден |
| `InvalidWebhookUrlException` | Некорректный URL webhook |
| `MaintenanceAlreadyActiveException` | Maintenance уже активен |

---

## 8. Repositories

| Репозиторий | Методы |
|---|---|
| `SystemSettingsRepository` | `get_by_scope`, `get_global`, `get_by_organization`, `get_by_workspace` |
| `FeatureFlagRepository` | `get_by_id`, `get_by_key`, `get_all`, `get_enabled`, `get_scheduled` |
| `TemplateRepository` | `get_by_id`, `get_by_type`, `get_system`, `get_custom` |
| `EmailTemplateRepository` | `get_by_key`, `get_all`, `get_custom` |
