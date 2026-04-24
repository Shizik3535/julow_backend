# Administration BC — Спецификация

> Путь: `app/context/administration/domain`
> Исходные требования: §15 (Администрирование)

## Контекст

Administration BC отвечает за admin panel, системные настройки (глобальные и per-workspace/per-organization), feature flags с таргетингом, шаблоны, email-шаблоны, maintenance mode, LDAP/SSO/SMTP конфигурацию, вебхуки, health checks. Для self-hosted версии — управление инфраструктурой.

---

## Принципы расширяемости

1. **SystemSettings — иерархия** — глобальные + per-organization + per-workspace настройки. Workspace наследует от organization, organization от глобальных.
2. **FeatureFlag — AR** — с таргетингом по пользователям/командам/проценту. Новые условия таргетинга = расширение.
3. **EmailTemplateType — enum** — вместо магической строки `template_type: str`.
4. **Template.content — VO** — типизированное содержимое вместо `dict`.
5. **allowed_file_types — FileType enum** — вместо `list[str]`. Синхронизация с FileStorage BC.
6. **WebhookConfig — entity** — исходящие вебхуки. Новые типы событий = расширение.
7. **SsoConfig — VO** — SSO конфигурация (помимо LDAP). Новые провайдеры = расширение.
8. **Credentials — по ссылке** — SMTP/LDAP credentials через vault ref, не в открытом виде.

---

## Value Objects

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `SystemMode` | Enum | `NORMAL`, `MAINTENANCE`, `READ_ONLY` | §15.1 |
| `FeatureFlagStatus` | Enum | `ENABLED`, `DISABLED`, `GRADUAL_ROLLOUT`, `SCHEDULED` | §15.1 |
| `RolloutPercentage` | frozen dataclass | value: int (0–100) | §15.1 |
| `FeatureFlagConditionType` | Enum | `USER_ID`, `TEAM_ID`, `WORKSPACE_ID`, `ORGANIZATION_ID`, `PLAN_TYPE`, `PERCENTAGE`, `CUSTOM_ATTRIBUTE` | §15.1 |
| `TemplateType` | Enum | `PROJECT`, `TASK`, `REPORT`, `EMAIL`, `NOTIFICATION`, `DASHBOARD` | §15.1 |
| `EmailTemplateType` | Enum | `WELCOME`, `PASSWORD_RESET`, `EMAIL_VERIFICATION`, `INVITATION`, `NOTIFICATION_DIGEST`, `BILLING_RECEIPT`, `TRIAL_EXPIRING`, `CUSTOM` | §15.1 |
| `SystemHealth` | Enum | `HEALTHY`, `DEGRADED`, `DOWN`, `UNKNOWN` | §15.2 |
| `SettingsScope` | Enum | `GLOBAL`, `ORGANIZATION`, `WORKSPACE` | §15.1 |
| `SmtpConfig` | frozen dataclass | host: str, port: int, use_tls: bool, username: str \| None, password_ref: str \| None (vault ref), from_email: str, from_name: str \| None | §15.2 |
| `LdapConfig` | frozen dataclass | server_url: str, base_dn: str, bind_dn: str, bind_password_ref: str \| None (vault ref), use_ssl: bool, user_search_filter: str \| None | §15.2 |
| `SsoConfig` | frozen dataclass | provider: SsoProvider, client_id: str, client_secret_ref: str (vault ref), authorization_url: str, token_url: str, userinfo_url: str \| None, scopes: list[str] | §15.2 |
| `SsoProvider` | Enum | `SAML`, `OIDC_GOOGLE`, `OIDC_AZURE`, `OIDC_OKTA`, `OIDC_CUSTOM` | §15.2 |
| `WebhookEventType` | Enum | `TASK_CREATED`, `TASK_COMPLETED`, `COMMENT_ADDED`, `FILE_UPLOADED`, `USER_INVITED`, `PAYMENT_SUCCEEDED`, `PAYMENT_FAILED`, `CUSTOM` | §15.1 |
| `WebhookStatus` | Enum | `ACTIVE`, `DISABLED`, `FAILED` | §15.1 |
| `HealthCheckType` | Enum | `DATABASE`, `REDIS`, `STORAGE`, `SMTP`, `LDAP`, `SSO`, `EXTERNAL_API` | §15.2 |
| `LanguageCode` | Enum | `RU`, `EN`, `DE`, `FR`, `ES`, `ZH`, `JA` | §15.1 |

> **`SystemMode`** — добавлен `READ_ONLY` — система доступна только для чтения (перед maintenance).
>
> **`FeatureFlagStatus`** — добавлен `SCHEDULED` — запланированное включение/выключение (с `scheduled_at`).
>
> **`FeatureFlagConditionType`** — типы условий таргетинга. `CUSTOM_ATTRIBUTE` — произвольный атрибут пользователя. Новые условия = значение enum.
>
> **`TemplateType`** — добавлены `NOTIFICATION`, `DASHBOARD`.
>
> **`EmailTemplateType`** — типизированная замена `template_type: str`. Новые типы email = значение enum. `CUSTOM` — произвольный шаблон.
>
> **`SettingsScope`** — уровень настроек. Глобальные → организация → workspace. Workspace наследует от organization.
>
> **`SmtpConfig`/`LdapConfig`** — `password_ref`/`bind_password_ref` — ссылки на vault, не сами пароли. `from_email`/`from_name` — отправитель.
>
> **`SsoConfig`/`SsoProvider`** — SSO конфигурация. Новые провайдеры = значение enum. `client_secret_ref` — vault ref.
>
> **`WebhookEventType`** — типы событий для вебхуков. `CUSTOM` — произвольное событие. Новые события = значение enum.
>
> **`HealthCheckType`** — типы health checks. Новые проверки = значение enum.

## Entities

| Сущность | Поля | Описание | Исходное требование |
|---|---|---|---|
| `FeatureFlag` | id: Id, key: str, status: FeatureFlagStatus, rollout_percentage: RolloutPercentage \| None, description: str \| None, conditions: list[FeatureFlagCondition], scheduled_at: datetime \| None, created_by: Id, created_at: datetime, updated_at: datetime | Feature flag | §15.1 |
| `FeatureFlagCondition` | id: Id, condition_type: FeatureFlagConditionType, values: list[str] (user_ids, team_ids, etc.), attribute_key: str \| None (для CUSTOM_ATTRIBUTE), attribute_value: str \| None | Условие таргетинга | §15.1 |
| `EmailTemplate` | id: Id, template_type: EmailTemplateType, subject: str, body: str, is_system: bool, language: LanguageCode \| None, variables: list[str] \| None (описание переменных) | Email-шаблон | §15.1 |
| `MaintenanceConfig` | message: str, estimated_end: datetime \| None, allowed_ips: list[str] (CIDR), is_read_only: bool | Конфигурация maintenance | §15.1 |
| `WebhookConfig` | id: Id, url: str, secret: str \| None (для подписи), events: list[WebhookEventType], status: WebhookStatus, description: str \| None, last_delivery_at: datetime \| None, last_failure_at: datetime \| None, failure_count: int, created_by: Id, created_at: datetime, updated_at: datetime | Исходящий вебхук | §15.1 |
| `WebhookDelivery` | id: Id, webhook_id: Id, event_type: WebhookEventType, payload: dict, status_code: int \| None, response_body: str \| None, delivered_at: datetime \| None, next_retry_at: datetime \| None, retry_count: int | Запись доставки вебхука | §15.1 |
| `HealthCheck` | id: Id, check_type: HealthCheckType, name: str, endpoint: str \| None, is_enabled: bool, interval_seconds: int, last_check_at: datetime \| None, last_status: SystemHealth \| None, last_error: str \| None | Проверка здоровья системы | §15.2 |

> **`FeatureFlag`** — стал полноценным entity с `id`, `conditions`, `scheduled_at`. `conditions` — список условий таргетинга (AND логика). `scheduled_at` — для `SCHEDULED` статуса.
>
> **`FeatureFlagCondition`** — условие таргетинга. `condition_type` определяет, что в `values`. Например, `USER_ID` → values = ["user-1", "user-2"], `PERCENTAGE` → values = ["50"], `CUSTOM_ATTRIBUTE` → attribute_key + attribute_value. Новые типы условий = значение enum.
>
> **`EmailTemplate`** — `template_type: EmailTemplateType` вместо `str`. `language` — мультиязычные шаблоны. `variables` — описание переменных шаблона (например, ["user_name", "workspace_name"]).
>
> **`MaintenanceConfig`** — `allowed_ips` в CIDR нотации. `is_read_only` — READ_ONLY режим.
>
> **`WebhookConfig`** — исходящий вебхук. `secret` — для HMAC подписи payload. `failure_count` — при превышении лимита → `FAILED` статус. Новые события = значение в `WebhookEventType`.
>
> **`WebhookDelivery`** — запись каждой попытки доставки. Retry с exponential backoff. `next_retry_at` — следующая попытка.
>
> **`HealthCheck`** — периодическая проверка здоровья. `interval_seconds` — частота. Новые типы проверок = значение enum.

## Domain Events

| Событие | Поля | Описание | Исходное требование |
|---|---|---|---|
| `SystemSettingsUpdated` | settings_id, scope: SettingsScope, changed_fields: list[str] | Системные настройки обновлены | §15.1 |
| `FeatureFlagCreated` | flag_id, key | Feature flag создан | §15.1 |
| `FeatureFlagToggled` | flag_id, key, new_status | Feature flag переключён | §15.1 |
| `FeatureFlagRolloutChanged` | flag_id, key, percentage | Rollout изменён | §15.1 |
| `FeatureFlagConditionAdded` | flag_id, condition_type | Условие таргетинга добавлено | §15.1 |
| `FeatureFlagConditionRemoved` | flag_id, condition_id | Условие таргетинга удалено | §15.1 |
| `FeatureFlagScheduled` | flag_id, scheduled_at | Feature flag запланирован | §15.1 |
| `MaintenanceModeEnabled` | settings_id, is_read_only | Maintenance mode включён | §15.1 |
| `MaintenanceModeDisabled` | settings_id | Maintenance mode отключён | §15.1 |
| `TemplateCreated` | template_id, template_type: TemplateType | Шаблон создан | §15.1 |
| `TemplateUpdated` | template_id, changed_fields: list[str] | Шаблон обновлён | §15.1 |
| `TemplateDeleted` | template_id | Шаблон удалён | §15.1 |
| `EmailTemplateUpdated` | template_id, template_type: EmailTemplateType | Email-шаблон обновлён | §15.1 |
| `SmtpConfigUpdated` | settings_id | SMTP конфигурация обновлена | §15.2 |
| `LdapConfigUpdated` | settings_id | LDAP конфигурация обновлена | §15.2 |
| `SsoConfigUpdated` | settings_id, provider: SsoProvider | SSO конфигурация обновлена | §15.2 |
| `WebhookCreated` | webhook_id, url | Вебхук создан | §15.1 |
| `WebhookUpdated` | webhook_id, changed_fields: list[str] | Вебхук обновлён | §15.1 |
| `WebhookDeleted` | webhook_id | Вебхук удалён | §15.1 |
| `WebhookDeliverySucceeded` | webhook_id, delivery_id | Доставка вебхука успешна | §15.1 |
| `WebhookDeliveryFailed` | webhook_id, delivery_id, status_code | Доставка вебхука не удалась | §15.1 |
| `WebhookDisabled` | webhook_id, reason | Вебхук отключён (много ошибок) | §15.1 |
| `HealthCheckStatusChanged` | check_id, check_type, old_status, new_status | Статус health check изменился | §15.2 |

> **`SystemSettingsUpdated`** — добавлены `scope` и `changed_fields` для гранулярной обработки.
>
> **`FeatureFlagCreated`/`Scheduled`** — новые events для полного жизненного цикла фича-флагов.
>
> **`FeatureFlagConditionAdded/Removed`** — управление условиями таргетинга.
>
> **`SsoConfigUpdated`** — новый event для SSO конфигурации.
>
> **`WebhookCreated/Updated/Deleted`** — управление вебхуками.
>
> **`WebhookDeliverySucceeded/Failed`** — отслеживание доставки. `WebhookDisabled` — автоматическое отключение при множественных ошибках.
>
> **`HealthCheckStatusChanged`** — изменение статуса health check. Позволяет уведомлять администратора о деградации.

## Exceptions

| Исключение | Описание |
|---|---|
| `SystemSettingsNotFoundException` | Настройки не найдены |
| `FeatureFlagNotFoundException` | Feature flag не найден |
| `DuplicateFeatureFlagKeyException` | Ключ флага уже существует |
| `InvalidFeatureFlagConditionException` | Некорректное условие таргетинга |
| `CannotEnableMaintenanceException` | Нельзя включить maintenance |
| `CannotDisableMaintenanceException` | Нельзя отключить maintenance |
| `TemplateNotFoundException` | Шаблон не найден |
| `InvalidTemplateException` | Некорректный шаблон |
| `CannotDeleteSystemTemplateException` | Нельзя удалить системный шаблон |
| `WebhookNotFoundException` | Вебхук не найден |
| `InvalidWebhookUrlException` | Некорректный URL вебхука |
| `WebhookDeliveryFailedException` | Доставка вебхука не удалась |
| `DuplicateWebhookException` | Вебхук с таким URL уже существует |
| `HealthCheckNotFoundException` | Health check не найден |
| `InvalidSmtpConfigException` | Некорректная SMTP конфигурация |
| `InvalidLdapConfigException` | Некорректная LDAP конфигурация |
| `InvalidSsoConfigException` | Некорректная SSO конфигурация |
| `SettingsScopeViolationException` | Нарушение иерархии настроек |

## Aggregates

### SystemSettings (Aggregate Root)

Поля:
- scope: SettingsScope
- organization_id: Id | None (opaque, None для GLOBAL)
- workspace_id: Id | None (opaque, None для GLOBAL/ORGANIZATION)
- system_mode: SystemMode
- maintenance_config: MaintenanceConfig | None
- smtp_config: SmtpConfig | None
- ldap_config: LdapConfig | None
- sso_configs: list[SsoConfig]
- default_language: LanguageCode
- default_timezone: str (IANA timezone)
- max_file_size_mb: int
- allowed_file_types: list[str] — MIME types (синхронизация с FileStorage BC через events)
- webhooks: list[WebhookConfig]
- webhook_deliveries: list[WebhookDelivery]
- health_checks: list[HealthCheck]
- created_at: datetime
- updated_at: datetime

Методы:
- `create_global()` → `SystemSettings` (factory, scope=GLOBAL)
- `create_for_organization(organization_id)` → `SystemSettings` (factory, scope=ORGANIZATION)
- `create_for_workspace(workspace_id, organization_id)` → `SystemSettings` (factory, scope=WORKSPACE)
- `enable_maintenance(message, estimated_end=None, allowed_ips=None, is_read_only=False)`
- `disable_maintenance()`
- `update_smtp(config: SmtpConfig)`
- `update_ldap(config: LdapConfig)`
- `add_sso_config(config: SsoConfig)`
- `remove_sso_config(provider: SsoProvider)`
- `update_file_restrictions(max_size_mb, allowed_types)`
- `update_defaults(language=None, timezone=None)`
- `add_webhook(url, events, secret=None, description=None, created_by)`
- `update_webhook(webhook_id, url=None, events=None, status=None)`
- `remove_webhook(webhook_id)`
- `record_webhook_delivery(delivery: WebhookDelivery)`
- `disable_webhook_on_failures(webhook_id, max_failures=10)` — автоотключение
- `add_health_check(check_type, name, endpoint=None, interval_seconds=60)`
- `remove_health_check(check_id)`
- `update_health_check_status(check_id, status, error=None)`
- `get_effective_settings() → dict` — с учётом наследования (workspace ← organization ← global)

Инварианты:
- GLOBAL — singleton (один экземпляр)
- ORGANIZATION — один экземпляр на organization_id
- WORKSPACE — один экземпляр на workspace_id
- Maintenance mode: `allowed_ips` могут обходить maintenance
- `WebhookConfig.url` — валидный URL
- `WebhookConfig` уникален по URL в рамках настроек
- `SsoConfig` уникален по provider в рамках настроек
- `HealthCheck` уникален по name в рамках настроек
- Иерархия: workspace наследует от organization, organization от GLOBAL
- Workspace не может установить более宽松ные (relaxed) настройки, чем organization

### Template (Aggregate Root)

Поля:
- name: str
- template_type: TemplateType
- content: dict[str, str] — ключ-значение (структура зависит от template_type)
- is_system: bool
- workspace_id: Id | None (opaque, None = глобальный шаблон)
- created_by: Id
- created_at: datetime
- updated_at: datetime

Методы:
- `create(name, template_type, content, created_by, is_system=False, workspace_id=None)` → `Template` (factory)
- `update(content)`
- `delete()` — системные шаблоны нельзя удалить

Инварианты:
- Системные шаблоны (`is_system=True`) нельзя удалять
- Название шаблона уникально в рамках типа и workspace

### FeatureFlag (Aggregate Root)

Поля:
- key: str
- status: FeatureFlagStatus
- rollout_percentage: RolloutPercentage | None
- description: str | None
- conditions: list[FeatureFlagCondition]
- scheduled_at: datetime | None — для SCHEDULED статуса
- is_permanent: bool — постоянный флаг (не удаляется)
- created_by: Id
- created_at: datetime
- updated_at: datetime

Методы:
- `create(key, created_by, description=None, is_permanent=False)` → `FeatureFlag` (factory, status=DISABLED)
- `enable()` — DISABLED/SCHEDULED → ENABLED
- `disable()` — ENABLED/GRADUAL_ROLLOUT → DISABLED
- `set_gradual_rollout(percentage: RolloutPercentage)` — → GRADUAL_ROLLOUT
- `schedule(scheduled_at, target_status)` — → SCHEDULED
- `add_condition(condition_type, values, attribute_key=None, attribute_value=None)`
- `remove_condition(condition_id)`
- `update_description(description)`
- `delete()` — только если `is_permanent=False` и `status=DISABLED`

Инварианты:
- `key` уникален глобально
- `GRADUAL_ROLLOUT` требует `rollout_percentage`
- `SCHEDULED` требует `scheduled_at`
- `PERMANENT` флаги нельзя удалять
- Условия таргетинга: AND логика между conditions
- `FeatureFlagCondition.values` не пустой
- `CUSTOM_ATTRIBUTE` требует `attribute_key` и `attribute_value`

## Repositories

| Репозиторий | Методы |
|---|---|
| `SystemSettingsRepository` | `get_global`, `get_by_organization`, `get_by_workspace`, `get_effective_for_workspace` |
| `TemplateRepository` | `get_by_id`, `get_by_type`, `get_system_templates`, `get_by_workspace`, `get_by_name`, `search` |
| `FeatureFlagRepository` | `get_by_id`, `get_by_key`, `get_all`, `get_by_status`, `get_scheduled`, `evaluate(key, context: dict) → bool` |
| `WebhookRepository` | `get_by_id`, `get_by_url`, `get_active_webhooks`, `get_by_event_type`, `get_failed_webhooks` |

> **`SystemSettingsRepository.get_effective_for_workspace`** — объединяет GLOBAL + ORGANIZATION + WORKSPACE настройки с учётом наследования.
>
> **`FeatureFlagRepository.evaluate`** — вычисляет, включён ли флаг для данного контекста (user_id, team_id, workspace_id, plan_type, custom attributes). Используется на app-слое для проверки фича-флагов.
>
> **`FeatureFlagRepository.get_scheduled`** — флаги, которые нужно включить/выключить по расписанию.
>
> **`WebhookRepository.get_by_event_type`** — вебхуки, подписанные на конкретное событие (для доставки).
>
> **`WebhookRepository.get_failed_webhooks`** — вебхуки со статусом FAILED (для мониторинга).
