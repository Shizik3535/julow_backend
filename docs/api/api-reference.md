# API Reference — Julow Backend

Базовый префикс: `/api/v1`

Все endpoint'ы ниже указаны относительно этого префикса.
Полный URL: `http://<host>:8000/api/v1<endpoint>`

---

## Identity BC — Аутентификация

Контроллер: `AuthController` | Префикс: `/auth`

| Метод | URI | Описание |
|-------|-----|----------|
| POST | `/auth/register` | Регистрация нового пользователя. Назначает роль `user`, статус — `pending_verification` |
| POST | `/auth/login` | Вход в систему по email + пароль. Возвращает JWT access/refresh токены |
| POST | `/auth/refresh` | Обновление пары токенов по текущему refresh-токену |
| POST | `/auth/confirm-email` | Подтверждение email по токену верификации. Статус → `active` |
| POST | `/auth/password-reset/request` | Запрос сброса пароля. Отправляет токен на email |
| POST | `/auth/password-reset/confirm` | Смена пароля по токену сброса (одноразовый) |

---

## Identity BC — Аккаунт

Контроллер: `AccountController` | Префикс: `/account`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/account/me` | Данные аутентифицированного пользователя |
| POST | `/account/me/change-password` | Смена пароля (требует текущий пароль) |
| POST | `/account/me/request-deletion` | Запрос удаления аккаунта. Статус → `pending_deletion` |
| POST | `/account/me/cancel-deletion` | Отмена удаления аккаунта. Статус → `active` |
| POST | `/account/me/disable` | Деактивация аккаунта. Статус → `disabled` |
| POST | `/account/me/reactivate` | Реактивация аккаунта. Статус → `active` |
| GET | `/account/sessions` | Список активных сессий пользователя |
| DELETE | `/account/sessions/{session_id}` | Завершить указанную сессию |
| DELETE | `/account/sessions` | Завершить все сессии кроме текущей |
| GET | `/account/roles` | Список системных ролей (с фильтрацией и пагинацией) |
| GET | `/account/roles/{role_id}` | Получить роль по UUID |

---

## Identity BC — Безопасность

Контроллер: `SecurityController` | Префикс: `/account/security`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/account/security/status` | Обзор безопасности: пароль, блокировка, 2FA, OAuth, доверенные устройства, резервные коды |
| POST | `/account/security/2fa/enable` | Включить фактор 2FA (totp / email_code / app). Возвращает provisioning URI для TOTP |
| POST | `/account/security/2fa/disable` | Отключить фактор 2FA. Нельзя отключить последний активный |
| POST | `/account/security/2fa/verify` | Проверить одноразовый код 2FA |
| POST | `/account/security/2fa/set-primary` | Назначить метод 2FA основным |
| POST | `/account/security/2fa/backup-codes` | Сгенерировать новые резервные коды (старые заменяются) |
| POST | `/account/security/2fa/use-backup-code` | Использовать резервный код (одноразовый) |
| GET | `/account/security/oauth` | Список привязанных OAuth-провайдеров |
| POST | `/account/security/oauth/link` | Привязать OAuth-провайдер (google, github, yandex, apple) |
| DELETE | `/account/security/oauth/{provider}` | Отвязать OAuth-провайдер. Нельзя отвязать последний метод входа |
| GET | `/account/security/trusted-devices` | Список доверенных устройств (без просроченных) |
| POST | `/account/security/trusted-devices` | Добавить текущее устройство в доверенные |
| DELETE | `/account/security/trusted-devices/{fingerprint}` | Удалить доверенное устройство |

---

## Identity BC — Администрирование

Контроллер: `AdminController` | Префикс: `/admin/users`

| Метод | URI | Описание |
|-------|-----|----------|
| POST | `/admin/users/{user_id}/roles/{role_id}` | Назначить роль пользователю |
| DELETE | `/admin/users/{user_id}/roles/{role_id}` | Снять роль с пользователя (нельзя снять последнюю системную) |
| POST | `/admin/users/{user_id}/unlock` | Разблокировать аккаунт (сброс блокировки от неудачных входов) |

---

## Profile BC — Профиль

Контроллер: `ProfileController` | Префикс: `/profile`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/profile/me` | Получить свой профиль (аватар, bio, должность) |
| GET | `/profile/me/settings` | Получить все настройки профиля |
| GET | `/profile/search` | Пагинированный поиск профилей (admin) |
| PATCH | `/profile/me/personal-info` | Обновить bio и/или job_title |
| POST | `/profile/me/avatar` | Загрузить новый аватар |
| POST | `/profile/me/social-links` | Добавить ссылку на соцсеть |
| DELETE | `/profile/me/social-links/{platform}` | Удалить ссылку на соцсеть |
| PUT | `/profile/me/appearance` | Заменить настройки внешнего вида (тема, акцент, плотность) |
| PUT | `/profile/me/localization` | Заменить настройки локализации (язык, часовой пояс, формат даты/времени) |
| PUT | `/profile/me/navigation` | Заменить настройки навигации (стартовая страница) |
| PUT | `/profile/me/notifications` | Заменить настройки уведомлений (типы, каналы доставки) |
| PUT | `/profile/me/privacy` | Заменить настройки приватности (видимость профиля, онлайн-статус, трекинг) |
| PUT | `/profile/me/hotkeys` | Заменить конфигурацию горячих клавиш |
| PUT | `/profile/me/sidebar` | Заменить конфигурацию секций sidebar |
| POST | `/profile/me/pinned` | Закрепить элемент (workspace, project, task и т.д.) |
| DELETE | `/profile/me/pinned/{target_type}/{target_id}` | Открепить элемент |
| PUT | `/profile/me/pinned/reorder` | Переупорядочить закреплённые элементы |

---

## Organization BC — Организации

Контроллер: `OrganizationController` | Префикс: `/orgs`

| Метод | URI | Описание |
|-------|-----|----------|
| POST | `/orgs` | Создать организацию (текущий пользователь — владелец) |
| GET | `/orgs` | Пагинированный поиск организаций |
| GET | `/orgs/{org_id}` | Получить организацию по UUID |
| PATCH | `/orgs/{org_id}` | Обновить информацию (название, персонализация, брендинг) |
| PATCH | `/orgs/{org_id}/security-policy` | Обновить политику безопасности (2FA, длина пароля, таймаут сессии, IP-листы) |
| PATCH | `/orgs/{org_id}/membership-policy` | Обновить политику членства (приглашения, роли, лимиты) |
| POST | `/orgs/{org_id}/suspend` | Приостановить организацию с указанием причины |
| POST | `/orgs/{org_id}/reactivate` | Реактивировать приостановленную организацию |
| POST | `/orgs/{org_id}/request-deletion` | Запросить удаление организации. Статус → `pending_deletion` |
| POST | `/orgs/{org_id}/transfer-ownership` | Передать владение другому пользователю |

---

## Organization BC — Участники

Контроллер: `MemberController` | Префикс: `/orgs`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/orgs/{org_id}/members` | Список участников организации |
| GET | `/orgs/{org_id}/members/{user_id}` | Получить данные участника |
| POST | `/orgs/{org_id}/members` | Добавить участника с указанной ролью |
| PATCH | `/orgs/{org_id}/members/{user_id}/role` | Изменить роль участника |
| PATCH | `/orgs/{org_id}/members/{user_id}/display-name` | Изменить отображаемое имя участника |
| DELETE | `/orgs/{org_id}/members/{user_id}` | Удалить участника из организации |
| POST | `/orgs/{org_id}/members/{user_id}/deactivate` | Деактивировать участника без удаления |
| POST | `/orgs/{org_id}/members/{user_id}/reactivate` | Реактивировать деактивированного участника |
| POST | `/orgs/{org_id}/owners` | Добавить со-владельца |
| DELETE | `/orgs/{org_id}/owners/{user_id}` | Удалить со-владельца (минимум один владелец остаётся) |

---

## Organization BC — Приглашения

Контроллер: `InvitationController` | Префикс: `/orgs`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/orgs/{org_id}/invitations` | Список приглашений организации |
| POST | `/orgs/{org_id}/invitations/email` | Отправить приглашение на email |
| POST | `/orgs/{org_id}/invitations/bulk` | Массовая отправка приглашений (дубликаты пропускаются) |
| POST | `/orgs/{org_id}/invitations/link` | Сгенерировать ссылку-приглашение (с ограничениями по использованию/времени) |
| POST | `/orgs/{org_id}/invitations/{invitation_id}/revoke` | Отозвать приглашение |
| GET | `/orgs/invitations/token/{token}` | Получить приглашение по токену ссылки |
| POST | `/orgs/invitations/{invitation_id}/accept` | Принять приглашение (пользователь добавляется в организацию) |
| POST | `/orgs/invitations/{invitation_id}/decline` | Отклонить приглашение |

---

## Organization BC — Подразделения

Контроллер: `DepartmentController` | Префикс: `/orgs`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/orgs/{org_id}/departments` | Список подразделений организации |
| GET | `/orgs/{org_id}/departments/{department_id}` | Получить подразделение по UUID |
| POST | `/orgs/{org_id}/departments` | Создать подразделение |
| PATCH | `/orgs/{org_id}/departments/{department_id}` | Обновить подразделение (название, руководитель) |
| DELETE | `/orgs/{org_id}/departments/{department_id}` | Удалить подразделение (мягкое удаление) |
| POST | `/orgs/{org_id}/departments/{department_id}/members/{user_id}` | Добавить участника в подразделение |
| DELETE | `/orgs/{org_id}/departments/{department_id}/members/{user_id}` | Удалить участника из подразделения |

---

## Organization BC — Команды

Контроллер: `TeamController` | Префикс: `/orgs`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/orgs/{org_id}/teams` | Список команд организации |
| GET | `/orgs/{org_id}/teams/{team_id}` | Получить команду по UUID |
| POST | `/orgs/{org_id}/teams` | Создать команду |
| PATCH | `/orgs/{org_id}/teams/{team_id}` | Обновить команду (название, описание, лидер, иконка) |
| POST | `/orgs/{org_id}/teams/{team_id}/deactivate` | Деактивировать команду без удаления |
| POST | `/orgs/{org_id}/teams/{team_id}/reactivate` | Реактивировать деактивированную команду |
| POST | `/orgs/{org_id}/teams/{team_id}/members/{user_id}` | Добавить участника в команду |
| DELETE | `/orgs/{org_id}/teams/{team_id}/members/{user_id}` | Удалить участника из команды |

---

## Organization BC — Роли

Контроллер: `RoleController` | Префикс: `/orgs`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/orgs/{org_id}/roles` | Список ролей организации (фильтр `system_only`) |
| GET | `/orgs/{org_id}/roles/{role_id}` | Получить роль по UUID |
| POST | `/orgs/{org_id}/roles` | Создать кастомную роль с разрешениями |
| PATCH | `/orgs/{org_id}/roles/{role_id}` | Обновить разрешения/описание кастомной роли |
| DELETE | `/orgs/{org_id}/roles/{role_id}` | Удалить кастомную роль (системные удалить нельзя) |

---

## Organization BC — Интеграции

Контроллер: `IntegrationController` | Префикс: `/orgs`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/orgs/{org_id}/sso-integrations` | Список SSO-интеграций |
| POST | `/orgs/{org_id}/sso-integrations` | Добавить SSO-интеграцию (сертификат шифруется) |
| PATCH | `/orgs/{org_id}/sso-integrations/{integration_id}` | Обновить параметры SSO-интеграции |
| POST | `/orgs/{org_id}/sso-integrations/{integration_id}/deactivate` | Деактивировать SSO-интеграцию |
| GET | `/orgs/{org_id}/storage` | Получить конфигурацию хранилища |
| POST | `/orgs/{org_id}/storage` | Добавить хранилище (ключ доступа шифруется) |
| PATCH | `/orgs/{org_id}/storage/{storage_id}` | Обновить конфигурацию/квоту хранилища |

---

## Workspace BC — Workspace

Контроллер: `WorkspaceController` | Префикс: `/workspaces`

| Метод | URI | Описание |
|-------|-----|----------|
| POST | `/workspaces` | Создать workspace (текущий пользователь — владелец) |
| GET | `/workspaces` | Пагинированный поиск workspace с фильтрацией |
| GET | `/workspaces/{ws_id}` | Получить workspace по UUID |
| PATCH | `/workspaces/{ws_id}` | Обновить информацию (название, персонализация, брендинг) |
| PATCH | `/workspaces/{ws_id}/security-policy` | Обновить политику безопасности (PIN, пароль, IP-whitelist, SSO, 2FA) |
| PATCH | `/workspaces/{ws_id}/membership-policy` | Обновить политику членства (приглашения, роли, лимиты участников) |
| PATCH | `/workspaces/{ws_id}/limits` | Обновить лимиты (проекты, участники, хранилище, файлы, команды) |
| POST | `/workspaces/{ws_id}/archive` | Архивировать workspace (проекты → read-only) |
| POST | `/workspaces/{ws_id}/restore` | Восстановить архивированный workspace |
| POST | `/workspaces/{ws_id}/suspend` | Приостановить workspace с указанием причины |
| POST | `/workspaces/{ws_id}/reactivate` | Реактивировать приостановленный workspace |
| POST | `/workspaces/{ws_id}/request-deletion` | Запросить удаление workspace. Статус → `pending_deletion` |
| POST | `/workspaces/{ws_id}/transfer-ownership` | Передать владение другому пользователю |
| POST | `/workspaces/{ws_id}/move` | Переместить в иерархии (под нового родителя или отсоединить) |
| GET | `/workspaces/{ws_id}/settings` | Получить настройки (политики безопасности, членства, лимиты) |
| GET | `/workspaces/{ws_id}/children` | Список дочерних workspace |
| POST | `/workspaces/{ws_id}/owners` | Добавить со-владельца |
| DELETE | `/workspaces/{ws_id}/owners/{user_id}` | Удалить со-владельца (минимум один владелец остаётся) |

---

## Workspace BC — Участники

Контроллер: `WorkspaceMemberController` | Префикс: `/workspaces`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/workspaces/{ws_id}/members` | Список участников workspace |
| GET | `/workspaces/{ws_id}/members/{user_id}` | Получить данные участника |
| POST | `/workspaces/{ws_id}/members` | Добавить участника с указанной ролью |
| PATCH | `/workspaces/{ws_id}/members/{user_id}/role` | Изменить роль участника |
| PATCH | `/workspaces/{ws_id}/members/{user_id}/display-name` | Изменить отображаемое имя участника |
| DELETE | `/workspaces/{ws_id}/members/{user_id}` | Удалить участника из workspace |
| POST | `/workspaces/{ws_id}/members/{user_id}/deactivate` | Деактивировать участника без удаления |
| POST | `/workspaces/{ws_id}/members/{user_id}/reactivate` | Реактивировать деактивированного участника |

---

## Workspace BC — Приглашения

Контроллер: `WorkspaceInvitationController` | Префикс: `/workspaces`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/workspaces/{ws_id}/invitations` | Список приглашений workspace |
| POST | `/workspaces/{ws_id}/invitations/email` | Отправить приглашение на email |
| POST | `/workspaces/{ws_id}/invitations/bulk` | Массовая отправка приглашений (дубликаты пропускаются) |
| POST | `/workspaces/{ws_id}/invitations/link` | Сгенерировать ссылку-приглашение (с ограничениями по использованию/времени) |
| POST | `/workspaces/{ws_id}/invitations/{invitation_id}/revoke` | Отозвать приглашение |
| GET | `/workspaces/invitations/token/{token}` | Получить приглашение по токену ссылки |
| POST | `/workspaces/invitations/{invitation_id}/accept` | Принять приглашение (пользователь добавляется в workspace) |
| POST | `/workspaces/invitations/{invitation_id}/decline` | Отклонить приглашение |

---

## Workspace BC — Команды

Контроллер: `WorkspaceTeamController` | Префикс: `/workspaces`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/workspaces/{ws_id}/teams` | Список команд workspace |
| GET | `/workspaces/{ws_id}/teams/{team_id}` | Получить команду по UUID |
| POST | `/workspaces/{ws_id}/teams` | Создать команду |
| PATCH | `/workspaces/{ws_id}/teams/{team_id}` | Обновить команду (название, описание, лидер, иконка) |
| POST | `/workspaces/{ws_id}/teams/{team_id}/deactivate` | Деактивировать команду без удаления |
| POST | `/workspaces/{ws_id}/teams/{team_id}/reactivate` | Реактивировать деактивированную команду |
| POST | `/workspaces/{ws_id}/teams/{team_id}/members/{user_id}` | Добавить участника в команду |
| DELETE | `/workspaces/{ws_id}/teams/{team_id}/members/{user_id}` | Удалить участника из команды |

---

## Workspace BC — Роли

Контроллер: `WorkspaceRoleController` | Префикс: `/workspaces`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/workspaces/{ws_id}/roles` | Список ролей workspace (фильтр `system_only`) |
| GET | `/workspaces/{ws_id}/roles/{role_id}` | Получить роль по UUID |
| POST | `/workspaces/{ws_id}/roles` | Создать кастомную роль с разрешениями |
| PATCH | `/workspaces/{ws_id}/roles/{role_id}` | Обновить разрешения/описание кастомной роли |
| DELETE | `/workspaces/{ws_id}/roles/{role_id}` | Удалить кастомную роль (системные удалить нельзя) |

---

## Organization BC — Workspace (read-only)

Контроллер: `OrgWorkspaceController` | Префикс: `/orgs`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/orgs/{org_id}/workspaces` | Список workspace организации (только те, где пользователь — участник, или все при орг-разрешении `workspaces.read`) |

---

## Сводка по Bounded Context'ам

| BC | Контроллер | Кол-во endpoint'ов |
|----|-----------|-------------------|
| Identity | AuthController | 6 |
| Identity | AccountController | 11 |
| Identity | SecurityController | 13 |
| Identity | AdminController | 3 |
| Profile | ProfileController | 17 |
| Organization | OrganizationController | 10 |
| Organization | MemberController | 10 |
| Organization | InvitationController | 8 |
| Organization | DepartmentController | 7 |
| Organization | TeamController | 8 |
| Organization | RoleController | 5 |
| Organization | IntegrationController | 7 |
| Workspace | WorkspaceController | 18 |
| Workspace | WorkspaceMemberController | 8 |
| Workspace | WorkspaceInvitationController | 8 |
| Workspace | WorkspaceTeamController | 8 |
| Workspace | WorkspaceRoleController | 5 |
| Workspace | OrgWorkspaceController | 1 |
| **Итого** | | **153** |
