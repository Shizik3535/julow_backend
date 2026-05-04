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
| GET | `/orgs/invitations/mine` | Мои приглашения в организации (PENDING по email, ACCEPTED/DECLINED по user_id) |

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
| POST | `/workspaces/{ws_id}/logo` | Загрузить логотип workspace |
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
| GET | `/workspaces/invitations/mine` | Мои приглашения в workspace (PENDING по email, ACCEPTED/DECLINED по user_id) |

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

## Project BC — Мои проекты и поиск

Контроллер: `MyProjectsController` | Префикс: `/projects`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/projects/mine` | Проекты текущего пользователя |
| GET | `/projects/` | Глобальный поиск проектов (фильтры: query, workspace_id) |

---

## Project BC — Проекты

Контроллер: `ProjectController` | Префикс: `/workspaces/{ws_id}/projects`

| Метод | URI | Описание |
|-------|-----|----------|
| POST | `/workspaces/{ws_id}/projects/` | Создать проект |
| GET | `/workspaces/{ws_id}/projects/` | Список проектов workspace |
| GET | `/workspaces/{ws_id}/projects/archived` | Архивированные проекты |
| GET | `/workspaces/{ws_id}/projects/{project_id}` | Получить проект |
| PATCH | `/workspaces/{ws_id}/projects/{project_id}` | Обновить информацию (название, описание, иконка, цвет, категория, даты) |
| POST | `/workspaces/{ws_id}/projects/{project_id}/archive` | Архивировать проект |
| POST | `/workspaces/{ws_id}/projects/{project_id}/restore` | Восстановить проект из архива |
| POST | `/workspaces/{ws_id}/projects/{project_id}/suspend` | Приостановить проект (с указанием причины) |
| POST | `/workspaces/{ws_id}/projects/{project_id}/reactivate` | Реактивировать проект |
| POST | `/workspaces/{ws_id}/projects/{project_id}/request-deletion` | Запросить удаление проекта |
| POST | `/workspaces/{ws_id}/projects/{project_id}/transfer-ownership` | Передать владение проектом |
| POST | `/workspaces/{ws_id}/projects/{project_id}/owners` | Добавить со-владельца |
| DELETE | `/workspaces/{ws_id}/projects/{project_id}/owners/{user_id}` | Удалить со-владельца |
| PATCH | `/workspaces/{ws_id}/projects/{project_id}/methodology` | Сменить методологию (kanban, scrum, waterfall, hybrid, shape_up) |
| PATCH | `/workspaces/{ws_id}/projects/{project_id}/visibility` | Сменить видимость (private, workspace, organization, public) |
| POST | `/workspaces/{ws_id}/projects/{project_id}/custom-fields` | Добавить кастомное поле |
| PATCH | `/workspaces/{ws_id}/projects/{project_id}/custom-fields/{field_name}` | Обновить кастомное поле |
| DELETE | `/workspaces/{ws_id}/projects/{project_id}/custom-fields/{field_name}` | Удалить кастомное поле |
| POST | `/workspaces/{ws_id}/projects/{project_id}/milestones` | Добавить milestone |
| PATCH | `/workspaces/{ws_id}/projects/{project_id}/milestones/{milestone_id}` | Обновить milestone |
| POST | `/workspaces/{ws_id}/projects/{project_id}/milestones/{milestone_id}/change-status` | Изменить статус milestone |

---

## Project BC — Участники проекта

Контроллер: `ProjectMemberController` | Префикс: `/workspaces/{ws_id}/projects`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/workspaces/{ws_id}/projects/{project_id}/members` | Список участников проекта |
| GET | `/workspaces/{ws_id}/projects/{project_id}/members/{user_id}` | Получить участника проекта |
| POST | `/workspaces/{ws_id}/projects/{project_id}/members` | Добавить участника в проект |
| PATCH | `/workspaces/{ws_id}/projects/{project_id}/members/{user_id}/role` | Изменить роль участника |
| DELETE | `/workspaces/{ws_id}/projects/{project_id}/members/{user_id}` | Удалить участника из проекта |
| POST | `/workspaces/{ws_id}/projects/{project_id}/members/{user_id}/deactivate` | Деактивировать участника |
| POST | `/workspaces/{ws_id}/projects/{project_id}/members/{user_id}/reactivate` | Реактивировать участника |

---

## Project BC — Роли проекта

Контроллер: `ProjectRoleController` | Префикс: `/workspaces/{ws_id}/projects`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/workspaces/{ws_id}/projects/{project_id}/roles` | Список ролей проекта |
| GET | `/workspaces/{ws_id}/projects/{project_id}/roles/{role_id}` | Получить роль проекта |
| POST | `/workspaces/{ws_id}/projects/{project_id}/roles` | Создать кастомную роль |
| PATCH | `/workspaces/{ws_id}/projects/{project_id}/roles/{role_id}` | Обновить роль (разрешения, описание) |
| DELETE | `/workspaces/{ws_id}/projects/{project_id}/roles/{role_id}` | Удалить кастомную роль |

---

## Project BC — Спринты

Контроллер: `SprintController` | Префикс: `/workspaces/{ws_id}/projects`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/workspaces/{ws_id}/projects/{project_id}/sprints` | Список спринтов проекта |
| GET | `/workspaces/{ws_id}/projects/{project_id}/sprints/active` | Активный спринт |
| GET | `/workspaces/{ws_id}/projects/{project_id}/sprints/{sprint_id}` | Получить спринт |
| POST | `/workspaces/{ws_id}/projects/{project_id}/sprints` | Создать спринт |
| POST | `/workspaces/{ws_id}/projects/{project_id}/sprints/{sprint_id}/start` | Запустить спринт |
| PATCH | `/workspaces/{ws_id}/projects/{project_id}/sprints/{sprint_id}/goal` | Обновить цель спринта |
| PATCH | `/workspaces/{ws_id}/projects/{project_id}/sprints/{sprint_id}/date-range` | Обновить даты спринта |
| POST | `/workspaces/{ws_id}/projects/{project_id}/sprints/{sprint_id}/retro` | Создать ретроспективу спринта |
| POST | `/workspaces/{ws_id}/projects/{project_id}/sprints/{sprint_id}/complete` | Завершить спринт |
| POST | `/workspaces/{ws_id}/projects/{project_id}/sprints/{sprint_id}/cancel` | Отменить спринт |

---

## Project BC — Эпики

Контроллер: `EpicController` | Префикс: `/workspaces/{ws_id}/projects`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/workspaces/{ws_id}/projects/{project_id}/epics` | Список эпиков проекта |
| GET | `/workspaces/{ws_id}/projects/{project_id}/epics/{epic_id}` | Получить эпик |
| POST | `/workspaces/{ws_id}/projects/{project_id}/epics` | Создать эпик |
| PATCH | `/workspaces/{ws_id}/projects/{project_id}/epics/{epic_id}` | Обновить эпик |
| POST | `/workspaces/{ws_id}/projects/{project_id}/epics/{epic_id}/change-status` | Изменить статус эпика |

---

## Project BC — Доска

Контроллер: `ProjectBoardController` | Префикс: `/workspaces/{ws_id}/projects`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/workspaces/{ws_id}/projects/{project_id}/board` | Получить доску проекта |
| POST | `/workspaces/{ws_id}/projects/{project_id}/board/columns` | Добавить колонку |
| DELETE | `/workspaces/{ws_id}/projects/{project_id}/board/columns/{column_id}` | Удалить колонку |
| PUT | `/workspaces/{ws_id}/projects/{project_id}/board/columns/reorder` | Переупорядочить колонки |
| PATCH | `/workspaces/{ws_id}/projects/{project_id}/board/columns/{column_id}/wip-limit` | Изменить WIP-лимит колонки |
| POST | `/workspaces/{ws_id}/projects/{project_id}/board/swimlanes` | Добавить swimlane |
| DELETE | `/workspaces/{ws_id}/projects/{project_id}/board/swimlanes/{swimlane_id}` | Удалить swimlane |
| POST | `/workspaces/{ws_id}/projects/{project_id}/board/workflow/statuses` | Добавить статус workflow |
| DELETE | `/workspaces/{ws_id}/projects/{project_id}/board/workflow/statuses/{status_id}` | Удалить статус workflow |
| POST | `/workspaces/{ws_id}/projects/{project_id}/board/workflow/transitions` | Добавить переход workflow |
| DELETE | `/workspaces/{ws_id}/projects/{project_id}/board/workflow/transitions/{transition_id}` | Удалить переход workflow |
| PATCH | `/workspaces/{ws_id}/projects/{project_id}/board/views/{view_id}` | Обновить представление |
| DELETE | `/workspaces/{ws_id}/projects/{project_id}/board/views/{view_id}` | Удалить представление |
| PATCH | `/workspaces/{ws_id}/projects/{project_id}/board/automations/{rule_id}` | Обновить правило автоматизации |
| DELETE | `/workspaces/{ws_id}/projects/{project_id}/board/automations/{rule_id}` | Удалить правило автоматизации |

---

## Project BC — Системные шаблоны ретроспектив

Контроллер: `RetroTemplateController` | Префикс: `/retro-templates`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/retro-templates/` | Список системных шаблонов ретроспектив |

---

## Project BC — Кастомные шаблоны ретроспектив workspace

Контроллер: `WorkspaceRetroTemplateController` | Префикс: `/workspaces/{ws_id}/retro-templates`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/workspaces/{ws_id}/retro-templates/` | Список шаблонов ретроспектив workspace |
| POST | `/workspaces/{ws_id}/retro-templates/` | Создать кастомный шаблон |
| PATCH | `/workspaces/{ws_id}/retro-templates/{template_id}` | Обновить шаблон |
| DELETE | `/workspaces/{ws_id}/retro-templates/{template_id}` | Удалить шаблон |

---

## Task BC — Мои задачи

Контроллер: `MyTasksController` | Префикс: `/tasks`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/tasks/mine` | Мои задачи (кросс-проектный поиск с фильтрацией) |
| GET | `/tasks/mine/overdue` | Мои просроченные задачи |

---

## Task BC — Задачи проекта

Контроллер: `TaskController` | Префикс: `/workspaces/{ws_id}/projects`

| Метод | URI | Описание |
|-------|-----|----------|
| POST | `/workspaces/{ws_id}/projects/{project_id}/tasks` | Создать задачу |
| POST | `/workspaces/{ws_id}/projects/{project_id}/tasks/from-template` | Создать задачу из шаблона |
| GET | `/workspaces/{ws_id}/projects/{project_id}/tasks` | Поиск задач проекта (пагинация, фильтры) |
| GET | `/workspaces/{ws_id}/projects/{project_id}/tasks/count` | Счётчик задач проекта |
| GET | `/workspaces/{ws_id}/projects/{project_id}/tasks/count-by-status/{status_id}` | Счётчик задач по статусу |
| POST | `/workspaces/{ws_id}/projects/{project_id}/tasks/bulk` | Массовое обновление задач |

---

## Task BC — Операции с задачей

Контроллер: `TaskDetailController` | Префикс: `/tasks`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/tasks/{task_id}` | Получить задачу |
| PATCH | `/tasks/{task_id}` | Обновить информацию (заголовок, описание, даты) |
| DELETE | `/tasks/{task_id}` | Удалить задачу |
| POST | `/tasks/{task_id}/archive` | Архивировать задачу |
| POST | `/tasks/{task_id}/restore` | Восстановить из архива |
| POST | `/tasks/{task_id}/change-status` | Сменить workflow-статус |
| POST | `/tasks/{task_id}/change-priority` | Сменить приоритет |
| POST | `/tasks/{task_id}/change-type` | Сменить тип задачи |
| POST | `/tasks/{task_id}/move` | Переместить на доске (drag-n-drop) |
| PATCH | `/tasks/{task_id}/effort-estimate` | Установить оценку усилия |
| PATCH | `/tasks/{task_id}/actual-effort` | Установить фактическое усилие |
| PATCH | `/tasks/{task_id}/progress` | Обновить прогресс (0–100) |
| POST | `/tasks/{task_id}/compute-progress` | Вычислить прогресс из чек-листов |

---

## Task BC — Исполнители, спринты, эпики

Контроллер: `TaskAssigneeController` | Префикс: `/tasks`

| Метод | URI | Описание |
|-------|-----|----------|
| POST | `/tasks/{task_id}/assignees` | Назначить исполнителя |
| DELETE | `/tasks/{task_id}/assignees/{assignee_id}` | Снять исполнителя |
| POST | `/tasks/{task_id}/sprint` | Привязать к спринту |
| DELETE | `/tasks/{task_id}/sprint` | Убрать из спринта |
| POST | `/tasks/{task_id}/epic` | Привязать к эпику |
| DELETE | `/tasks/{task_id}/epic` | Убрать из эпика |

---

## Task BC — Чек-листы

Контроллер: `TaskChecklistController` | Префикс: `/tasks`

| Метод | URI | Описание |
|-------|-----|----------|
| POST | `/tasks/{task_id}/checklists` | Добавить чек-лист |
| DELETE | `/tasks/{task_id}/checklists/{checklist_id}` | Удалить чек-лист |
| POST | `/tasks/{task_id}/checklists/{checklist_id}/items` | Добавить пункт |
| POST | `/tasks/{task_id}/checklists/{checklist_id}/items/{item_id}/toggle` | Переключить пункт |
| POST | `/tasks/{task_id}/checklists/{checklist_id}/items/{item_id}/assign` | Назначить исполнителя пункта |

---

## Task BC — Связи между задачами

Контроллер: `TaskRelationController` | Префикс: `/tasks`

| Метод | URI | Описание |
|-------|-----|----------|
| POST | `/tasks/{task_id}/relations` | Добавить связь |
| DELETE | `/tasks/{task_id}/relations/{related_task_id}` | Удалить связь |

---

## Task BC — Метаданные

Контроллер: `TaskMetadataController` | Префикс: `/tasks`

| Метод | URI | Описание |
|-------|-----|----------|
| POST | `/tasks/{task_id}/labels` | Добавить метку |
| DELETE | `/tasks/{task_id}/labels/{label}` | Удалить метку |
| POST | `/tasks/{task_id}/watchers` | Добавить наблюдателя |
| DELETE | `/tasks/{task_id}/watchers/{user_id}` | Удалить наблюдателя |
| POST | `/tasks/{task_id}/attachments` | Загрузить вложение |
| DELETE | `/tasks/{task_id}/attachments/{file_id}` | Удалить вложение |
| POST | `/tasks/{task_id}/custom-fields` | Установить кастомное поле |
| DELETE | `/tasks/{task_id}/custom-fields/{field_name}` | Удалить кастомное поле |
| POST | `/tasks/{task_id}/recurrence` | Установить повторение |
| DELETE | `/tasks/{task_id}/recurrence` | Удалить повторение |

---

## Task BC — История и подзадачи

Контроллер: `TaskHistoryController` | Префикс: `/tasks`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/tasks/{task_id}/subtasks` | Подзадачи |
| GET | `/tasks/{task_id}/changelog` | История изменений задачи |
| GET | `/tasks/{task_id}/changelog/{field_name}` | История изменений поля |

---

## Task BC — Системные шаблоны задач

Контроллер: `TaskTemplateController` | Префикс: `/task-templates`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/task-templates/` | Список системных шаблонов |
| GET | `/task-templates/{template_id}` | Получить шаблон по UUID |

---

## Task BC — Шаблоны задач проекта

Контроллер: `ProjectTaskTemplateController` | Префикс: `/workspaces/{ws_id}/projects`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/workspaces/{ws_id}/projects/{project_id}/task-templates` | Список шаблонов проекта |
| POST | `/workspaces/{ws_id}/projects/{project_id}/task-templates` | Создать шаблон |
| PATCH | `/workspaces/{ws_id}/projects/{project_id}/task-templates/{template_id}` | Обновить шаблон |
| DELETE | `/workspaces/{ws_id}/projects/{project_id}/task-templates/{template_id}` | Удалить шаблон |

---

## Notification BC — Уведомления

Контроллер: `NotificationController` | Префикс: `/notifications`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/notifications/connection-info` | Информация о подключении к real-time уведомлениям (WebSocket URL, протокол, типы событий) |
| GET | `/notifications/` | Получить список уведомлений с фильтрацией и пагинацией |
| GET | `/notifications/unread-count` | Количество непрочитанных уведомлений (в т.ч. по workspace) |
| PATCH | `/notifications/{notification_id}/read` | Пометить уведомление как прочитанное |
| POST | `/notifications/read-all` | Пометить все уведомления как прочитанные |
| PATCH | `/notifications/{notification_id}/archive` | Архивировать уведомление |

---

## Notification BC — Настройки уведомлений

Контроллер: `NotificationSettingsController` | Префикс: `/notification-settings`

| Метод | URI | Описание |
|-------|-----|----------|
| GET | `/notification-settings/preferences` | Получить настройки уведомлений |
| POST | `/notification-settings/preferences` | Установить настройку (тип ↔ канал) |
| PUT | `/notification-settings/reminder-window` | Установить окно напоминания о дедлайне (кол-во часов) |
| GET | `/notification-settings/types` | Получить доступные типы уведомлений |
| GET | `/notification-settings/dnd` | Получить настройки «Не беспокоить» |
| PUT | `/notification-settings/dnd` | Обновить расписание DND |
| POST | `/notification-settings/dnd/disable` | Отключить DND |
| GET | `/notification-settings/digest` | Получить настройки дайджеста |
| PUT | `/notification-settings/digest` | Обновить настройки дайджеста |
| GET | `/notification-settings/devices` | Список зарегистрированных устройств |
| POST | `/notification-settings/devices` | Зарегистрировать push-токен устройства |
| DELETE | `/notification-settings/devices/{device_token_id}` | Удалить устройство |

---

## WebSocket — Real-time уведомления

| URI | Описание |
|-----|----------|
| `/ws/notifications?token=<jwt>` | WebSocket-эндпоинт для получения уведомлений в реальном времени |

Протокол:
- Сервер отправляет JSON: `{"event_type": "...", "payload": {...}}`
- Клиент отправляет `"ping"` для heartbeat, сервер отвечает `"pong"`
- Типы событий сервера: `notification.created`, `notification.read`, `notification.all_read`, `notification.archived`

Подключение:
1. Вызвать `GET /notifications/connection-info` для получения URL и параметров
2. Подключиться к WebSocket: `new WebSocket(url + "?token=" + jwt)`
3. Отправлять `"ping"` каждые 30 секунд для поддержания соединения

---

## Сводка по Bounded Context'ам

| BC | Контроллер | Кол-во endpoint'ов |
|----|-----------|-------------------|
| Identity | AuthController | 6 |
| Identity | AccountController | 11 |
| Identity | SecurityController | 13 |
| Identity | AdminController | 3 |
| Profile | ProfileController | 16 |
| Organization | OrganizationController | 10 |
| Organization | MemberController | 10 |
| Organization | InvitationController | 9 |
| Organization | DepartmentController | 7 |
| Organization | TeamController | 8 |
| Organization | RoleController | 5 |
| Organization | IntegrationController | 7 |
| Workspace | WorkspaceController | 19 |
| Workspace | WorkspaceMemberController | 8 |
| Workspace | WorkspaceInvitationController | 9 |
| Workspace | WorkspaceTeamController | 8 |
| Workspace | WorkspaceRoleController | 5 |
| Workspace | OrgWorkspaceController | 1 |
| Project | MyProjectsController | 2 |
| Project | ProjectController | 21 |
| Project | ProjectMemberController | 7 |
| Project | ProjectRoleController | 5 |
| Project | SprintController | 10 |
| Project | EpicController | 5 |
| Project | ProjectBoardController | 15 |
| Project | RetroTemplateController | 1 |
| Project | WorkspaceRetroTemplateController | 4 |
| Task | MyTasksController | 2 |
| Task | TaskController | 6 |
| Task | TaskDetailController | 13 |
| Task | TaskAssigneeController | 6 |
| Task | TaskChecklistController | 5 |
| Task | TaskRelationController | 2 |
| Task | TaskMetadataController | 10 |
| Task | TaskHistoryController | 3 |
| Task | TaskTemplateController | 2 |
| Task | ProjectTaskTemplateController | 4 |
| Notification | NotificationController | 6 |
| Notification | NotificationSettingsController | 12 |
| **Итого** | | **286** |
