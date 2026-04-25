# События Identity BC

## События, которые отдаёт Identity BC

### User Events

| Событие | Описание | Поля |
|---|---|---|
| `UserRegistered` | Пользователь зарегистрирован | `user_id`, `email`, `auth_provider` |
| `EmailConfirmed` | Email подтверждён | `user_id` |
| `RoleAssigned` | Роль назначена пользователю | `user_id`, `role_id` |
| `RoleRemoved` | Роль снята с пользователя | `user_id`, `role_id` |
| `PasswordChanged` | Пароль изменён | `user_id` |
| `AccountDeletionRequested` | Запрос удаления аккаунта | `user_id` |
| `AccountDisabled` | Аккаунт деактивирован | `user_id` |
| `AccountReactivated` | Аккаунт реактивирован | `user_id` |

### Auth Events

| Событие | Описание | Поля |
|---|---|---|
| `UserLoggedIn` | Успешный вход пользователя | `user_id`, `session_id`, `ip`, `device` |
| `LoginFailed` | Неудачная попытка входа | `user_id`, `ip` |
| `UserLockedOut` | Блокировка после неудачных попыток | `user_id`, `lockout_until` |
| `AuthFactorEnabled` | Фактор 2FA включён | `user_id`, `method`, `is_primary` |
| `AuthFactorDisabled` | Фактор 2FA отключён | `user_id`, `method` |
| `NewDeviceLogin` | Вход с нового устройства/IP | `user_id`, `ip`, `device` |
| `PasswordResetRequested` | Запрос сброса пароля | `user_id`, `email` |
| `PasswordResetCompleted` | Пароль сброшен | `user_id` |
| `OAuthLinked` | OAuth-аккаунт привязан | `user_id`, `provider` |
| `OAuthUnlinked` | OAuth-аккаунт отвязан | `user_id`, `provider` |
| `SSOLinked` | SSO привязан | `user_id` |
| `TrustedDeviceAdded` | Доверенное устройство добавлено | `user_id`, `device_fingerprint` |
| `TrustedDeviceRemoved` | Доверенное устройство удалено | `user_id`, `device_fingerprint` |

### Session Events

| Событие | Описание | Поля |
|---|---|---|
| `SessionCreated` | Сессия создана | `user_id`, `ip_address`, `device_info` |
| `SessionTerminated` | Сессия завершена | `user_id`, `session_id` |
| `AllOtherSessionsTerminated` | Все другие сессии завершены, кроме текущей | `user_id`, `current_session_id` |
| `SessionRefreshed` | Сессия обновлена (refresh token) | `user_id` |

**Итого: 23 события**

---

## События, на которые подписывается Identity BC

### Внутренние подписки (внутри Identity BC)

| Обработчик | Событие | Описание |
|---|---|---|
| `OnUserLoggedInCreateSession` | `UserLoggedIn` | Создаёт новую сессию при успешном входе. Межагрегатное взаимодействие: UserAuth → (event) → Session. |

### Кросс-BC подписки

Нет. Identity BC не подписывается на события других BC.

**Итого: 1 подписка (внутренняя)**
