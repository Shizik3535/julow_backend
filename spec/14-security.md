# 14. Security — Безопасность

## Обзор

Контекст безопасности охватывает шифрование данных, compliance (GDPR, SOC 2, ISO 27001, HIPAA), audit logging и мониторинг подозрительной активности. Это cross-cutting concern, который влияет на все остальные контексты.

---

## Принципы расширяемости

1. **AuditAction — расширяемый enum** — новые действия = значение enum. AuditResource — строка с валидацией.
2. **SecurityEventType — enum** — типы подозрительной активности. Новые детекторы = значение enum + handler.
3. **DataSubjectRequestType — enum** — GDPR/CCPA запросы.
4. **SecurityPolicy — AR** — политики безопасности (password, session, IP, retention, backup, encryption).
5. **SecurityIncident — AR** — инциденты безопасности с жизненным циклом.
6. **ComplianceConfig — entity** — конфигурация соответствия стандартам.

---

## 1. Функциональные требования

### 1.1. Защита данных

| Требование | Free | Start | Business | Enterprise |
|-----------|------|-------|----------|------------|
| TLS 1.3 (in transit) | ✅ | ✅ | ✅ | ✅ |
| AES-256 (at rest) | ✅ | ✅ | ✅ | ✅ |
| Шифрование бэкапов | ✅ | ✅ | ✅ | ✅ |
| Data residency (выбор региона) | ❌ | ❌ | ❌ | ✅ |
| Автоматические бэкапы | ✅ daily | ✅ daily | ✅ 2×day | ✅ настр. |
| Disaster Recovery Plan | ❌ | ❌ | ✅ | ✅ |
| Encryption key management | Platform | Platform | Platform | Customer-managed |

### 1.2. Compliance

| Стандарт | Free | Start | Business | Enterprise |
|----------|------|-------|----------|------------|
| GDPR | ✅ | ✅ | ✅ | ✅ |
| SOC 2 Type II | — | — | ✅ | ✅ |
| ISO 27001 | — | — | ✅ | ✅ |
| HIPAA | — | — | ❌ | ✅ |
| CCPA | ✅ | ✅ | ✅ | ✅ |
| Cookie consent | ✅ | ✅ | ✅ | ✅ |

### GDPR-специфичные требования
- Право на удаление (right to erasure) — полное удаление данных пользователя
- Право на экспорт (data portability) — экспорт всех данных пользователя
- DPA (Data Processing Agreement) — для Business/Enterprise
- Согласие на обработку данных (consent management)
- Cookie consent banner

### 1.3. Audit & Monitoring

| Требование | Free | Start | Business | Enterprise |
|-----------|------|-------|----------|------------|
| Audit log | ❌ | ❌ | ⚡ 90 дней | ✅ ∞ |
| Фильтрация audit log | — | — | ✅ | ✅ |
| Поиск по audit log | — | — | ✅ | ✅ |
| Экспорт audit log | — | — | ✅ | ✅ |
| Мониторинг подозрительной активности | ❌ | ❌ | ✅ | ✅ |
| Security event notifications | ✅ | ✅ | ✅ | ✅ |
| Penetration testing | — | — | Ежегодно | Ежеквартально |
| Bug bounty | — | — | — | ✅ |

**Audit log записывает:**
- Кто (user_id, email, IP)
- Что (action, resource_type, resource_id)
- Когда (timestamp)
- Откуда (IP, user_agent, geo)
- Детали (old_value, new_value)

**Отслеживаемые действия:**
- Аутентификация (login, logout, failed login, 2FA)
- Управление пользователями (create, update, delete, role change)
- Организация / Workspace (create, update, delete, member changes)
- Проекты (create, update, delete, member changes)
- Задачи (create, update, delete — только metadata, не content)
- Настройки безопасности (SSO, 2FA policy, IP whitelist)
- Файлы (upload, download, delete)
- Экспорт данных
- Биллинг (subscription changes, payments)
- Admin actions

---

## 2. Доменная модель

### Value Objects

| VO | Тип | Описание |
|---|---|---|
| `AuditAction` | Enum | `LOGIN`, `LOGOUT`, `LOGIN_FAILED`, `2FA_ENABLED`, `2FA_DISABLED`, `PASSWORD_CHANGED`, `PASSWORD_RESET`, `SESSION_TERMINATED`, `USER_CREATED`, `USER_UPDATED`, `USER_SUSPENDED`, `USER_DELETED`, `ROLE_CHANGED`, `ORG_CREATED`, `ORG_UPDATED`, `ORG_DELETED`, `ORG_MEMBER_ADDED`, `ORG_MEMBER_REMOVED`, `WS_CREATED`, `WS_UPDATED`, `WS_DELETED`, `WS_MEMBER_ADDED`, `WS_MEMBER_REMOVED`, `PROJECT_CREATED`, `PROJECT_UPDATED`, `PROJECT_DELETED`, `TASK_CREATED`, `TASK_DELETED`, `FILE_UPLOADED`, `FILE_DOWNLOADED`, `FILE_DELETED`, `DATA_EXPORTED`, `DATA_IMPORTED`, `SUBSCRIPTION_CHANGED`, `PAYMENT_PROCESSED`, `SYSTEM_SETTING_CHANGED`, `FEATURE_FLAG_CHANGED`, `MAINTENANCE_MODE_TOGGLED` |
| `AuditResource` | str (validated) | `"user"`, `"organization"`, `"workspace"`, `"project"`, `"task"`, etc. |
| `Severity` | Enum | `INFO`, `WARNING`, `CRITICAL` |
| `SecurityEventType` | Enum | `BRUTE_FORCE`, `SUSPICIOUS_LOGIN`, `IMPOSSIBLE_TRAVEL`, `MASS_DATA_ACCESS`, `PRIVILEGE_ESCALATION`, `UNUSUAL_EXPORT`, `ACCOUNT_TAKEOVER` |
| `ComplianceStandard` | Enum | `GDPR`, `SOC2`, `ISO27001`, `HIPAA`, `CCPA` |
| `DataRegion` | Enum | `EU`, `US`, `ASIA` |
| `IpAddress` | frozen dataclass | value: str (validated IPv4/IPv6) |
| `IncidentStatus` | Enum | `OPEN`, `INVESTIGATING`, `RESOLVED`, `DISMISSED` |
| `IncidentSeverity` | Enum | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `DataSubjectRequestType` | Enum | `DATA_EXPORT`, `DATA_DELETION`, `CONSENT_WITHDRAWAL` |
| `DataSubjectRequestStatus` | Enum | `PENDING`, `PROCESSING`, `COMPLETED`, `FAILED` |
| `BackupType` | Enum | `FULL`, `INCREMENTAL` |
| `BackupStatus` | Enum | `SCHEDULED`, `RUNNING`, `COMPLETED`, `FAILED` |
| `EncryptionAlgorithm` | Enum | `AES_256_GCM`, `AES_256_CBC` |

#### VO Groups

```python
class PasswordPolicyConfig:
    min_length: int  # default 8
    require_uppercase: bool
    require_lowercase: bool
    require_digits: bool
    require_special: bool
    max_age_days: int | None  # None = no expiry
    history_count: int  # prevent reuse of last N passwords

class SessionPolicyConfig:
    max_sessions: int
    idle_timeout_minutes: int
    absolute_timeout_hours: int

class RetentionPolicyConfig:
    audit_log_days: int  # 90 for Business, unlimited for Enterprise
    backup_retention_days: int
```

### Entities

| Сущность | Поля | Описание |
|---|---|---|
| `SecurityEvent` | type: SecurityEventType, severity: IncidentSeverity, ip: IpAddress, user_id: Id \| None, details: dict, detected_at | Событие безопасности |
| `ComplianceConfig` | standard: ComplianceStandard, is_enabled: bool, settings: dict | Конфигурация соответствия |
| `IpRule` | ip_pattern: str, type: IpRuleType (ALLOW/DENY), description | IP-правило |
| `BackupSchedule` | frequency: str, time: time, retention_days: int, is_encrypted: bool | Расписание бэкапов |
| `BackupRecord` | backup_type: BackupType, status: BackupStatus, size_bytes: int \| None, started_at, completed_at \| None | Запись бэкапа |
| `EncryptionConfig` | algorithm: EncryptionAlgorithm, key_provider: str, key_ref: str | Конфиг шифрования |
| `IncidentNote` | author_id: Id, content: str, created_at | Заметка к инциденту |

### Aggregates

#### AuditLog (Aggregate Root)

Поля:
- workspace_id: Id | None
- organization_id: Id | None
- actor_id: Id | None
- actor_email: str
- actor_ip: IpAddress
- actor_user_agent: str
- actor_geo_country: str | None
- actor_geo_city: str | None
- action: AuditAction
- resource_type: AuditResource
- resource_id: Id | None
- resource_name: str | None
- details: dict
- old_values: dict | None
- new_values: dict | None
- severity: Severity
- created_at: datetime

Методы:
- `create(action, resource_type, actor_id, actor_email, actor_ip, ...)` → `AuditLog` (factory)

Инварианты:
- Append-only, никогда не удаляется (кроме retention)
- Пароли и токены никогда не логируются
- Task content не логируется — только metadata

#### SecurityPolicy (Aggregate Root)

Поля:
- organization_id: Id (opaque)
- password_policy: PasswordPolicyConfig
- session_policy: SessionPolicyConfig
- retention_policy: RetentionPolicyConfig
- ip_rules: list[IpRule]
- compliance_configs: list[ComplianceConfig]
- data_region: DataRegion | None
- encryption: EncryptionConfig
- backup_schedule: BackupSchedule | None
- backup_records: list[BackupRecord]
- created_at: datetime
- updated_at: datetime

Методы:
- `create(organization_id)` → `SecurityPolicy` (factory, defaults)
- `update_password_policy(config)` / `update_session_policy(config)` / `update_retention_policy(config)`
- `add_ip_rule(pattern, type, description)` / `remove_ip_rule(rule_id)`
- `enable_compliance(standard)` / `disable_compliance(standard)`
- `set_data_region(region)` / `update_encryption(config)`
- `set_backup_schedule(schedule)` / `start_backup(type)` / `complete_backup(record_id)` / `fail_backup(record_id)`

Инварианты:
- Data residency — только Enterprise
- Customer-managed keys — только Enterprise
- HIPAA compliance — только Enterprise

#### SecurityIncident (Aggregate Root)

Поля:
- workspace_id: Id | None
- user_id: Id | None
- type: SecurityEventType
- severity: IncidentSeverity
- title: str
- description: str
- events: list[SecurityEvent]
- notes: list[IncidentNote]
- status: IncidentStatus
- resolved_by: Id | None
- resolved_at: datetime | None
- created_at: datetime

Методы:
- `create(type, severity, title, description, initial_event)` → `SecurityIncident` (factory, status=OPEN)
- `add_event(event)` / `add_note(author_id, content)`
- `investigate()` → status=INVESTIGATING
- `resolve(resolved_by)` → status=RESOLVED
- `dismiss(dismissed_by)` → status=DISMISSED
- `reopen()` → status=OPEN

Инварианты:
- RESOLVED/DISMISSED можно reopen
- CRITICAL инциденты нельзя dismiss (only resolve)

---

## 3. Бизнес-правила

### Audit Log
1. Audit log — append-only, никогда не удаляется (кроме retention policy)
2. Retention: Business — 90 дней, Enterprise — бессрочно (или настраиваемо)
3. Sensitive data: пароли и токены никогда не логируются в audit
4. Task content (description, comments) не логируется — только metadata (created, deleted)

### Security Monitoring
5. Brute force: > 10 неудачных логинов с одного IP за 10 минут → alert
6. Impossible travel: логин из другой страны менее чем через 1 час → alert
7. Mass data access: > 1000 файлов скачано за час → alert
8. Unusual export: экспорт всех данных workspace → alert (для Business/Enterprise)

### GDPR
9. Data export: генерируется в течение 72 часов (по закону — 30 дней)
10. Data deletion: мягкое удаление немедленно, физическое — через 30 дней
11. При data deletion: удаляются все данные пользователя, анонимизируются комментарии и history
12. Consent withdrawal: отключение маркетинговых email, но не системных

### Encryption
13. At rest: AES-256-GCM для БД, S3 server-side encryption
14. In transit: TLS 1.3 minimum, HSTS enabled
15. Secrets (tokens, keys, passwords): Argon2id или AES-256 в зависимости от типа
16. Customer-managed keys (Enterprise): интеграция с AWS KMS / HashiCorp Vault

---

## 4. API Endpoints

### 4.1. Audit Log

```
GET /api/v1/workspaces/{ws_id}/audit-log
```

**Query params:** `from`, `to`, `actor_id`, `action`, `resource_type`, `resource_id`, `severity`, `search`, `page`, `limit`

**Response (200):**
```json
{
  "items": [
    {
      "id": "uuid",
      "actor": {"id": "uuid", "email": "john@example.com"},
      "actor_ip": "192.168.1.1",
      "actor_geo": "Moscow, Russia",
      "action": "project_created",
      "resource_type": "project",
      "resource_id": "project_uuid",
      "resource_name": "Backend API",
      "details": {"methodology": "scrum"},
      "severity": "info",
      "created_at": "2025-02-01T10:00:00Z"
    }
  ],
  "total": 500,
  "page": 1,
  "limit": 50
}
```

---

```
GET /api/v1/organizations/{org_id}/audit-log
```
*Audit log на уровне организации*

---

```
POST /api/v1/workspaces/{ws_id}/audit-log/export
```

**Request:**
```json
{
  "from": "2025-01-01",
  "to": "2025-02-28",
  "format": "csv"
}
```

### 4.2. Security Alerts

```
GET /api/v1/admin/security/alerts
```

**Query params:** `type`, `severity`, `status`, `page`, `limit`

---

```
PATCH /api/v1/admin/security/alerts/{alert_id}
```

**Request:**
```json
{
  "status": "resolved",
  "notes": "False positive, user was on VPN"
}
```

### 4.3. GDPR

```
POST /api/v1/users/me/gdpr/export
```

**Response (202):**
```json
{
  "request_id": "uuid",
  "status": "pending",
  "estimated_completion": "2025-02-03T10:00:00Z"
}
```

---

```
GET /api/v1/users/me/gdpr/requests
```

---

```
GET /api/v1/users/me/gdpr/requests/{request_id}
```

---

```
POST /api/v1/users/me/gdpr/delete
```
*Запрос на удаление всех данных*

**Request:**
```json
{
  "confirmation": "DELETE MY DATA",
  "password": "current_password"
}
```

---

```
GET /api/v1/admin/gdpr/requests
```
*Admin: просмотр всех GDPR-запросов*

---

```
POST /api/v1/admin/gdpr/requests/{request_id}/process
```

---

## 5. Схема БД

### Таблица: `audit_log`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| workspace_id | UUID | NULLABLE | |
| organization_id | UUID | NULLABLE | |
| actor_id | UUID | NULLABLE | |
| actor_email | VARCHAR(255) | NOT NULL | |
| actor_ip | VARCHAR(45) | NOT NULL | |
| actor_user_agent | TEXT | NOT NULL | |
| actor_geo_country | VARCHAR(100) | NULLABLE | |
| actor_geo_city | VARCHAR(100) | NULLABLE | |
| action | VARCHAR(50) | NOT NULL | |
| resource_type | VARCHAR(30) | NOT NULL | |
| resource_id | UUID | NULLABLE | |
| resource_name | VARCHAR(200) | NULLABLE | |
| details | JSONB | NOT NULL, DEFAULT '{}' | |
| old_values | JSONB | NULLABLE | |
| new_values | JSONB | NULLABLE | |
| severity | VARCHAR(10) | NOT NULL, DEFAULT 'info' | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_audit_ws` — на `workspace_id`
- `idx_audit_org` — на `organization_id`
- `idx_audit_actor` — на `actor_id`
- `idx_audit_action` — на `action`
- `idx_audit_resource` — на `(resource_type, resource_id)`
- `idx_audit_created` — на `created_at`
- `idx_audit_ws_created` — на `(workspace_id, created_at DESC)`

*Рекомендация: использовать partitioned table по месяцам для масштабируемости.*

### Таблица: `security_alerts`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| workspace_id | UUID | NULLABLE | |
| user_id | UUID | NULLABLE | |
| type | VARCHAR(30) | NOT NULL | |
| severity | VARCHAR(10) | NOT NULL | |
| title | VARCHAR(200) | NOT NULL | |
| description | TEXT | NOT NULL | |
| details | JSONB | NOT NULL, DEFAULT '{}' | |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'open' | |
| resolved_by | UUID | FK → users.id, NULLABLE | |
| resolved_at | TIMESTAMPTZ | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_sa_status` — на `status`
- `idx_sa_severity` — на `severity`
- `idx_sa_type` — на `type`

### Таблица: `gdpr_requests`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| user_id | UUID | FK → users.id, NOT NULL | |
| type | VARCHAR(20) | NOT NULL | |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | |
| result_file_id | UUID | FK → files.id, NULLABLE | |
| notes | TEXT | NULLABLE | |
| processed_by | UUID | FK → users.id, NULLABLE | |
| requested_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| processed_at | TIMESTAMPTZ | NULLABLE | |
| completed_at | TIMESTAMPTZ | NULLABLE | |

**Индексы:**
- `idx_gdpr_user` — на `user_id`
- `idx_gdpr_status` — на `status`

---

## 6. Доменные события

| Событие | Поля | Описание |
|---|---|---|
| `AuditLogCreated` | entry_id, action, resource_type, resource_id, actor_id | Audit-запись |
| `SecurityIncidentCreated` | incident_id, type, severity | Инцидент создан |
| `SecurityIncidentResolved` | incident_id, resolved_by | Инцидент разрешён |
| `SecurityIncidentDismissed` | incident_id, dismissed_by | Инцидент отклонён |
| `SecurityIncidentReopened` | incident_id | Инцидент переоткрыт |
| `SuspiciousActivityDetected` | user_id, ip, event_type | Подозрительная активность |
| `SecurityPolicyUpdated` | organization_id, changed_fields: list[str] | Политика обновлена |
| `IpRuleAdded` | organization_id, ip_pattern, rule_type | IP-правило |
| `IpRuleRemoved` | organization_id, rule_id | IP-правило удалено |
| `DataSubjectRequestCreated` | request_id, user_id, request_type | GDPR-запрос |
| `DataSubjectRequestCompleted` | request_id, user_id | Запрос выполнен |
| `DataSubjectRequestFailed` | request_id, error | Запрос не удался |
| `BackupStarted` | backup_id, backup_type | Бэкап начат |
| `BackupCompleted` | backup_id, size_bytes | Бэкап завершён |
| `BackupFailed` | backup_id, error | Бэкап не удался |

---

## 7. Exceptions

| Исключение | Описание |
|---|---|
| `AuditLogNotFoundException` | Запись не найдена |
| `SecurityIncidentNotFoundException` | Инцидент не найден |
| `CannotDismissCriticalIncidentException` | CRITICAL нельзя dismiss |
| `SecurityPolicyNotFoundException` | Политика не найдена |
| `InvalidIpPatternException` | Некорректный IP-паттерн |
| `DataSubjectRequestNotFoundException` | GDPR-запрос не найден |
| `DataSubjectRequestAlreadyProcessedException` | Запрос уже обработан |
| `BackupFailedException` | Бэкап не удался |
| `ComplianceNotAvailableException` | Стандарт недоступен на тарифе |
| `DataRegionNotAvailableException` | Data residency недоступен |

---

## 8. Repositories

| Репозиторий | Методы |
|---|---|
| `AuditLogRepository` | `get_by_id`, `get_by_workspace`, `get_by_organization`, `get_by_actor`, `get_by_action`, `get_by_resource`, `get_by_date_range`, `search`, `count_by_action` |
| `SecurityIncidentRepository` | `get_by_id`, `get_by_status`, `get_by_severity`, `get_by_type`, `get_open`, `get_by_workspace` |
| `SecurityPolicyRepository` | `get_by_organization` |
| `DataSubjectRequestRepository` | `get_by_id`, `get_by_user`, `get_by_status`, `get_pending` |
