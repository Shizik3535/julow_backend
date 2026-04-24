# Notification BC — Спецификация

> Путь: `app/context/notification/domain`
> Исходные требования: §10 (Уведомления)

## Контекст

Notification BC отвечает за создание, доставку и настройку уведомлений. Получает события из других BC (Task, Communication, Billing, Security, FileStorage) и создаёт уведомления на основе настроек пользователя.

---

## Value Objects

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `NotificationType` | Enum | `TASK_ASSIGNED`, `MENTIONED`, `STATUS_CHANGED`, `DEADLINE_APPROACHING`, `OVERDUE_TASK`, `NEW_COMMENT`, `WATCHER_UPDATED`, `INVITED`, `SPRINT_COMPLETED`, `SYSTEM`, `BILLING`, `SECURITY` | §10.2 |
| `ChannelType` | Enum | `IN_APP`, `EMAIL`, `PUSH` | §10.1 |
| `NotificationPriority` | Enum | `LOW`, `MEDIUM`, `HIGH`, `URGENT` | — |
| `NotificationGroupKey` | frozen dataclass | key: str (для группировки) | §10.3 |

## Entities

| Сущность | Поля | Описание | Исходное требование |
|---|---|---|---|
| `DoNotDisturbSchedule` | start_hour, start_minute, end_hour, end_minute, enabled | Расписание DND | §10.3 |
| `DigestConfig` | is_enabled: bool, frequency: str (daily/weekly), preferred_hour: int | Настройка дайджеста | §10.3 |

## Domain Events

| Событие | Поля | Описание | Исходное требование |
|---|---|---|---|
| `NotificationCreated` | notification_id, recipient_id, notification_type | Уведомление создано | §10.1 |
| `NotificationRead` | notification_id | Уведомление прочитано | §10.3 |
| `NotificationMarkedAllRead` | user_id | Все уведомления прочитаны | §10.3 |
| `NotificationPreferencesUpdated` | user_id | Настройки обновлены | §10.3 |
| `DoNotDisturbEnabled` | user_id | DND включён | §10.3 |
| `DoNotDisturbDisabled` | user_id | DND отключён | §10.3 |
| `DigestSent` | user_id | Дайджест отправлен | §10.3 |

## Exceptions

| Исключение | Описание |
|---|---|
| `NotificationNotFoundException` | Уведомление не найдено |
| `NotificationPreferencesNotFoundException` | Настройки не найдены |

## Aggregates

### Notification (Aggregate Root)

Поля:
- recipient_id: Id
- notification_type: NotificationType
- title: str
- body: str
- priority: NotificationPriority
- is_read: bool
- group_key: NotificationGroupKey | None
- source_type: str | None (task, comment, meeting, etc.)
- source_id: Id | None (opaque, из другого BC)
- action_url: Url | None
- created_at: datetime

Методы:
- `create(recipient_id, notification_type, title, body, priority, source_type, source_id, action_url, group_key)` → `Notification` (factory)
- `mark_read()`

Инварианты:
- Созданное уведомление — unread
- group_key для группировки одинаковых уведомлений

### NotificationPreferences (Aggregate Root)

Поля:
- user_id: Id
- channel_preferences: dict ({NotificationType: [ChannelType]})
- dnd_schedule: DoNotDisturbSchedule | None
- digest_config: DigestConfig | None
- project_overrides: dict ({project_id: {type: [channels]}})
- created_at, updated_at

Методы:
- `update_channels(channel_preferences)`
- `enable_dnd(schedule)`
- `disable_dnd()`
- `set_project_override(project_id, preferences)` — §10.3
- `remove_project_override(project_id)` — §10.3

Инварианты:
- Каждый тип уведомления имеет хотя бы один канал
- DND расписание — опционально
- Project overrides не могут полностью отключить SECURITY/BILLING уведомления

## Repositories

| Репозиторий | Методы |
|---|---|
| `NotificationRepository` | `get_by_id`, `get_unread_by_user`, `get_by_user`, `count_unread`, `mark_all_read` |
| `NotificationPreferencesRepository` | `get_by_user_id` |
