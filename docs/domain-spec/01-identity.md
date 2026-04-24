# Identity BC — Спецификация

> Путь: `app/context/identity/domain`
> Исходные требования: §1 (Аутентификация и авторизация), §2 (Системные роли)

## Контекст

Identity BC отвечает за регистрацию, аутентификацию, авторизацию, управление сессиями и системные роли. Уже частично реализован.

---

## Принципы расширяемости

1. **Enum-ы только для стабильных множеств** — `AuthProvider`, `TwoFAMethod`, `SessionStatus` редко меняются, enum допустим. При добавлении значения — правка enum + миграция, это задокументированная процедура.
2. **Роли — entity, не enum** — `Role` хранится как запись, позволяет кастомные роли без изменения домена.
3. **Один фактор = одна запись** — `AuthFactor` как коллекция внутри `UserAuth`, добавление нового метода 2FA = новая запись, не изменение структуры.
4. **Токены обобщены** — `VerificationToken` с `token_type` вместо N копий VO.
5. **Aggregate boundaries** — `User` не управляет сессиями другого AR (`Session`). Взаимодействие через events на app-слое.

---

## Value Objects

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `AuthProvider` | Enum | `EMAIL_PASSWORD`, `OAUTH_GOOGLE`, `OAUTH_GITHUB`, `OAUTH_YANDEX`, `OAUTH_APPLE`, `SAML_SSO` | §1.1, §1.2 |
| `TwoFAMethod` | Enum | `TOTP`, `EMAIL_CODE`, `APP` | §1.2 |
| `LoginStatus` | Enum | `SUCCESS`, `FAILED`, `BLOCKED` | §1.2 |
| `SessionStatus` | Enum | `ACTIVE`, `EXPIRED`, `TERMINATED` | §1.4 |
| `VerificationType` | Enum | `EMAIL_CONFIRMATION`, `PASSWORD_RESET`, `ACCOUNT_DELETION`, `EMAIL_CHANGE` | §1.1, §1.3 |
| `AccountStatus` | Enum | `PENDING_VERIFICATION`, `ACTIVE`, `LOCKED`, `DISABLED`, `PENDING_DELETION` | §1.1, §1.2 |
| `PasswordHash` | frozen dataclass | Хэш пароля (не хранить plain!) | §1.1 |
| `VerificationToken` | frozen dataclass | token_type: VerificationType, value: str, expires_at: datetime | §1.1, §1.3 |
| `TwoFASecret` | frozen dataclass | value: str (encrypted), method: TwoFAMethod | §1.2 |
| `FailedLoginPolicy` | frozen dataclass | thresholds: list[LockoutThreshold], configurable per-context | §1.2 |
| `LockoutThreshold` | frozen dataclass | failed_attempts: int, lock_duration_minutes: int | §1.2 |
| `PasswordPolicy` | frozen dataclass | min_length, require_upper, require_lower, require_digit, require_special, max_age_days \| None | §1.1 |
| `IpAddress` | frozen dataclass | value: str (validated) | §1.2 |
| `DeviceInfo` | frozen dataclass | user_agent: str, os: str \| None, browser: str \| None, device_type: str \| None | §1.4 |

> **Примечание по расширению enum-ов**: Добавление нового значения в `AuthProvider` или `TwoFAMethod` требует: (1) правки enum, (2) добавления метода в `UserAuth`/`AuthFactor` при необходимости, (3) миграции БД. Это задокументированная процедура с низким риском, т.к. множества стабильны.

## Entities

| Сущность | Поля | Описание | Исходное требование |
|---|---|---|---|
| `OAuthLink` | provider: AuthProvider, provider_user_id: str, email: str \| None, display_name: str \| None, linked_at: datetime | Привязка внешнего провайдера к аккаунту | §1.1, §1.2 |
| `AuthFactor` | method: TwoFAMethod, secret: TwoFASecret \| None, is_enabled: bool, is_primary: bool, verified_at: datetime \| None, priority: int | Один фактор аутентификации (2FA). Коллекция внутри UserAuth | §1.2 |
| `LoginAttempt` | ip: IpAddress, user_agent: str, attempted_at: datetime, was_successful: bool, login_status: LoginStatus | Запись попытки входа | §1.2 |
| `TrustedDevice` | device_fingerprint: str, device_info: DeviceInfo, ip: IpAddress, trusted_at: datetime, expires_at: datetime \| None | Доверенное устройство пользователя | §1.2 |
| `Role` | name: str, permissions: list[str], is_system: bool, description: str \| None | Роль пользователя (системная или кастомная) | §2 |

> **`AuthFactor` вместо `TwoFAConfig`**: Каждый фактор — отдельная запись в коллекции. Это позволяет: несколько методов 2FA одновременно, резервные методы (fallback), приоритеты, добавление новых методов без изменения структуры. `is_primary` указывает основной фактор, остальные — fallback.

> **`Role` вместо `SystemRole` enum**: Системные роли (super_admin, admin, supporter, user) — предустановленные записи с `is_system=True`. Кастомные роли создаются через administration BC с `is_system=False`. Это открывает RBAC без изменения домена.

## Domain Events

| Событие | Поля | Описание | Исходное требование |
|---|---|---|---|
| `UserRegistered` | user_id, email, auth_provider | Пользователь зарегистрирован | §1.1 |
| `EmailConfirmed` | user_id | Email подтверждён | §1.1 |
| `UserLoggedIn` | user_id, session_id, ip, device | Успешный вход | §1.2 |
| `LoginFailed` | user_id, ip | Неудачная попытка входа | §1.2 |
| `UserLockedOut` | user_id, lockout_until | Блокировка после неудачных попыток | §1.2 |
| `AuthFactorEnabled` | user_id, method, is_primary | Фактор 2FA включён | §1.2 |
| `AuthFactorDisabled` | user_id, method | Фактор 2FA отключён | §1.2 |
| `NewDeviceLogin` | user_id, ip, device | Вход с нового устройства/IP | §1.2 |
| `PasswordResetRequested` | user_id, email | Запрос сброса пароля | §1.3 |
| `PasswordResetCompleted` | user_id | Пароль сброшен | §1.3 |
| `SessionTerminated` | user_id, session_id | Сессия завершена | §1.4 |
| `AllOtherSessionsTerminated` | user_id | Все сессии кроме текущей завершены | §1.4 |
| `OAuthLinked` | user_id, provider | OAuth-аккаунт привязан | §1.1 |
| `OAuthUnlinked` | user_id, provider | OAuth-аккаунт отвязан | §1.1 |
| `SSOLinked` | user_id | SSO привязан | §1.2 |
| `RoleAssigned` | user_id, role | Роль назначена | §2 |
| `RoleRemoved` | user_id, role | Роль снята | §2 |
| `PasswordChanged` | user_id | Пароль изменён | §1.1 |
| `AccountDeletionRequested` | user_id | Запрос удаления аккаунта | §1.1 |
| `AccountDisabled` | user_id | Аккаунт деактивирован | §1.1 |
| `AccountReactivated` | user_id | Аккаунт реактивирован | §1.1 |
| `TrustedDeviceAdded` | user_id, device_fingerprint | Доверенное устройство добавлено | §1.2 |
| `TrustedDeviceRemoved` | user_id, device_fingerprint | Доверенное устройство удалено | §1.2 |

## Exceptions

| Исключение | Описание |
|---|---|
| `UserNotFoundException` | Пользователь не найден |
| `InvalidCredentialsException` | Неверные учётные данные |
| `UserBlockedException` | Пользователь заблокирован |
| `EmailNotConfirmedException` | Email не подтверждён |
| `TwoFARequiredException` | Требуется 2FA |
| `InvalidTwoFACodeException` | Неверный код 2FA |
| `InvalidVerificationTokenException` | Неверный или просроченный токен верификации |
| `OAuthProviderAlreadyLinkedException` | OAuth уже привязан |
| `CannotUnlinkLastProviderException` | Нельзя отвязать последний метод входа |
| `SessionNotFoundException` | Сессия не найдена |
| `AccountDeletionPendingException` | Аккаунт в процессе удаления |
| `RoleNotFoundException` | Роль не найдена |
| `DuplicateRoleException` | Роль уже назначена |
| `LastSystemRoleException` | Нельзя снять последнюю системную роль |

## Aggregates

### User (Aggregate Root)

Отвечает за идентичность, статус и роли. Не управляет аутентификацией напрямую — делегирует `UserAuth`.

Методы:
- `register(email, password, auth_provider)` → `User` (factory)
- `confirm_email()`
- `assign_role(role)`
- `remove_role(role)`
- `disable()`
- `reactivate()`
- `request_account_deletion()`
- `cancel_account_deletion()`

Инварианты:
- У пользователя всегда есть хотя бы одна системная роль
- Email должен быть подтверждён для определённых действий
- Аккаунт в статусе `PENDING_DELETION` не может выполнять действия кроме `cancel_account_deletion`

### UserAuth (Aggregate Root)

Отвечает за аутентификацию: пароль, OAuth, 2FA, блокировки, верификации. Связан с `User` через `user_id` (opaque ID).

Методы:
- `create_for_email_auth(user_id, email, password_hash)` → `UserAuth` (factory)
- `create_for_oauth(user_id, email, provider, provider_user_id)` → `UserAuth` (factory)
- `create_for_sso(user_id, email, provider_user_id)` → `UserAuth` (factory)
- `verify_password(password)` → bool
- `change_password(new_password_hash)`
- `request_password_reset(token, expires_at)` → VerificationToken
- `reset_password(token_value, new_password_hash)`
- `request_email_verification(token, expires_at)` → VerificationToken
- `verify_email(token_value)`
- `record_failed_login(policy: FailedLoginPolicy)`
- `record_successful_login()`
- `unlock()`
- `is_locked()` → bool
- `enable_auth_factor(method, secret, is_primary=False)`
- `disable_auth_factor(method)`
- `verify_auth_factor(method, code)` → bool
- `set_primary_factor(method)`
- `link_oauth(provider, provider_user_id, email=None, display_name=None)`
- `unlink_oauth(provider)`
- `add_trusted_device(fingerprint, device_info, ip, expires_at=None)`
- `remove_trusted_device(fingerprint)`
- `is_trusted_device(fingerprint)` → bool

Инварианты:
- Блокировка по `FailedLoginPolicy` (прогрессивная: thresholds настраиваются)
- 2FA-факторы проверяются после успешной проверки пароля/OAuth
- Хотя бы один `is_primary=True` фактор, если 2FA включена
- Нельзя отвязать последний OAuth если нет пароля
- Резервный код (backup) — отдельный `AuthFactor` с `method=APP`

### Session (Aggregate Root)

Полностью самостоятельный AR. `User` и `UserAuth` не управляют сессиями напрямую — только через events.

Методы:
- `create(user_id, device, ip, geo, max_concurrent)` → `Session` (factory)
- `terminate()`
- `terminate_all_for_user(user_id, except_session_id)` → list[Session] (class method)
- `refresh_activity()`

Инварианты:
- Сессия имеет срок действия
- Завершённая сессия не может быть обновлена
- При превышении `max_concurrent` — самая старая сессия завершается автоматически

> **Взаимодействие через events**: `UserLoggedIn` (от UserAuth) → app-layer handler создаёт Session. `SessionTerminated` → app-layer handler уведомляет UserAuth. Никаких прямых вызовов между AR.

## Repositories

| Репозиторий | Методы |
|---|---|
| `UserRepository` | `get_by_id`, `get_by_email`, `search`, `get_by_role` |
| `UserAuthRepository` | `get_by_id`, `get_by_user_id`, `get_by_email`, `get_by_oauth_provider` |
| `SessionRepository` | `get_by_id`, `get_active_by_user`, `get_by_user`, `count_active_by_user` |
| `RoleRepository` | `get_by_id`, `get_by_name`, `get_system_roles`, `search` |

## Предустановленные системные роли

При инициализации системы создаются 4 записи `Role` с `is_system=True`:

| name | permissions | Описание |
|---|---|---|
| `super_admin` | `*` (все) | Полный доступ |
| `admin` | `users.*`, `content.*`, `settings.*` | Управление пользователями и контентом |
| `supporter` | `users.read`, `users.support`, `content.read` | Ограниченные права поддержки |
| `user` | `self.*` | Базовый доступ к собственным данным |

> Кастомные роли создаются через Administration BC и хранятся с `is_system=False`. Identity BC хранит и проверяет роли, но не создаёт кастомные — это ответственность Administration BC.
