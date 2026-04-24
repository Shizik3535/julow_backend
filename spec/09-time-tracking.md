# 09. Time Tracking — Учёт времени

## Обзор

Контекст учёта времени позволяет трекать затраченное время на задачи. Поддерживается таймер (start/stop) и ручной ввод. Данные используются для отчётов по трудозатратам, сравнения оценок и фактических затрат.

**Доступность:** Free ❌ | Start ✅ | Business ✅ | Enterprise ✅

---

## Принципы расширяемости

1. **ActivityCategory — entity** — категории активности (Development, Meeting, Code Review, etc.) с `is_system` flag. Новые категории = запись, не правка домена.
2. **TimeEntryTag — entity** — теги для записей (billable, overtime, etc.). Новые теги = запись.
3. **ApprovalStatus — enum** — `PENDING`, `APPROVED`, `REJECTED`. Для согласования записей менеджером.
4. **RejectionReason — entity** — причина отклонения записи.
5. **Events с `changed_fields`** — детализация обновлений.

---

## 1. Функциональные требования

### 1.1. Трекинг

| Требование | Start | Business | Enterprise |
|-----------|-------|----------|------------|
| Таймер (start/stop) | ✅ | ✅ | ✅ |
| Ручной ввод | ✅ | ✅ | ✅ |
| Редактирование записей | ✅ | ✅ | ✅ |
| Описание к записи | ✅ | ✅ | ✅ |
| Привязка к задаче/проекту | ✅ | ✅ | ✅ |
| Напоминание о незаполненном времени | ❌ | ✅ | ✅ |
| Округление времени | ❌ | ✅ | ✅ |
| Billable/non-billable | ❌ | ✅ | ✅ |

**Правила:**
- Только один активный таймер на пользователя одновременно
- При запуске нового таймера — предыдущий автоматически останавливается
- Минимальная единица — 1 минута
- Округление: настраиваемо (1 мин, 5 мин, 15 мин, 30 мин, 1 час)
- Напоминание: ежедневно в настраиваемое время, если за день не залогировано время

### 1.2. Отчёты по времени

| Требование | Start | Business | Enterprise |
|-----------|-------|----------|------------|
| По пользователю | ✅ | ✅ | ✅ |
| По команде | ❌ | ✅ | ✅ |
| По проекту | ✅ | ✅ | ✅ |
| По задаче | ✅ | ✅ | ✅ |
| За произвольный период | ✅ | ✅ | ✅ |
| Оценка vs факт | ❌ | ✅ | ✅ |
| Группировка и фильтрация | ⚡ | ✅ | ✅ |
| Экспорт (CSV/PDF/Excel) | ❌ | ✅ | ✅ |
| Детализированный отчёт | ⚡ | ✅ | ✅ |
| Сводный отчёт | ❌ | ✅ | ✅ |

---

## 2. Доменная модель

### Value Objects

| VO | Тип | Описание |
|---|---|---|
| `TimeEntryStatus` | Enum | `RUNNING`, `STOPPED`, `DELETED` |
| `ApprovalStatus` | Enum | `PENDING`, `APPROVED`, `REJECTED` |
| `RoundingMode` | Enum | `NONE`, `UP_1`, `UP_5`, `UP_15`, `UP_30`, `UP_60` |
| `Duration` | frozen dataclass | minutes: int (≥1, ≤1440) |
| `AccentColor` | frozen dataclass | hex: str (validated `#RRGGBB`) |

### Entities

| Сущность | Поля | Описание |
|---|---|---|
| `ActivityCategory` | id, name, color: AccentColor \| None, is_system: bool, workspace_id: Id | Категория активности |
| `TimeEntryTag` | id, name, color: AccentColor \| None, workspace_id: Id | Тег записи |
| `RejectionReason` | id, reason: str, rejected_by: Id, rejected_at: datetime | Причина отклонения |

#### Предустановленные категории активности

При создании workspace создаются `ActivityCategory` с `is_system=True`:

| name | Описание |
|---|---|
| `Development` | Разработка |
| `Code Review` | Код-ревью |
| `Meeting` | Совещание |
| `Testing` | Тестирование |
| `Documentation` | Документация |
| `Other` | Другое |

> Кастомные категории = `ActivityCategory` с `is_system=False`.

### Aggregates

#### TimeEntry (Aggregate Root)

Поля:
- workspace_id: Id (opaque)
- user_id: Id
- task_id: Id | None (opaque, из Task BC)
- project_id: Id (opaque, из Project BC)
- category: ActivityCategory | None
- tags: list[TimeEntryTag]
- description: str | None (до 500 символов)
- started_at: datetime
- ended_at: datetime | None
- duration: Duration | None — computed or manual
- status: TimeEntryStatus
- is_manual: bool
- is_billable: bool
- approval_status: ApprovalStatus
- rejection: RejectionReason | None
- created_at: datetime
- updated_at: datetime

Методы:
- `start(user_id, workspace_id, project_id, task_id=None, description=None, category=None, is_billable=False)` → `TimeEntry` (factory, status=RUNNING)
- `create_manual(user_id, workspace_id, project_id, started_at, duration, task_id=None, description=None, category=None, is_billable=False)` → `TimeEntry` (factory, status=STOPPED, is_manual=True)
- `stop()` — вычисляет duration, status=STOPPED
- `update(description=None, task_id=None, project_id=None, category=None, is_billable=None, started_at=None, duration=None)`
- `soft_delete()` — status=DELETED
- `add_tag(tag)` / `remove_tag(tag_name)`
- `approve(approved_by)` — approval_status=APPROVED
- `reject(rejected_by, reason)` — approval_status=REJECTED
- `reset_approval()` — при редактировании → PENDING

Инварианты:
- Один активный таймер на пользователя (глобально)
- При старте нового — предыдущий автоматически останавливается
- Duration: 1–1440 минут
- RUNNING: ended_at=None, duration=None
- STOPPED: ended_at и duration заполнены
- Rounding применяется при отображении (не меняет raw данные)
- Task привязка: если require_task в настройках — обязательна (проверка на app-слое)
- При редактировании одобренной записи — approval сбрасывается в PENDING

#### ActivityCategory (Aggregate Root)

Поля:
- name: str
- color: AccentColor | None
- is_system: bool
- workspace_id: Id (opaque)
- created_at: datetime

Методы:
- `create(name, workspace_id, color=None)` → `ActivityCategory` (is_system=False)
- `update(name=None, color=None)` — только для не-системных
- `delete()` — только для не-системных

Инварианты:
- Системные категории нельзя редактировать/удалять
- Имя уникально в рамках workspace

---

## 3. Бизнес-правила

1. Один активный таймер на пользователя (глобально, не per workspace)
2. При старте нового таймера — предыдущий останавливается с текущим временем
3. duration_minutes: для таймера — вычисляется при остановке; для ручного — вводится
4. Минимум: 1 минута; максимум: 24 часа (1440 минут) на одну запись
5. Task привязка: если require_task=true в настройках — задача обязательна
6. Редактирование: пользователь может редактировать свои записи; Admin+ может редактировать любые
7. Удаление: soft-delete
8. Rounding: применяется при отображении в отчётах (не меняет raw данные)
9. actual_effort в задаче: автоматически обновляется при создании/изменении/удалении TimeEntry

---

## 4. API Endpoints

### 4.1. Таймер

```
POST /api/v1/workspaces/{ws_id}/time-tracking/timer/start
```

**Request:**
```json
{
  "task_id": "task_uuid",
  "project_id": "project_uuid",
  "description": "Working on auth module"
}
```

**Response (201):**
```json
{
  "id": "time_entry_uuid",
  "task_id": "task_uuid",
  "project_id": "project_uuid",
  "started_at": "2025-02-01T09:00:00Z",
  "is_running": true,
  "description": "Working on auth module"
}
```

---

```
POST /api/v1/workspaces/{ws_id}/time-tracking/timer/stop
```

**Response (200):**
```json
{
  "id": "time_entry_uuid",
  "started_at": "2025-02-01T09:00:00Z",
  "ended_at": "2025-02-01T11:30:00Z",
  "duration_minutes": 150,
  "is_running": false
}
```

---

```
GET /api/v1/workspaces/{ws_id}/time-tracking/timer/current
```
*Получить текущий активный таймер*

### 4.2. Записи времени (CRUD)

```
POST /api/v1/workspaces/{ws_id}/time-entries
```

**Request (manual):**
```json
{
  "task_id": "task_uuid",
  "project_id": "project_uuid",
  "description": "Code review",
  "started_at": "2025-02-01T14:00:00Z",
  "duration_minutes": 45,
  "is_billable": true
}
```

---

```
GET /api/v1/workspaces/{ws_id}/time-entries
```

**Query params:** `user_id`, `project_id`, `task_id`, `from`, `to`, `is_billable`, `page`, `limit`

---

```
GET /api/v1/workspaces/{ws_id}/time-entries/{entry_id}
```

---

```
PATCH /api/v1/workspaces/{ws_id}/time-entries/{entry_id}
```

---

```
DELETE /api/v1/workspaces/{ws_id}/time-entries/{entry_id}
```

### 4.3. Отчёты

```
GET /api/v1/workspaces/{ws_id}/time-tracking/reports/summary
```

**Query params:** `from`, `to`, `group_by` (user/project/task/day/week), `user_id`, `project_id`, `is_billable`

**Response (200):**
```json
{
  "period": {"from": "2025-02-01", "to": "2025-02-28"},
  "total_minutes": 9600,
  "billable_minutes": 7200,
  "entries_count": 120,
  "groups": [
    {
      "key": "project_uuid",
      "label": "Backend API",
      "total_minutes": 4800,
      "billable_minutes": 3600,
      "entries_count": 60
    }
  ]
}
```

---

```
GET /api/v1/workspaces/{ws_id}/time-tracking/reports/detailed
```

**Query params:** same as summary + `sort_by`, `order`

---

```
GET /api/v1/workspaces/{ws_id}/time-tracking/reports/estimate-vs-actual
```

**Query params:** `project_id`, `sprint_id`

**Response (200):**
```json
{
  "tasks": [
    {
      "task_id": "uuid",
      "key": "API-42",
      "title": "Implement auth",
      "estimation": 8.0,
      "actual": 10.5,
      "difference": -2.5,
      "percentage": 131
    }
  ],
  "summary": {
    "total_estimation": 40.0,
    "total_actual": 42.5,
    "accuracy_percentage": 94
  }
}
```

---

```
GET /api/v1/workspaces/{ws_id}/time-tracking/reports/export
```

**Query params:** `format` (csv/pdf/excel), `from`, `to`, `user_id`, `project_id`, `type` (summary/detailed)

**Response (200):** File download

### 4.4. Настройки

```
GET /api/v1/workspaces/{ws_id}/time-tracking/settings
```

---

```
PUT /api/v1/workspaces/{ws_id}/time-tracking/settings
```

**Request:**
```json
{
  "rounding": "up_15",
  "reminder_enabled": true,
  "reminder_time": "18:00",
  "reminder_days": [0, 1, 2, 3, 4],
  "default_billable": true,
  "require_task": true,
  "require_description": false
}
```

---

## 5. Схема БД

### Таблица: `time_entries`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| workspace_id | UUID | FK → workspaces.id, NOT NULL | |
| user_id | UUID | FK → users.id, NOT NULL | |
| task_id | UUID | FK → tasks.id, NULLABLE | |
| project_id | UUID | FK → projects.id, NOT NULL | |
| description | VARCHAR(500) | NULLABLE | |
| started_at | TIMESTAMPTZ | NOT NULL | |
| ended_at | TIMESTAMPTZ | NULLABLE | |
| duration_minutes | INTEGER | NULLABLE | |
| is_running | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| is_manual | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| is_billable | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

**Индексы:**
- `idx_te_user_running` — UNIQUE на `(user_id)` WHERE `is_running = TRUE`
- `idx_te_ws_user` — на `(workspace_id, user_id)`
- `idx_te_task` — на `task_id`
- `idx_te_project` — на `project_id`
- `idx_te_started` — на `started_at`
- `idx_te_ws_started` — на `(workspace_id, started_at)`

### Таблица: `time_tracking_settings`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| workspace_id | UUID | PK, FK → workspaces.id | |
| rounding | VARCHAR(10) | NOT NULL, DEFAULT 'none' | |
| reminder_enabled | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| reminder_time | TIME | NULLABLE | |
| reminder_days | JSONB | NOT NULL, DEFAULT '[0,1,2,3,4]' | |
| default_billable | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| require_task | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| require_description | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

---

## 6. Доменные события

| Событие | Поля | Описание |
|---|---|---|
| `TimerStarted` | entry_id, user_id, project_id, task_id \| None | Таймер запущен |
| `TimerStopped` | entry_id, duration_minutes | Таймер остановлен |
| `TimerAutoStopped` | entry_id, user_id, reason | Автоостановка (new_timer / daily_limit) |
| `TimeEntryCreated` | entry_id, user_id, project_id, duration_minutes, is_manual | Запись создана |
| `TimeEntryUpdated` | entry_id, changed_fields: list[str] | Запись обновлена |
| `TimeEntryDeleted` | entry_id | Запись удалена |
| `TimeEntryApproved` | entry_id, approved_by | Запись одобрена |
| `TimeEntryRejected` | entry_id, rejected_by, reason | Запись отклонена |
| `TimeEntryApprovalReset` | entry_id | Approval сброшен (после редактирования) |
| `TaskActualEffortUpdated` | task_id, total_minutes | Факт. трудозатраты обновлены |
| `TimeReminderSent` | user_id, workspace_id, date | Напоминание отправлено |
| `ActivityCategoryCreated` | category_id, workspace_id, name | Категория создана |
| `ActivityCategoryUpdated` | category_id, changed_fields: list[str] | Категория обновлена |
| `ActivityCategoryDeleted` | category_id | Категория удалена |

---

## 7. Exceptions

| Исключение | Описание |
|---|---|
| `TimeEntryNotFoundException` | Запись не найдена |
| `TimerAlreadyRunningException` | Таймер уже запущен |
| `TimerNotRunningException` | Нет активного таймера |
| `InvalidDurationException` | Некорректная длительность (< 1 или > 1440 мин) |
| `TimeEntryOverlapException` | Перекрытие с другой записью |
| `ActivityCategoryNotFoundException` | Категория не найдена |
| `CannotDeleteSystemCategoryException` | Нельзя удалить системную категорию |
| `DuplicateCategoryNameException` | Категория с таким именем уже существует |
| `TimeEntryAlreadyApprovedException` | Запись уже одобрена |
| `TimeEntryAlreadyRejectedException` | Запись уже отклонена |
| `CannotEditApprovedEntryException` | Нельзя редактировать одобренную запись (сначала сбросить) |

---

## 8. Repositories

| Репозиторий | Методы |
|---|---|
| `TimeEntryRepository` | `get_by_id`, `get_by_user`, `get_by_project`, `get_by_task`, `get_running_by_user`, `get_by_date_range`, `get_by_approval_status`, `sum_duration_by_task`, `sum_duration_by_project`, `sum_duration_by_user` |
| `ActivityCategoryRepository` | `get_by_id`, `get_by_workspace`, `get_system_categories`, `get_by_name` |
| `TimeEntryTagRepository` | `get_by_id`, `get_by_workspace`, `get_by_name` |
