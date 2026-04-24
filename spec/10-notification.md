# 10. Notification — Уведомления

## Обзор

Контекст уведомлений — подписчик (subscriber) на события из всех остальных контекстов. Отвечает за доставку уведомлений через in-app, email и push-каналы. Пользователь управляет настройками уведомлений на глобальном, проектном и task-уровне.

---

## Принципы расширяемости

1. **NotificationType — расширяемый enum** — новые типы уведомлений = значение enum. Маршрутизация и шаблоны на app-слое.
2. **ChannelType — расширяемый enum** — `IN_APP`, `EMAIL`, `PUSH`, `WEBHOOK`. Новые каналы (SMS, Telegram) = значение enum + handler на infrastructure.
3. **NotificationPriority — enum** — `LOW`, `NORMAL`, `HIGH`, `URGENT`. Определяет порядок доставки и bypass DND.
4. **NotificationGroupKey — VO** — группировка однотипных уведомлений. Новые группировки = расширение.
5. **DoNotDisturbSchedule — entity** — расписание DND, а не просто on/off.
6. **DigestConfig — entity** — конфигурация дайджестов с кастомной частотой.

---

## 1. Функциональные требования

### 1.1. Каналы уведомлений

| Канал | Free | Start | Business | Enterprise |
|-------|------|-------|----------|------------|
| In-app | ✅ | ✅ | ✅ | ✅ |
| Email | ✅ | ✅ | ✅ | ✅ |
| Push (mobile/desktop) | ❌ | ✅ | ✅ | ✅ |
| Webhook | ❌ | ❌ | ✅ | ✅ |

### 1.2. Типы уведомлений

| Тип | Описание | Каналы по умолчанию |
|-----|----------|-------------------|
| `task_assigned` | Назначение на задачу | in-app, email |
| `task_unassigned` | Снятие с задачи | in-app |
| `mention` | Упоминание (@mention) | in-app, email |
| `task_status_changed` | Изменение статуса задачи | in-app |
| `task_due_approaching` | Приближение дедлайна (1 день, 3 дня) | in-app, email |
| `task_overdue` | Просроченная задача | in-app, email |
| `task_comment` | Новый комментарий к задаче | in-app |
| `task_updated` | Изменение в задаче (для watchers) | in-app |
| `project_invitation` | Приглашение в проект | in-app, email |
| `workspace_invitation` | Приглашение в workspace | in-app, email |
| `organization_invitation` | Приглашение в организацию | email |
| `sprint_completed` | Завершение спринта | in-app |
| `sprint_started` | Начало спринта | in-app |
| `meeting_scheduled` | Запланирована встреча | in-app, email |
| `meeting_cancelled` | Встреча отменена | in-app, email |
| `meeting_reminder` | Напоминание о встрече (15 мин) | in-app, push |
| `billing_payment_success` | Успешная оплата | email |
| `billing_payment_failed` | Неудачная оплата | in-app, email |
| `billing_trial_ending` | Окончание trial (3 дня) | in-app, email |
| `billing_quota_warning` | Приближение к лимиту | in-app |
| `security_new_device` | Вход с нового устройства | email |
| `security_password_changed` | Пароль изменён | email |
| `security_2fa_changed` | 2FA включена/выключена | email |
| `system_maintenance` | Плановые работы | in-app, email |
| `time_reminder` | Напоминание о незаполненном времени | in-app, push |

### 1.3. Настройки уведомлений

| Требование | Free | Start | Business | Enterprise |
|-----------|------|-------|----------|------------|
| Глобальные настройки (по типам) | ✅ | ✅ | ✅ | ✅ |
| Настройки по каналам | ✅ | ✅ | ✅ | ✅ |
| Настройки на уровне проекта | ❌ | ✅ | ✅ | ✅ |
| Subscribe/unsubscribe на задачу | ✅ | ✅ | ✅ | ✅ |
| «Не беспокоить» (расписание) | ✅ | ✅ | ✅ | ✅ |
| Дайджест (ежедневный/еженедельный) | ❌ | ✅ | ✅ | ✅ |
| Группировка уведомлений | ✅ | ✅ | ✅ | ✅ |
| Mark as read / Mark all as read | ✅ | ✅ | ✅ | ✅ |

---

## 2. Доменная модель

### Value Objects

| VO | Тип | Описание |
|---|---|---|
| `NotificationType` | Enum | `TASK_ASSIGNED`, `TASK_UNASSIGNED`, `MENTION`, `TASK_STATUS_CHANGED`, `TASK_DUE_APPROACHING`, `TASK_OVERDUE`, `TASK_COMMENT`, `TASK_UPDATED`, `PROJECT_INVITATION`, `WORKSPACE_INVITATION`, `ORGANIZATION_INVITATION`, `SPRINT_COMPLETED`, `SPRINT_STARTED`, `MEETING_SCHEDULED`, `MEETING_CANCELLED`, `MEETING_REMINDER`, `BILLING_PAYMENT_SUCCESS`, `BILLING_PAYMENT_FAILED`, `BILLING_TRIAL_ENDING`, `BILLING_QUOTA_WARNING`, `SECURITY_NEW_DEVICE`, `SECURITY_PASSWORD_CHANGED`, `SECURITY_2FA_CHANGED`, `SYSTEM_MAINTENANCE`, `TIME_REMINDER` |
| `ChannelType` | Enum | `IN_APP`, `EMAIL`, `PUSH`, `WEBHOOK` |
| `NotificationPriority` | Enum | `LOW`, `NORMAL`, `HIGH`, `URGENT` |
| `PreferenceScope` | Enum | `GLOBAL`, `PROJECT`, `WORKSPACE` |
| `DigestFrequency` | Enum | `DAILY`, `WEEKLY` |
| `NotificationGroupKey` | frozen dataclass | type: NotificationType, target_id: Id \| None, window_minutes: int |

> **`NotificationPriority`** — `URGENT` и `HIGH` bypass DND. `LOW` может быть отложена до дайджеста. Приоритет определяется на app-слое по типу события.
>
> **`NotificationGroupKey`** — однотипные уведомления за `window_minutes` группируются. Например, 5 комментариев к одной задаче за 5 минут → 1 уведомление.

### Entities

| Сущность | Поля | Описание |
|---|---|---|
| `DoNotDisturbSchedule` | enabled: bool, schedule_start: time \| None, schedule_end: time \| None, schedule_days: list[int] \| None, timezone: str | Расписание DND |
| `DigestConfig` | enabled: bool, frequency: DigestFrequency, delivery_time: time, delivery_day: int \| None (для weekly), timezone: str | Конфигурация дайджеста |

> **TaskWatcher** — принадлежит Task BC (TaskWatcher entity в Task AR). Notification BC потребляет `TaskWatcherAdded`/`TaskWatcherRemoved` events.

### Aggregates

#### Notification (Aggregate Root)

Поля:
- user_id: Id — получатель
- workspace_id: Id | None
- type: NotificationType
- priority: NotificationPriority
- title: str
- body: str
- data: dict — контекстные данные (task_id, project_id, etc.)
- channels: list[ChannelType] — через какие каналы отправлено
- group_key: NotificationGroupKey | None
- is_read: bool
- read_at: datetime | None
- is_archived: bool
- actor_id: Id | None — кто инициировал (null для системных)
- created_at: datetime

Методы:
- `create(user_id, type, title, body, data, channels, priority=NORMAL, workspace_id=None, actor_id=None, group_key=None)` → `Notification`
- `mark_as_read()`
- `archive()`

Инварианты:
- Прочитанное уведомление нельзя пометить как непрочитанное
- Архивированное уведомление не отображается в списке

#### NotificationPreferences (Aggregate Root)

Поля:
- user_id: Id
- preferences: list[PreferenceEntry] — type → channel → enabled, scope
- dnd: DoNotDisturbSchedule
- digest: DigestConfig

Где `PreferenceEntry`:
- notification_type: NotificationType
- channel: ChannelType
- enabled: bool
- scope: PreferenceScope
- scope_id: Id | None — project_id или workspace_id

Методы:
- `create(user_id)` → `NotificationPreferences` (factory, defaults)
- `set_preference(type, channel, enabled, scope=GLOBAL, scope_id=None)`
- `update_dnd(schedule: DoNotDisturbSchedule)`
- `update_digest(config: DigestConfig)`
- `is_dnd_active(now: datetime)` → bool
- `should_deliver(type, channel, scope_id=None)` → bool
- `mark_all_read(workspace_id=None)` → int (count)

Инварианты:
- DND exceptions: security- и billing-уведомления всегда доставляются
- Project-level override перекрывает глобальные настройки
- Digest enabled → отдельные email заменяются на сводку

---

## 3. Бизнес-правила

1. **DND**: при активном DND — in-app и push не отправляются; email откладывается до окончания DND
2. **DND exceptions**: security- и billing-уведомления всегда доходят
3. **Digest**: при включённом дайджесте — отдельные email заменяются на сводку
4. **Watchers**: автоматически подписываются: assignee, reporter, commenters задачи
5. **Unsubscribe**: при отписке от задачи — перестают приходить все уведомления по ней
6. **Project-level override**: настройки на уровне проекта перекрывают глобальные
7. **Grouping**: однотипные уведомления за короткий период (< 5 мин) группируются
8. **Mark all as read**: помечает все непрочитанные уведомления в текущем workspace
9. **Retention**: уведомления хранятся 90 дней, затем архивируются; архив — 1 год
10. **Real-time**: in-app уведомления доставляются через WebSocket

---

## 4. API Endpoints

### 4.1. Уведомления

```
GET /api/v1/notifications
```

**Query params:** `workspace_id`, `type`, `is_read`, `page`, `limit`

**Response (200):**
```json
{
  "items": [
    {
      "id": "uuid",
      "type": "task_assigned",
      "title": "You were assigned to API-42",
      "body": "John Doe assigned you to \"Implement auth\"",
      "data": {
        "task_id": "task_uuid",
        "task_key": "API-42",
        "project_id": "project_uuid",
        "workspace_id": "ws_uuid"
      },
      "actor": {"id": "uuid", "display_name": "John Doe", "avatar_url": "..."},
      "is_read": false,
      "created_at": "2025-02-01T10:00:00Z"
    }
  ],
  "total": 50,
  "unread_count": 12
}
```

---

```
GET /api/v1/notifications/unread-count
```

**Response (200):**
```json
{
  "total": 12,
  "by_workspace": {
    "ws_uuid_1": 8,
    "ws_uuid_2": 4
  }
}
```

---

```
POST /api/v1/notifications/{notification_id}/read
```

---

```
POST /api/v1/notifications/read-all
```

**Request:**
```json
{
  "workspace_id": "ws_uuid"
}
```

---

```
POST /api/v1/notifications/{notification_id}/archive
```

### 4.2. Настройки

```
GET /api/v1/notifications/preferences
```

**Response (200):**
```json
{
  "global": [
    {"type": "task_assigned", "in_app": true, "email": true, "push": true},
    {"type": "task_comment", "in_app": true, "email": false, "push": false}
  ],
  "project_overrides": [
    {
      "project_id": "uuid",
      "project_name": "Backend API",
      "preferences": [
        {"type": "task_comment", "in_app": true, "email": true, "push": false}
      ]
    }
  ]
}
```

---

```
PUT /api/v1/notifications/preferences
```

**Request:**
```json
{
  "scope": "global",
  "preferences": [
    {"type": "task_assigned", "in_app": true, "email": true, "push": true},
    {"type": "task_comment", "in_app": true, "email": false, "push": false}
  ]
}
```

---

```
PUT /api/v1/notifications/preferences/project/{project_id}
```

### 4.3. Task Watchers

```
POST /api/v1/workspaces/{ws_id}/projects/{project_id}/tasks/{task_id}/watch
```

---

```
DELETE /api/v1/workspaces/{ws_id}/projects/{project_id}/tasks/{task_id}/watch
```

---

```
GET /api/v1/workspaces/{ws_id}/projects/{project_id}/tasks/{task_id}/watchers
```

### 4.4. Do Not Disturb

```
GET /api/v1/notifications/dnd
```

---

```
PUT /api/v1/notifications/dnd
```

**Request:**
```json
{
  "enabled": true,
  "schedule_enabled": true,
  "schedule_start": "22:00",
  "schedule_end": "08:00",
  "schedule_days": [0, 1, 2, 3, 4, 5, 6],
  "schedule_timezone": "Europe/Moscow"
}
```

### 4.5. Digest

```
GET /api/v1/notifications/digest
```

---

```
PUT /api/v1/notifications/digest
```

**Request:**
```json
{
  "enabled": true,
  "frequency": "daily",
  "delivery_time": "09:00",
  "timezone": "Europe/Moscow"
}
```

---

## 5. Схема БД

### Таблица: `notifications`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| user_id | UUID | FK → users.id, NOT NULL | Получатель |
| workspace_id | UUID | NULLABLE | |
| type | VARCHAR(50) | NOT NULL | |
| title | VARCHAR(200) | NOT NULL | |
| body | TEXT | NOT NULL | |
| data | JSONB | NOT NULL, DEFAULT '{}' | |
| channels | JSONB | NOT NULL, DEFAULT '[]' | |
| is_read | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| read_at | TIMESTAMPTZ | NULLABLE | |
| is_archived | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| actor_id | UUID | FK → users.id, NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_notif_user_unread` — на `(user_id, is_read, created_at DESC)` WHERE `is_read = FALSE`
- `idx_notif_user_ws` — на `(user_id, workspace_id, created_at DESC)`
- `idx_notif_created` — на `created_at` (для cleanup job)

### Таблица: `notification_preferences`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| user_id | UUID | FK → users.id, NOT NULL | |
| notification_type | VARCHAR(50) | NOT NULL | |
| channel | VARCHAR(20) | NOT NULL | |
| enabled | BOOLEAN | NOT NULL, DEFAULT TRUE | |
| scope | VARCHAR(20) | NOT NULL, DEFAULT 'global' | |
| scope_id | UUID | NULLABLE | project_id or workspace_id |

**Индексы:**
- `idx_np_user_type` — на `(user_id, notification_type, scope, scope_id)`

### Таблица: `task_watchers`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| task_id | UUID | FK → tasks.id, NOT NULL | |
| user_id | UUID | FK → users.id, NOT NULL | |
| subscribed_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_tw_pk` — PRIMARY KEY на `(task_id, user_id)`
- `idx_tw_user` — на `user_id`

### Таблица: `dnd_settings`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| user_id | UUID | PK, FK → users.id | |
| enabled | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| schedule_enabled | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| schedule_start | TIME | NULLABLE | |
| schedule_end | TIME | NULLABLE | |
| schedule_days | JSONB | NULLABLE | |
| schedule_timezone | VARCHAR(50) | NOT NULL, DEFAULT 'UTC' | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

### Таблица: `digest_settings`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| user_id | UUID | PK, FK → users.id | |
| enabled | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| frequency | VARCHAR(10) | NOT NULL, DEFAULT 'daily' | |
| delivery_time | TIME | NOT NULL, DEFAULT '09:00' | |
| delivery_day | INTEGER | NULLABLE | 0=Mon for weekly |
| timezone | VARCHAR(50) | NOT NULL, DEFAULT 'UTC' | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

---

## 6. Доменные события

| Событие | Поля | Описание |
|---|---|---|
| `NotificationCreated` | notification_id, user_id, type, priority, channels | Уведомление создано |
| `NotificationRead` | notification_id, user_id | Прочитано |
| `AllNotificationsRead` | user_id, workspace_id \| None, count | Все прочитаны |
| `NotificationArchived` | notification_id | Архивировано |
| `NotificationPreferenceUpdated` | user_id, notification_type, channel, enabled, scope | Настройка обновлена |
| `DndSettingsUpdated` | user_id, enabled | DND обновлён |
| `DigestSettingsUpdated` | user_id, enabled, frequency | Дайджест обновлён |
| `DigestSent` | user_id, notification_count, period | Дайджест отправлен |

---

## 7. Exceptions

| Исключение | Описание |
|---|---|
| `NotificationNotFoundException` | Уведомление не найдено |
| `NotificationAlreadyReadException` | Уведомление уже прочитано |
| `NotificationPreferencesNotFoundException` | Настройки не найдены |
| `InvalidDndScheduleException` | Некорректное расписание DND |
| `InvalidDigestConfigException` | Некорректная конфигурация дайджеста |

---

## 8. Repositories

| Репозиторий | Методы |
|---|---|
| `NotificationRepository` | `get_by_id`, `get_by_user`, `get_unread_by_user`, `get_by_user_and_workspace`, `count_unread`, `count_unread_by_workspace`, `get_by_group_key`, `get_archived` |
| `NotificationPreferencesRepository` | `get_by_user`, `get_by_user_and_scope` |
