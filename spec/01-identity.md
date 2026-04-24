# 01. Identity — Аутентификация и авторизация

## Обзор

Контекст Identity отвечает за регистрацию, аутентификацию, управление сессиями, 2FA и восстановление доступа. Это фундаментальный контекст, от которого зависят все остальные.

> Путь: `app/context/identity/domain`
> Исходные требования: §1 (Аутентификация и авторизация), §2 (Системные роли)

---

## Принципы расширяемости

1. **Enum-ы только для стабильных множеств** — `AuthProvider`, `TwoFAMethod`, `SessionStatus` редко меняются, enum допустим. При добавлении значения — правка enum + миграция, это задокументированная процедура.
2. **Роли — entity, не enum** — `Role` хранится как запись, позволяет кастомные роли без изменения домена.
3. **Один фактор = одна запись** — `AuthFactor` как коллекция внутри `UserAuth`, добавление нового метода 2FA = новая запись, не изменение структуры.
4. **Токены обобщены** — `VerificationToken` с `token_type` вместо N копий VO.
5. **Aggregate boundaries** — `User` не управляет сессиями другого AR (`Session`). Взаимодействие через events на app-слое.

---

## 1. Функциональные требования

### 1.1. Регистрация

| Требование | Free | Start | Business | Enterprise |
|-----------|------|-------|----------|------------|
| Email + пароль | ✅ | ✅ | ✅ | ✅ |
| OAuth 2.0 (Google, GitHub, Яндекс, Apple) | ✅ | ✅ | ✅ | ✅ |
| SSO (SAML 2.0) | ❌ | ❌ | ✅ | ✅ |
| Подтверждение email | ✅ | ✅ | ✅ | ✅ |
| LDAP / Active Directory | ❌ | ❌ | ❌ | ✅ |

**Правила:**
- Пароль: минимум 8 символов, 1 заглавная, 1 строчная, 1 цифра, 1 спецсимвол
- Email: уникальный в системе, подтверждение в течение 72 часов, иначе аккаунт удаляется
- OAuth: при первом входе создаётся аккаунт, при повторном — привязывается к существующему по email
- SSO: доступен только для пользователей, чей email-домен привязан к SSO-провайдеру организации

### 1.2. Вход в систему

| Требование | Free | Start | Business | Enterprise |
|-----------|------|-------|----------|------------|
| Email + пароль | ✅ | ✅ | ✅ | ✅ |
| OAuth 2.0 | ✅ | ✅ | ✅ | ✅ |
| SSO (SAML 2.0) | ❌ | ❌ | ✅ | ✅ |
| QR-code вход | ❌ | ✅ | ✅ | ✅ |
| 2FA: TOTP | ✅ | ✅ | ✅ | ✅ |
| 2FA: Email-код | ✅ | ✅ | ✅ | ✅ |
| 2FA: Authenticator app | ✅ | ✅ | ✅ | ✅ |
| Блокировка при неудачных попытках | ✅ | ✅ | ✅ | ✅ |
| Уведомление о входе с нового устройства | ✅ | ✅ | ✅ | ✅ |

**Правила блокировки:**
- 1-я неудача → предупреждение
- 4-я неудача → блокировка на 1 минуту
- 5-я → блокировка на 5 минут
- 6-я → блокировка на 10 минут
- 7+ → блокировка на 30 минут
- Счётчик сбрасывается после успешного входа

**QR-code вход:**
- Генерация QR-кода на веб-странице входа
- Сканирование из мобильного приложения (уже авторизованного)
- QR-код действителен 2 минуты
- Одноразовый

### 1.3. Восстановление доступа

- Запрос сброса пароля по email
- Ссылка для сброса действительна 1 час
- Одноразовая ссылка (после использования — недействительна)
- После сброса — завершение всех активных сессий (опционально)
- Rate limit: не более 3 запросов на сброс в час

### 1.4. Управление сессиями

| Требование | Free | Start | Business | Enterprise |
|-----------|------|-------|----------|------------|
| Макс. активных сессий | 3 | 10 | 25 | ∞ |
| Просмотр активных сессий | ✅ | ✅ | ✅ | ✅ |
| Завершение отдельной сессии | ✅ | ✅ | ✅ | ✅ |
| Завершение всех кроме текущей | ✅ | ✅ | ✅ | ✅ |

**Информация о сессии:**
- Device type (desktop/mobile/tablet)
- Browser / App name + version
- OS name + version
- IP-адрес
- Геолокация (город, страна)
- Время создания сессии
- Время последней активности

---

## 2. Доменная модель

### Aggregates

> **Aggregate boundaries**: `User` не управляет аутентификацией и сессиями напрямую. `UserAuth` — отдельный AR для аутентификации (пароль, OAuth, 2FA, блокировки). `Session` — полностью самостоятельный AR. Взаимодействие между AR — через events на app-слое.

#### User (Aggregate Root)

Отвечает за идентичность, статус и роли. Не управляет аутентификацией напрямую — делегирует `UserAuth`.

```
User
├── id: UserId (UUID)
├── email: Email (VO)
├── display_name: str
├── status: AccountStatus (enum)
├── email_verified: bool
├── email_verified_at: datetime | None
├── roles: List[Role] — системные и кастомные
├── created_at: datetime
├── updated_at: datetime
```

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

#### UserAuth (Aggregate Root)

Отвечает за аутентификацию: пароль, OAuth, 2FA, блокировки, верификации. Связан с `User` через `user_id` (opaque ID).

```
UserAuth
├── id: UUID
├── user_id: UserId
├── email: Email (VO) — для поиска при логине
├── password_hash: PasswordHash (VO) | None — null для OAuth-only
├── failed_login_attempts: int
├── locked_until: datetime | None
├── last_login_at: datetime | None
├── last_login_ip: IpAddress | None
├── created_at: datetime
├── updated_at: datetime
│
├── oauth_links: List[OAuthLink]
├── auth_factors: List[AuthFactor] — 2FA (коллекция)
├── verification_tokens: List[VerificationToken]
├── trusted_devices: List[TrustedDevice]
```

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

#### Session (Aggregate Root)

Полностью самостоятельный AR. `User` и `UserAuth` не управляют сессиями напрямую — только через events.

```
Session
├── id: SessionId (UUID)
├── user_id: UserId
├── token_hash: str — hashed (SHA-256)
├── status: SessionStatus (enum: ACTIVE, EXPIRED, TERMINATED)
├── device_info: DeviceInfo (VO)
├── ip_address: IpAddress (VO)
├── geo_city: str | None
├── geo_country: str | None
├── created_at: datetime
├── last_active_at: datetime
├── expires_at: datetime
```

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

### Entities

#### OAuthLink

```
OAuthLink
├── id: UUID
├── provider: AuthProvider (enum)
├── provider_user_id: str
├── email: str | None
├── display_name: str | None
├── access_token: str — encrypted
├── refresh_token: str | None — encrypted
├── token_expires_at: datetime | None
├── linked_at: datetime
├── created_at: datetime
├── updated_at: datetime
```

#### AuthFactor

> **`AuthFactor` вместо flat 2FA fields**: Каждый фактор — отдельная запись в коллекции. Это позволяет: несколько методов 2FA одновременно, резервные методы (fallback), приоритеты, добавление новых методов без изменения структуры. `is_primary` указывает основной фактор, остальные — fallback.

```
AuthFactor
├── id: UUID
├── user_auth_id: UUID
├── method: TwoFAMethod (enum: TOTP, EMAIL_CODE, APP)
├── secret: TwoFASecret (VO) | None — encrypted
├── is_enabled: bool
├── is_primary: bool
├── priority: int — для fallback ordering
├── verified_at: datetime | None
├── created_at: datetime
├── updated_at: datetime
```

#### VerificationToken

> **Обобщённый токен**: один тип вместо отдельных `RecoveryToken`, `EmailVerificationToken`. `token_type` определяет назначение.

```
VerificationToken
├── id: UUID
├── user_id: UserId
├── token_hash: str — hashed (SHA-256)
├── token_type: VerificationType (enum)
├── expires_at: datetime
├── used_at: datetime | None
├── created_at: datetime
```

#### TrustedDevice

```
TrustedDevice
├── id: UUID
├── user_auth_id: UUID
├── device_fingerprint: str
├── device_info: DeviceInfo (VO)
├── ip: IpAddress (VO)
├── trusted_at: datetime
├── expires_at: datetime | None
```

#### LoginAttempt

```
LoginAttempt
├── id: UUID
├── user_id: UserId | None — null если пользователь не найден
├── email: str
├── ip: IpAddress (VO)
├── user_agent: str
├── was_successful: bool
├── login_status: LoginStatus (enum: SUCCESS, FAILED, BLOCKED)
├── failure_reason: str | None
├── created_at: datetime
```

#### QrLoginRequest

```
QrLoginRequest
├── id: UUID
├── token: str — unique, short-lived
├── status: QrLoginStatus (enum: PENDING, SCANNED, CONFIRMED, EXPIRED)
├── created_by_ip: IpAddress
├── confirmed_by_user_id: UserId | None
├── confirmed_by_session_id: SessionId | None
├── expires_at: datetime
├── created_at: datetime
├── confirmed_at: datetime | None
```

#### Role

> **`Role` вместо `SystemRole` enum**: Системные роли (super_admin, admin, supporter, user) — предустановленные записи с `is_system=True`. Кастомные роли создаются через Administration BC с `is_system=False`. Это открывает RBAC без изменения домена.

```
Role
├── id: UUID
├── name: str — unique
├── permissions: List[str]
├── is_system: bool — системная (предустановленная) или кастомная
├── description: str | None
├── created_at: datetime
├── updated_at: datetime
```

### Value Objects

```python
class UserId:
    value: UUID

class SessionId:
    value: UUID

class Email:
    value: str  # lowercase, validated

class PasswordHash:
    value: str  # argon2id hash (не хранить plain!)

class IpAddress:
    value: str  # validated IPv4/IPv6

class DeviceInfo:
    user_agent: str
    os: str | None
    browser: str | None
    device_type: str | None  # desktop/mobile/tablet

class TwoFASecret:
    value: str  # encrypted
    method: TwoFAMethod

class PasswordPolicy:
    min_length: int = 8
    require_upper: bool = True
    require_lower: bool = True
    require_digit: bool = True
    require_special: bool = True
    max_age_days: int | None = None

class FailedLoginPolicy:
    thresholds: list[LockoutThreshold]

class LockoutThreshold:
    failed_attempts: int
    lock_duration_minutes: int
```

> **Примечание по расширению enum-ов**: Добавление нового значения в `AuthProvider` или `TwoFAMethod` требует: (1) правки enum, (2) добавления метода в `UserAuth`/`AuthFactor` при необходимости, (3) миграции БД. Это задокументированная процедура с низким риском, т.к. множества стабильны.

### Enums

```python
class AccountStatus(str, Enum):
    PENDING_VERIFICATION = "pending_verification"
    ACTIVE = "active"
    LOCKED = "locked"
    DISABLED = "disabled"
    PENDING_DELETION = "pending_deletion"

class AuthProvider(str, Enum):
    EMAIL_PASSWORD = "email_password"
    OAUTH_GOOGLE = "oauth_google"
    OAUTH_GITHUB = "oauth_github"
    OAUTH_YANDEX = "oauth_yandex"
    OAUTH_APPLE = "oauth_apple"
    SAML_SSO = "saml_sso"

class TwoFAMethod(str, Enum):
    TOTP = "totp"
    EMAIL_CODE = "email_code"
    APP = "app"

class LoginStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"

class SessionStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"

class VerificationType(str, Enum):
    EMAIL_CONFIRMATION = "email_confirmation"
    PASSWORD_RESET = "password_reset"
    ACCOUNT_DELETION = "account_deletion"
    EMAIL_CHANGE = "email_change"

class QrLoginStatus(str, Enum):
    PENDING = "pending"
    SCANNED = "scanned"
    CONFIRMED = "confirmed"
    EXPIRED = "expired"
```

---

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

## Repositories

| Репозиторий | Методы |
|---|---|
| `UserRepository` | `get_by_id`, `get_by_email`, `search`, `get_by_role` |
| `UserAuthRepository` | `get_by_id`, `get_by_user_id`, `get_by_email`, `get_by_oauth_provider` |
| `SessionRepository` | `get_by_id`, `get_active_by_user`, `get_by_user`, `count_active_by_user` |
| `RoleRepository` | `get_by_id`, `get_by_name`, `get_system_roles`, `search` |

---

## 3. Бизнес-правила и инварианты

1. **Email уникальность**: два пользователя не могут иметь одинаковый email
2. **Пароль**: валидируется по `PasswordPolicy` (min 8 символов, uppercase, lowercase, digit, special char; настраиваемо)
3. **Email verification**: аккаунт не может быть полностью активен без подтверждённого email
4. **OAuth linking**: OAuth-аккаунт привязывается к существующему пользователю по email (если email подтверждён)
5. **Session limit**: при превышении лимита — автоматически завершается самая старая сессия
6. **Login lockout**: блокировка по `FailedLoginPolicy` (прогрессивные thresholds, настраиваемые per-context)
7. **Verification token**: обобщённый, одноразовый, с `token_type`; PASSWORD_RESET действует 1 час, EMAIL_CONFIRMATION — 72 часа
8. **QR login**: токен действует 2 минуты, одноразовый
9. **2FA enforcement**: организация может требовать 2FA для всех участников (Business/Enterprise)
10. **2FA factors**: коллекция `AuthFactor`; хотя бы один `is_primary=True` если 2FA включена
11. **Password reset**: завершает все сессии (опционально, настраиваемо)
12. **Account lifecycle**: PENDING_VERIFICATION → ACTIVE → LOCKED/DISABLED/PENDING_DELETION
13. **Trusted devices**: вход с trusted device пропускает 2FA
14. **Cannot unlink last provider**: нельзя отвязать последний OAuth если нет пароля
15. **Soft delete**: при request_account_deletion → статус PENDING_DELETION, данные удаляются через 30 дней
16. **Rate limiting**: регистрация — 5/час/IP, вход — 10/мин/IP, сброс пароля — 3/час/email
17. **Roles**: у пользователя всегда есть хотя бы одна системная роль; кастомные роли через Administration BC

---

## 4. API Endpoints

### 4.1. Регистрация

```
POST /api/v1/auth/register
```

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecureP@ss1",
  "display_name": "John Doe"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "display_name": "John Doe",
  "status": "pending_verification",
  "email_verified": false,
  "created_at": "2025-01-01T00:00:00Z"
}
```

**Errors:**
- `409 Conflict` — email уже зарегистрирован
- `422 Unprocessable Entity` — невалидные данные (пароль слабый, email невалидный)
- `429 Too Many Requests` — rate limit

---

```
POST /api/v1/auth/register/oauth
```

**Request:**
```json
{
  "provider": "google",
  "code": "authorization_code",
  "redirect_uri": "https://app.taskflow.com/auth/callback"
}
```

**Response (201 / 200):**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@gmail.com",
    "display_name": "John Doe",
    "status": "active",
    "email_verified": true
  },
  "access_token": "jwt_token",
  "refresh_token": "refresh_token",
  "expires_in": 3600
}
```

---

```
POST /api/v1/auth/verify-email
```

**Request:**
```json
{
  "token": "verification_token"
}
```

**Response (200):**
```json
{
  "message": "Email verified successfully"
}
```

---

```
POST /api/v1/auth/resend-verification
```

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response (200):**
```json
{
  "message": "Verification email sent"
}
```

### 4.2. Вход

```
POST /api/v1/auth/login
```

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecureP@ss1",
  "device_info": {
    "device_type": "desktop",
    "browser": "Chrome 120",
    "os": "Windows 11"
  }
}
```

**Response (200):**
```json
{
  "access_token": "jwt_token",
  "refresh_token": "refresh_token",
  "expires_in": 3600,
  "requires_2fa": false,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "display_name": "John Doe"
  }
}
```

**Response (200, requires 2FA):**
```json
{
  "requires_2fa": true,
  "two_factor_method": "totp",
  "temp_token": "temporary_token_for_2fa"
}
```

**Errors:**
- `401 Unauthorized` — неверные credentials
- `403 Forbidden` — аккаунт заблокирован / не подтверждён
- `423 Locked` — временная блокировка (lockout)
- `429 Too Many Requests` — rate limit

---

```
POST /api/v1/auth/login/2fa
```

**Request:**
```json
{
  "temp_token": "temporary_token_for_2fa",
  "code": "123456",
  "device_info": {
    "device_type": "desktop",
    "browser": "Chrome 120",
    "os": "Windows 11"
  }
}
```

**Response (200):** аналогично успешному входу

---

```
POST /api/v1/auth/login/oauth
```

**Request:**
```json
{
  "provider": "google",
  "code": "authorization_code",
  "redirect_uri": "https://app.taskflow.com/auth/callback",
  "device_info": { ... }
}
```

---

```
POST /api/v1/auth/login/qr/generate
```

**Response (200):**
```json
{
  "qr_token": "unique_qr_token",
  "qr_image_url": "data:image/png;base64,...",
  "expires_at": "2025-01-01T00:02:00Z"
}
```

---

```
POST /api/v1/auth/login/qr/confirm
```
*Вызывается из мобильного приложения (авторизованного)*

**Request:**
```json
{
  "qr_token": "unique_qr_token"
}
```

---

```
GET /api/v1/auth/login/qr/status/{qr_token}
```
*Polling или WebSocket для проверки статуса QR-логина*

**Response (200):**
```json
{
  "status": "confirmed",
  "access_token": "jwt_token",
  "refresh_token": "refresh_token"
}
```

---

```
POST /api/v1/auth/login/sso
```

**Request:**
```json
{
  "email": "user@company.com"
}
```

**Response (200):**
```json
{
  "redirect_url": "https://idp.company.com/saml/login?SAMLRequest=..."
}
```

---

```
POST /api/v1/auth/login/sso/callback
```
*Callback от SAML IdP*

### 4.3. Токены

```
POST /api/v1/auth/token/refresh
```

**Request:**
```json
{
  "refresh_token": "refresh_token"
}
```

**Response (200):**
```json
{
  "access_token": "new_jwt_token",
  "refresh_token": "new_refresh_token",
  "expires_in": 3600
}
```

---

```
POST /api/v1/auth/logout
```

**Headers:** `Authorization: Bearer <access_token>`

**Response (204):** No Content

### 4.4. Восстановление доступа

```
POST /api/v1/auth/password/forgot
```

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response (200):**
```json
{
  "message": "If the email exists, a reset link has been sent"
}
```

---

```
POST /api/v1/auth/password/reset
```

**Request:**
```json
{
  "token": "reset_token",
  "new_password": "NewSecureP@ss1",
  "terminate_sessions": true
}
```

### 4.5. 2FA

```
POST /api/v1/auth/2fa/enable
```

**Request:**
```json
{
  "method": "totp"
}
```

**Response (200):**
```json
{
  "secret": "BASE32SECRET",
  "qr_code_url": "otpauth://totp/TaskFlow:user@example.com?secret=...",
  "backup_codes": ["code1", "code2", "..."]
}
```

---

```
POST /api/v1/auth/2fa/confirm
```

**Request:**
```json
{
  "code": "123456"
}
```

---

```
POST /api/v1/auth/2fa/disable
```

**Request:**
```json
{
  "password": "current_password"
}
```

---

```
GET /api/v1/auth/2fa/backup-codes
```

**Response (200):**
```json
{
  "backup_codes": ["code1", "code2", "..."],
  "generated_at": "2025-01-01T00:00:00Z"
}
```

---

```
POST /api/v1/auth/2fa/backup-codes/regenerate
```

### 4.6. Сессии

```
GET /api/v1/auth/sessions
```

**Response (200):**
```json
{
  "sessions": [
    {
      "id": "session_uuid",
      "device_type": "desktop",
      "browser": "Chrome 120",
      "os": "Windows 11",
      "ip_address": "192.168.1.1",
      "geo_city": "Moscow",
      "geo_country": "Russia",
      "created_at": "2025-01-01T00:00:00Z",
      "last_active_at": "2025-01-01T12:00:00Z",
      "is_current": true
    }
  ],
  "total": 2,
  "max_sessions": 3
}
```

---

```
DELETE /api/v1/auth/sessions/{session_id}
```

**Response (204):** No Content

---

```
DELETE /api/v1/auth/sessions
```
*Завершение всех сессий кроме текущей*

**Response (200):**
```json
{
  "terminated_count": 2
}
```

---

## 5. Схема БД

### Таблица: `users`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Lowercase |
| display_name | VARCHAR(100) | NOT NULL | |
| status | VARCHAR(30) | NOT NULL, DEFAULT 'pending_verification' | AccountStatus |
| email_verified | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| email_verified_at | TIMESTAMPTZ | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_users_email` — UNIQUE на `email`
- `idx_users_status` — на `status`
- `idx_users_created_at` — на `created_at`

### Таблица: `user_auths`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| user_id | UUID | FK → users.id, UNIQUE, NOT NULL | 1:1 с User |
| email | VARCHAR(255) | NOT NULL | Для поиска при логине |
| password_hash | VARCHAR(255) | NULLABLE | Null для OAuth-only |
| failed_login_attempts | INTEGER | NOT NULL, DEFAULT 0 | |
| locked_until | TIMESTAMPTZ | NULLABLE | |
| last_login_at | TIMESTAMPTZ | NULLABLE | |
| last_login_ip | VARCHAR(45) | NULLABLE | IPv4/IPv6 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_uauth_user_id` — UNIQUE на `user_id`
- `idx_uauth_email` — на `email`

### Таблица: `oauth_links`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| user_auth_id | UUID | FK → user_auths.id, NOT NULL | |
| provider | VARCHAR(20) | NOT NULL | AuthProvider enum |
| provider_user_id | VARCHAR(255) | NOT NULL | |
| email | VARCHAR(255) | NULLABLE | |
| display_name | VARCHAR(100) | NULLABLE | |
| access_token | TEXT | NOT NULL | Encrypted |
| refresh_token | TEXT | NULLABLE | Encrypted |
| token_expires_at | TIMESTAMPTZ | NULLABLE | |
| linked_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_oauth_uauth_provider` — UNIQUE на `(user_auth_id, provider)`
- `idx_oauth_provider_uid` — UNIQUE на `(provider, provider_user_id)`

### Таблица: `auth_factors`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| user_auth_id | UUID | FK → user_auths.id, NOT NULL | |
| method | VARCHAR(15) | NOT NULL | TwoFAMethod enum |
| secret | TEXT | NULLABLE | Encrypted |
| backup_codes | TEXT | NULLABLE | JSON array, encrypted |
| is_enabled | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| is_primary | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| priority | INTEGER | NOT NULL, DEFAULT 0 | Fallback ordering |
| verified_at | TIMESTAMPTZ | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_af_uauth` — на `user_auth_id`
- `idx_af_uauth_method` — UNIQUE на `(user_auth_id, method)`
- `idx_af_primary` — на `(user_auth_id)` WHERE `is_primary = TRUE`

### Таблица: `trusted_devices`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| user_auth_id | UUID | FK → user_auths.id, NOT NULL | |
| device_fingerprint | VARCHAR(255) | NOT NULL | |
| device_info | JSONB | NOT NULL | DeviceInfo VO |
| ip_address | VARCHAR(45) | NOT NULL | |
| trusted_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| expires_at | TIMESTAMPTZ | NULLABLE | |

**Индексы:**
- `idx_td_uauth` — на `user_auth_id`
- `idx_td_fingerprint` — UNIQUE на `(user_auth_id, device_fingerprint)`

### Таблица: `sessions`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| user_id | UUID | FK → users.id, NOT NULL | |
| token_hash | VARCHAR(64) | UNIQUE, NOT NULL | SHA-256 |
| status | VARCHAR(15) | NOT NULL, DEFAULT 'active' | SessionStatus |
| device_type | VARCHAR(10) | NOT NULL | desktop/mobile/tablet |
| browser | VARCHAR(100) | NULLABLE | |
| os | VARCHAR(100) | NULLABLE | |
| ip_address | VARCHAR(45) | NOT NULL | |
| geo_city | VARCHAR(100) | NULLABLE | |
| geo_country | VARCHAR(100) | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| last_active_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| expires_at | TIMESTAMPTZ | NOT NULL | |

**Индексы:**
- `idx_sessions_user_id` — на `user_id`
- `idx_sessions_token_hash` — UNIQUE на `token_hash`
- `idx_sessions_expires` — на `expires_at` (для cleanup job)
- `idx_sessions_active` — на `(user_id, status)` WHERE `status = 'active'`

### Таблица: `verification_tokens`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| user_id | UUID | FK → users.id, NOT NULL | |
| token_hash | VARCHAR(64) | UNIQUE, NOT NULL | SHA-256 |
| token_type | VARCHAR(25) | NOT NULL | VerificationType enum |
| expires_at | TIMESTAMPTZ | NOT NULL | |
| used_at | TIMESTAMPTZ | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_vt_token_hash` — UNIQUE на `token_hash`
- `idx_vt_user_type` — на `(user_id, token_type)`

### Таблица: `login_attempts`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| user_id | UUID | NULLABLE, FK → users.id | |
| email | VARCHAR(255) | NOT NULL | |
| ip_address | VARCHAR(45) | NOT NULL | |
| user_agent | TEXT | NOT NULL | |
| was_successful | BOOLEAN | NOT NULL | |
| login_status | VARCHAR(10) | NOT NULL | LoginStatus enum |
| failure_reason | VARCHAR(50) | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_login_attempts_user` — на `user_id`
- `idx_login_attempts_ip` — на `ip_address`
- `idx_login_attempts_created` — на `created_at`
- `idx_login_attempts_email_time` — на `(email, created_at)` (для rate limiting)

### Таблица: `qr_login_requests`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| token | VARCHAR(64) | UNIQUE, NOT NULL | |
| status | VARCHAR(15) | NOT NULL, DEFAULT 'pending' | |
| created_by_ip | VARCHAR(45) | NOT NULL | |
| confirmed_by_user_id | UUID | NULLABLE, FK → users.id | |
| confirmed_by_session_id | UUID | NULLABLE | |
| expires_at | TIMESTAMPTZ | NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| confirmed_at | TIMESTAMPTZ | NULLABLE | |

**Индексы:**
- `idx_qr_token` — UNIQUE на `token`
- `idx_qr_expires` — на `expires_at`

### Таблица: `roles`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| name | VARCHAR(50) | UNIQUE, NOT NULL | |
| permissions | JSONB | NOT NULL, DEFAULT '[]' | |
| is_system | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| description | TEXT | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_roles_name` — UNIQUE на `name`
- `idx_roles_system` — на `is_system`

### Таблица: `user_roles`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| user_id | UUID | FK → users.id, NOT NULL | |
| role_id | UUID | FK → roles.id, NOT NULL | |
| assigned_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| assigned_by | UUID | FK → users.id, NULLABLE | |

**Индексы:**
- `idx_ur_pk` — PRIMARY KEY на `(user_id, role_id)`
- `idx_ur_role` — на `role_id`

---

## 6. Доменные события

```python
# Регистрация
UserRegistered(user_id, email, auth_provider)
EmailVerificationSent(user_id, email)
EmailConfirmed(user_id)
UnverifiedAccountExpired(user_id, email)

# Вход
UserLoggedIn(user_id, session_id, ip, device, method: "password" | "oauth" | "sso" | "qr")
LoginFailed(user_id, ip, reason, attempt_number)
UserLockedOut(user_id, lockout_until, attempt_count)
AccountUnlocked(user_id)
NewDeviceLogin(user_id, session_id, ip, device)

# 2FA (AuthFactor)
AuthFactorEnabled(user_id, method, is_primary)
AuthFactorDisabled(user_id, method)
TwoFactorChallengeIssued(user_id, method)
TwoFactorVerified(user_id, method)
TwoFactorFailed(user_id, method)
BackupCodesRegenerated(user_id)

# Сессии
SessionCreated(user_id, session_id, ip, device)
SessionTerminated(user_id, session_id, terminated_by: "user" | "system" | "limit_exceeded")
AllOtherSessionsTerminated(user_id, count, except_session_id)

# Восстановление
PasswordResetRequested(user_id, email)
PasswordResetCompleted(user_id, sessions_terminated: bool)
PasswordChanged(user_id)

# OAuth
OAuthLinked(user_id, provider)
OAuthUnlinked(user_id, provider)
SSOLinked(user_id)

# Аккаунт
AccountDisabled(user_id, reason, disabled_by)
AccountReactivated(user_id, reactivated_by)
AccountDeletionRequested(user_id)
UserDeleted(user_id, method: "self" | "admin" | "gdpr")

# Роли
RoleAssigned(user_id, role)
RoleRemoved(user_id, role)

# Trusted Devices
TrustedDeviceAdded(user_id, device_fingerprint)
TrustedDeviceRemoved(user_id, device_fingerprint)

# QR
QrLoginRequested(qr_token, ip)
QrLoginScanned(qr_token, user_id)
QrLoginConfirmed(qr_token, user_id, session_id)
QrLoginExpired(qr_token)
```

---

## 7. Безопасность

### Хранение паролей
- Алгоритм: **Argon2id** (рекомендовано OWASP)
- Параметры: memory=64MB, iterations=3, parallelism=4
- Политика: настраивается через `PasswordPolicy` VO (per organization/workspace для Business/Enterprise)

### JWT-токены
- **Access token**: RS256, TTL = 15 минут
- **Refresh token**: opaque string, TTL = 30 дней, stored in DB (hashed)
- **Rotation**: при обновлении access token — выдаётся новый refresh token, старый инвалидируется

### Rate Limiting
| Endpoint | Лимит |
|----------|-------|
| POST /auth/register | 5 / час / IP |
| POST /auth/login | 10 / минута / IP |
| POST /auth/password/forgot | 3 / час / email |
| POST /auth/verify-email | 5 / час / email |
| POST /auth/2fa/* | 5 / минута / user |

### Защита от атак
- **CSRF**: SameSite cookies + CSRF token для cookie-based auth
- **XSS**: HttpOnly + Secure cookies
- **Brute force**: progressive lockout + rate limiting
- **Token theft**: refresh token rotation + device binding
- **Replay**: nonce в QR-login, одноразовые recovery tokens
