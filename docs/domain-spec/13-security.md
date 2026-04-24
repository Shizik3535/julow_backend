# Security BC — Спецификация

> Путь: `app/context/security/domain`
> Исходные требования: §14 (Безопасность)

## Контекст

Security BC отвечает за audit log, compliance, data residency, мониторинг подозрительной активности, запросы на экспорт/удаление данных (GDPR/CCPA), политики безопасности, инциденты безопасности, шифрование и бэкапы. Шифрование и бэкапы — infrastructure слой, но события о них проходят через этот BC.

---

## Принципы расширяемости

1. **AuditAction/AuditResource — расширяемые enum** — новые действия и ресурсы = значение enum.
2. **SecurityEventType — enum** — вместо магической строки `event_type: str`.
3. **ComplianceConfig.settings — VO group** — вместо нетипизированного `dict`.
4. **DataResidency — enum для region/country** — вместо магических строк.
5. **DataSubjectRequest — AR** — GDPR/CCPA запросы с полным жизненным циклом.
6. **SecurityPolicy — AR** — политики безопасности (password, session, IP). Новые политики = расширение.
7. **SecurityIncident — AR** — инциденты с расследованием. Новые типы инцидентов = значение enum.
8. **BackupSchedule — entity** — расписание бэкапов. Новые типы бэкапов = расширение.

---

## Value Objects

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `AuditAction` | Enum | `CREATE`, `READ`, `UPDATE`, `DELETE`, `LOGIN`, `LOGOUT`, `LOGIN_FAILED`, `EXPORT`, `SHARE`, `CONFIG_CHANGE`, `MFA_ENABLED`, `MFA_DISABLED`, `PASSWORD_CHANGE`, `ROLE_CHANGE`, `API_KEY_CREATED`, `API_KEY_REVOKED`, `PERMISSION_CHANGE`, `DATA_EXPORT`, `DATA_DELETE` | §14.3 |
| `AuditResource` | Enum | `USER`, `ORGANIZATION`, `WORKSPACE`, `PROJECT`, `TASK`, `FILE`, `COMMENT`, `CHAT`, `MEETING`, `TIME_ENTRY`, `INVOICE`, `SUBSCRIPTION`, `PLAN`, `SYSTEM`, `API_KEY`, `SECURITY_POLICY` | §14.3 |
| `Severity` | Enum | `INFO`, `WARNING`, `HIGH`, `CRITICAL` | §14.3 |
| `SecurityEventType` | Enum | `BRUTE_FORCE`, `SUSPICIOUS_LOGIN`, `PRIVILEGE_ESCALATION`, `DATA_EXFILTRATION`, `UNAUTHORIZED_ACCESS`, `CONFIG_DRIFT`, `COMPLIANCE_VIOLATION`, `ENCRYPTION_FAILURE`, `BACKUP_FAILURE`, `OTHER` | §14.3 |
| `ComplianceStandard` | Enum | `GDPR`, `SOC2`, `ISO27001`, `HIPAA`, `CCPA`, `PCI_DSS`, `FEDRAMP` | §14.2 |
| `DataRegion` | Enum | `EU_WEST`, `EU_CENTRAL`, `US_EAST`, `US_WEST`, `AP_SOUTHEAST`, `RU_CENTRAL` | §14.1 |
| `DataResidency` | frozen dataclass | region: DataRegion, country_code: str (ISO 3166-1 alpha-2) | §14.1 |
| `IpAddress` | frozen dataclass | value: str (validated IPv4/IPv6) | §14.3 |
| `IncidentStatus` | Enum | `OPEN`, `INVESTIGATING`, `MITIGATED`, `RESOLVED`, `FALSE_POSITIVE` | §14.3 |
| `IncidentSeverity` | Enum | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` | §14.3 |
| `DataSubjectRequestType` | Enum | `EXPORT`, `DELETION`, `CORRECTION`, `RESTRICTION`, `OBJECTION` | §14.2 |
| `DataSubjectRequestStatus` | Enum | `PENDING`, `IN_PROGRESS`, `COMPLETED`, `REJECTED` | §14.2 |
| `BackupType` | Enum | `FULL`, `INCREMENTAL`, `SNAPSHOT` | §14.1 |
| `BackupStatus` | Enum | `PENDING`, `IN_PROGRESS`, `COMPLETED`, `FAILED` | §14.1 |
| `EncryptionAlgorithm` | Enum | `AES_256_GCM`, `AES_256_CBC`, `CHACHA20_POLY1305` | §14.1 |
| `PasswordPolicyConfig` | frozen dataclass | min_length: int, require_uppercase: bool, require_lowercase: bool, require_digit: bool, require_special: bool, max_age_days: int \| None, history_count: int \| None | §14.1 |
| `SessionPolicyConfig` | frozen dataclass | max_duration_minutes: int \| None, idle_timeout_minutes: int \| None, enforce_single_session: bool | §14.1 |
| `RetentionPolicyConfig` | frozen dataclass | audit_log_days: int, security_events_days: int, backup_retention_days: int | §14.1 |

> **`AuditAction`** — расширяемый enum. Новые действия (например, `SUDO_ACTION`, `IMPERSONATE`) = значение enum.
>
> **`AuditResource`** — расширяемый enum. Новые ресурсы (например, `BILLING`, `NOTIFICATION`) = значение enum.
>
> **`SecurityEventType`** — типизированная замена `event_type: str`. Новые типы событий = значение enum. `OTHER` — fallback.
>
> **`Severity`** — добавлен `HIGH` между WARNING и CRITICAL.
>
> **`DataRegion`** — enum вместо `region: str`. Новые регионы = значение enum. Определяет, где физически хранятся данные.
>
> **`DataResidency`** — `country_code` — ISO 3166-1 alpha-2 (RU, US, DE и т.д.). `region` — DataRegion enum.
>
> **`IncidentStatus`** — жизненный цикл инцидента. `FALSE_POSITIVE` — ложное срабатывание.
>
> **`DataSubjectRequestType`** — типы запросов субъекта данных по GDPR. `CORRECTION` — исправление данных, `RESTRICTION` — ограничение обработки, `OBJECTION` — возражение против обработки. Новые типы = значение enum.
>
> **`PasswordPolicyConfig`/`SessionPolicyConfig`** — типизированные настройки политик вместо `dict`.
>
> **`RetentionPolicyConfig`** — сроки хранения данных. Настраивается администратором.

## Entities

| Сущность | Поля | Описание | Исходное требование |
|---|---|---|---|
| `SecurityEvent` | id: Id, event_type: SecurityEventType, severity: IncidentSeverity, details: dict[str, str], is_resolved: bool, resolved_at: datetime \| None, resolved_by: Id \| None | Событие безопасности | §14.3 |
| `ComplianceConfig` | id: Id, standard: ComplianceStandard, is_enabled: bool, settings: ComplianceSettings | Настройка compliance | §14.2 |
| `ComplianceSettings` | data_residency: DataResidency \| None, require_encryption_at_rest: bool, require_encryption_in_transit: bool, require_mfa: bool, audit_log_retention_days: int, data_retention_days: int \| None, allowed_ip_ranges: list[str] \| None | Настройки compliance стандарта | §14.2 |
| `IpRule` | id: Id, ip_range: str (CIDR), rule_type: IpRuleType, description: str \| None, created_by: Id, created_at: datetime | Правило IP доступа | §14.1 |
| `IpRuleType` | Enum | `WHITELIST`, `BLACKLIST` | §14.1 |
| `BackupSchedule` | id: Id, backup_type: BackupType, frequency: BackupFrequency, retention_days: int, is_active: bool, next_run_at: datetime \| None | Расписание бэкапов | §14.1 |
| `BackupFrequency` | Enum | `DAILY`, `WEEKLY`, `MONTHLY` | §14.1 |
| `BackupRecord` | id: Id, backup_type: BackupType, status: BackupStatus, started_at: datetime, completed_at: datetime \| None, size_bytes: int \| None, storage_path: str \| None, error_message: str \| None | Запись о бэкапе | §14.1 |
| `EncryptionConfig` | id: Id, algorithm: EncryptionAlgorithm, key_rotation_days: int \| None, is_at_rest: bool, is_in_transit: bool | Настройки шифрования | §14.1 |
| `IncidentNote` | id: Id, author_id: Id, content: str, created_at: datetime | Заметка к инциденту | §14.3 |

> **`SecurityEvent`** — `event_type: SecurityEventType` вместо `str`. `resolved_by` — кто разрешил событие. `details: dict[str, str]` — типизированные детали (например, `{"ip": "1.2.3.4", "attempts": "5"}`).
>
> **`ComplianceSettings`** — типизированная замена `settings: dict`. Каждое поле — конкретное требование стандарта. Новые требования = поле на VO.
>
> **`IpRule`** — IP whitelist/blacklist. `ip_range` — CIDR нотация (например, "192.168.1.0/24"). `WHITELIST` — разрешённые IP, `BLACKLIST` — заблокированные.
>
> **`BackupSchedule`** — расписание автоматических бэкапов. `BackupFrequency` — частота. `retention_days` — сколько дней хранить бэкапы.
>
> **`BackupRecord`** — запись о выполненном бэкапе. Связь с infrastructure слоем.
>
> **`EncryptionConfig`** — настройки шифрования. `key_rotation_days` — периодичность ротации ключей.
>
> **`IncidentNote`** — заметки при расследовании инцидента.

## Domain Events

| Событие | Поля | Описание | Исходное требование |
|---|---|---|---|
| `AuditEntryCreated` | actor_id \| None, action: AuditAction, resource_type: AuditResource, resource_id \| None, severity: Severity | Запись аудита создана | §14.3 |
| `SuspiciousActivityDetected` | actor_id \| None, event_type: SecurityEventType, reason: str | Подозрительная активность | §14.3 |
| `SecurityEventOccurred` | event_type: SecurityEventType, severity: IncidentSeverity | Событие безопасности | §14.3 |
| `SecurityEventResolved` | event_id, resolved_by | Событие безопасности разрешено | §14.3 |
| `SecurityIncidentCreated` | incident_id, severity: IncidentSeverity | Инцидент безопасности создан | §14.3 |
| `SecurityIncidentUpdated` | incident_id, changed_fields: list[str] | Инцидент обновлён | §14.3 |
| `SecurityIncidentResolved` | incident_id, resolved_by, resolution: str | Инцидент разрешён | §14.3 |
| `SecurityPolicyUpdated` | policy_id, changed_fields: list[str] | Политика безопасности обновлена | §14.1 |
| `ComplianceViolationDetected` | standard: ComplianceStandard, violation_details: str | Нарушение compliance | §14.2 |
| `DataSubjectRequestCreated` | request_id, user_id, request_type: DataSubjectRequestType | Запрос субъекта данных создан | §14.2 |
| `DataSubjectRequestCompleted` | request_id | Запрос субъекта данных выполнен | §14.2 |
| `DataSubjectRequestRejected` | request_id, reason | Запрос субъекта данных отклонён | §14.2 |
| `BackupCreated` | backup_id, backup_type: BackupType, size_bytes | Бэкап создан | §14.1 |
| `BackupRestored` | backup_id, restored_by | Бэкап восстановлен | §14.1 |
| `BackupFailed` | backup_id, error_message | Бэкап не удался | §14.1 |
| `EncryptionKeyRotated` | encryption_config_id | Ключ шифрования ротирован | §14.1 |
| `IpRuleAdded` | rule_id, rule_type: IpRuleType, ip_range | Правило IP добавлено | §14.1 |
| `IpRuleRemoved` | rule_id | Правило IP удалено | §14.1 |

> **`AuditEntryCreated`** — поля типизированы enum'ами вместо строк.
>
> **`SecurityEventResolved`** — разрешение события безопасности. Отдельный event от `Occurred`.
>
> **`SecurityIncidentCreated/Updated/Resolved`** — жизненный цикл инцидента. `resolution` — описание решения.
>
> **`DataSubjectRequestCreated/Completed/Rejected`** — полный жизненный цикл GDPR/CCPA запросов. `request_type` — тип запроса.
>
> **`BackupFailed`** — отдельный event для неудачных бэкапов. Позволяет реагировать (уведомление администратора).
>
> **`EncryptionKeyRotated`** — ротация ключей шифрования. Позволяет отслеживать compliance.
>
> **`IpRuleAdded/Removed`** — управление IP whitelist/blacklist.

## Exceptions

| Исключение | Описание |
|---|---|
| `AuditLogNotFoundException` | Запись аудита не найдена |
| `SecurityEventNotFoundException` | Событие безопасности не найдено |
| `SecurityIncidentNotFoundException` | Инцидент не найден |
| `SecurityPolicyNotFoundException` | Политика не найдена |
| `DataSubjectRequestNotFoundException` | Запрос субъекта данных не найден |
| `ComplianceViolationException` | Нарушение compliance |
| `ComplianceConfigNotFoundException` | Конфигурация compliance не найдена |
| `DataResidencyViolationException` | Нарушение data residency |
| `CannotExportDataException` | Нельзя экспортировать данные |
| `CannotDeleteDataException` | Нельзя удалить данные |
| `IpRuleNotFoundException` | Правило IP не найдено |
| `DuplicateIpRuleException` | Правило для этого IP диапазона уже существует |
| `InvalidIpRangeException` | Некорректный CIDR диапазон |
| `BackupScheduleNotFoundException` | Расписание бэкапов не найдено |
| `BackupNotFoundException` | Бэкап не найден |
| `EncryptionConfigNotFoundException` | Конфигурация шифрования не найдена |
| `CannotResolveAlreadyResolvedEventException` | Событие уже разрешено |
| `CannotModifyResolvedIncidentException` | Нельзя изменить разрешённый инцидент |
| `DataSubjectRequestAlreadyCompletedException` | Запрос уже выполнен |
| `InvalidDataResidencyException` | Некорректная конфигурация data residency |

## Aggregates

### AuditLog (Aggregate Root)

Поля:
- actor_id: Id | None (может быть система)
- action: AuditAction
- resource_type: AuditResource
- resource_id: Id | None (opaque)
- ip_address: IpAddress | None
- user_agent: str | None
- severity: Severity
- details: dict[str, str]
- workspace_id: Id | None (opaque, из Workspace BC)
- organization_id: Id | None (opaque, из Organization BC)
- occurred_at: datetime

Методы:
- `create(actor_id, action, resource_type, resource_id, ip_address, user_agent, severity, details, workspace_id=None, organization_id=None)` → `AuditLog` (factory)

Инварианты:
- AuditLog immutable — нельзя изменить после создания
- Каждое действие в системе логируется
- IP и user_agent опциональны (для системных действий)
- `details` — произвольные ключ-значение для контекста
- Хотя бы один из `workspace_id`/`organization_id` заполнен (кроме глобальных системных действий)

### SecurityPolicy (Aggregate Root)

Поля:
- workspace_id: Id | None (opaque, None = глобальная политика)
- organization_id: Id | None (opaque, None = глобальная политика)
- password_policy: PasswordPolicyConfig
- session_policy: SessionPolicyConfig
- ip_rules: list[IpRule]
- encryption_config: EncryptionConfig | None
- data_residency: DataResidency | None
- retention_policy: RetentionPolicyConfig
- compliance_configs: list[ComplianceConfig]
- backup_schedules: list[BackupSchedule]
- backup_records: list[BackupRecord]
- is_enforced: bool — политика активна
- created_at: datetime
- updated_at: datetime

Методы:
- `create(workspace_id=None, organization_id=None, password_policy, session_policy)` → `SecurityPolicy` (factory)
- `update_password_policy(config: PasswordPolicyConfig)`
- `update_session_policy(config: SessionPolicyConfig)`
- `add_ip_rule(ip_range, rule_type, description=None, created_by)`
- `remove_ip_rule(rule_id)`
- `set_encryption_config(config: EncryptionConfig)`
- `set_data_residency(residency: DataResidency)`
- `update_retention_policy(config: RetentionPolicyConfig)`
- `add_compliance_config(config: ComplianceConfig)`
- `remove_compliance_config(standard: ComplianceStandard)`
- `update_compliance_settings(standard, settings: ComplianceSettings)`
- `add_backup_schedule(schedule: BackupSchedule)`
- `remove_backup_schedule(schedule_id)`
- `record_backup(record: BackupRecord)`
- `enforce()` / `unenforce()`

Инварианты:
- Хотя бы один из `workspace_id`/`organization_id` задан (или оба None для глобальной)
- `IpRule.ip_range` — валидный CIDR
- `IpRule` уникален по `ip_range` + `rule_type`
- `ComplianceConfig` уникален по `standard` в рамках политики
- `BackupSchedule` уникален по `backup_type` в рамках политики
- Если `data_residency` задана, все данные должны храниться в указанном регионе (проверка на infrastructure слое)

### SecurityIncident (Aggregate Root)

Поля:
- title: str
- event_type: SecurityEventType
- severity: IncidentSeverity
- status: IncidentStatus
- description: str | None
- affected_resource_type: AuditResource | None
- affected_resource_id: Id | None (opaque)
- actor_id: Id | None (кто вызвал инцидент)
- notes: list[IncidentNote]
- resolved_by: Id | None
- resolution: str | None
- workspace_id: Id | None (opaque)
- detected_at: datetime
- resolved_at: datetime | None
- created_at: datetime
- updated_at: datetime

Методы:
- `create(title, event_type, severity, workspace_id=None, description=None, affected_resource_type=None, affected_resource_id=None, actor_id=None)` → `SecurityIncident` (factory, status=OPEN)
- `start_investigation(investigator_id)` — OPEN → INVESTIGATING
- `mitigate(mitigator_id)` — INVESTIGATING → MITIGATED
- `resolve(resolved_by, resolution)` — MITIGATING/INVESTIGATING → RESOLVED
- `mark_false_positive(resolved_by)` — → FALSE_POSITIVE
- `add_note(author_id, content)`
- `update_severity(new_severity)`

Инварианты:
- Статусные переходы: OPEN → INVESTIGATING → MITIGATED → RESOLVED, или → FALSE_POSITIVE из любого статуса
- RESOLVED/FALSE_POSITIVE инцидент нельзя изменить (кроме добавления notes)
- `resolution` обязателен при RESOLVED

### DataSubjectRequest (Aggregate Root)

Поля:
- user_id: Id
- request_type: DataSubjectRequestType
- status: DataSubjectRequestStatus
- description: str | None
- rejection_reason: str | None
- assigned_to: Id | None
- export_file_path: str | None — путь к экспортированным данным
- export_file_expires_at: datetime | None — срок действия ссылки на экспорт
- requested_at: datetime
- completed_at: datetime | None
- created_at: datetime
- updated_at: datetime

Методы:
- `create(user_id, request_type, description=None)` → `DataSubjectRequest` (factory, status=PENDING)
- `assign(assigned_to)`
- `start_processing()` — PENDING → IN_PROGRESS
- `complete_export(file_path, expires_at)` — для EXPORT
- `complete_deletion()` — для DELETION
- `complete()` — для CORRECTION/RESTRICTION/OBJECTION
- `reject(reason)` — PENDING → REJECTED
- `is_expired() → bool` — GDPR: 30 дней на обработку

Инварианты:
- GDPR: запрос должен быть обработан в течение 30 дней
- EXPORT — после завершения формируется файл со ссылкой
- DELETION — после завершения данные удаляются из всех BC (app-layer handler)
- REJECTED — должна быть указана причина
- Нельзя повторно завершить уже завершённый запрос

## Repositories

| Репозиторий | Методы |
|---|---|
| `AuditLogRepository` | `get_by_id`, `get_by_actor`, `get_by_resource`, `get_by_workspace`, `get_by_organization`, `get_by_action`, `get_by_date_range`, `search`, `get_suspicious_activity`, `count_by_action` |
| `SecurityPolicyRepository` | `get_by_id`, `get_by_workspace`, `get_by_organization`, `get_global`, `search` |
| `SecurityIncidentRepository` | `get_by_id`, `get_by_workspace`, `get_by_status`, `get_by_severity`, `get_by_event_type`, `search`, `count_open` |
| `DataSubjectRequestRepository` | `get_by_id`, `get_by_user`, `get_by_status`, `get_overdue`, `get_by_type`, `search` |

> **`AuditLogRepository.get_by_action`** — фильтрация по типу действия (например, все `LOGIN_FAILED`).
>
> **`AuditLogRepository.count_by_action`** — подсчёт действий (для детекции аномалий).
>
> **`SecurityPolicyRepository.get_global`** — глобальная политика (workspace_id=None, organization_id=None).
>
> **`SecurityIncidentRepository.count_open`** — количество открытых инцидентов.
>
> **`DataSubjectRequestRepository.get_overdue`** — запросы, не обработанные в течение 30 дней (GDPR compliance).
