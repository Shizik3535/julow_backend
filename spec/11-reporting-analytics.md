# 11. Reporting & Analytics — Отчётность и аналитика

## Обзор

Контекст отчётности и аналитики предоставляет дашборды с виджетами, стандартные и кастомные отчёты. Данные агрегируются из контекстов Task, Project, Time Tracking и других. Отчёты можно экспортировать и отправлять по расписанию.

---

## Принципы расширяемости

1. **WidgetType — расширяемый enum** — новые виджеты = значение enum + renderer на app-слое. Analytics BC не хранит бизнес-данные, а конфигурирует их отображение.
2. **DataSource — enum** — `TASKS`, `TIME_ENTRIES`, `SPRINTS`, `PROJECTS`, `MEMBERS`. Виджет ссылается на DataSource.
3. **ReportType — расширяемый enum** — новые отчёты = значение enum + generator.
4. **ExportFormat — расширяемый enum** — `PDF`, `EXCEL`, `CSV`, `PNG`. Новые форматы = значение enum.
5. **FilterConfig — VO** — типизированные фильтры вместо `config: dict`.
6. **WidgetConfig — VO** — типизированная конфигурация виджета.
7. **DashboardTemplate — entity** — предустановленные шаблоны дашбордов.
8. **DashboardShare — entity** — шеринг дашборда с уровнями доступа.

---

## 1. Функциональные требования

### 1.1. Дашборды

| Требование | Free | Start | Business | Enterprise |
|-----------|------|-------|----------|------------|
| Количество дашбордов | ❌ | 1 | 10 | ∞ |
| Виджеты на дашборд | — | 6 | 20 | ∞ |
| Автообновление | — | ⚡ 5 мин | ✅ 1 мин | ✅ real-time |
| Shared dashboards | — | ❌ | ✅ | ✅ |
| Дашборд на уровне workspace | — | ✅ | ✅ | ✅ |
| Дашборд на уровне проекта | — | ✅ | ✅ | ✅ |

### 1.2. Виджеты

| Виджет | Тип | Start | Business | Enterprise |
|--------|-----|-------|----------|------------|
| Распределение задач по статусам | Pie chart | ✅ | ✅ | ✅ |
| Динамика создания/закрытия задач | Line chart | ✅ | ✅ | ✅ |
| Загрузка по исполнителям | Bar chart | ❌ | ✅ | ✅ |
| Просроченные задачи | Table | ✅ | ✅ | ✅ |
| Задачи без исполнителя | Table | ✅ | ✅ | ✅ |
| Среднее время выполнения | Number | ❌ | ✅ | ✅ |
| Burndown chart | Line chart | ✅ | ✅ | ✅ |
| Velocity | Bar chart | ❌ | ✅ | ✅ |
| Time spent by project | Bar chart | ❌ | ✅ | ✅ |
| Task completion rate | Number | ❌ | ✅ | ✅ |
| Sprint progress | Progress bar | ✅ | ✅ | ✅ |
| Priority distribution | Pie chart | ✅ | ✅ | ✅ |
| Recently updated tasks | List | ✅ | ✅ | ✅ |
| Upcoming deadlines | List | ✅ | ✅ | ✅ |
| Custom metric | Number | ❌ | ❌ | ✅ |

### 1.3. Отчёты

| Требование | Free | Start | Business | Enterprise |
|-----------|------|-------|----------|------------|
| Стандартные отчёты | ❌ | ⚡ 3 типа | ✅ все | ✅ все |
| По проекту | — | ✅ | ✅ | ✅ |
| По команде | — | ❌ | ✅ | ✅ |
| По периоду | — | ✅ | ✅ | ✅ |
| По трудозатратам | — | ❌ | ✅ | ✅ |
| По производительности | — | ❌ | ✅ | ✅ |
| Запланированные отчёты | — | ❌ | ✅ | ✅ |
| Экспорт (PDF/Excel/CSV/PNG) | — | ⚡ CSV | ✅ | ✅ |

---

## 2. Доменная модель

### Value Objects

| VO | Тип | Описание |
|---|---|---|
| `WidgetType` | Enum | `TASK_STATUS_DISTRIBUTION`, `TASK_CREATION_TREND`, `ASSIGNEE_WORKLOAD`, `OVERDUE_TASKS`, `UNASSIGNED_TASKS`, `AVG_COMPLETION_TIME`, `BURNDOWN`, `VELOCITY`, `TIME_BY_PROJECT`, `COMPLETION_RATE`, `SPRINT_PROGRESS`, `PRIORITY_DISTRIBUTION`, `RECENTLY_UPDATED`, `UPCOMING_DEADLINES`, `CUSTOM_METRIC` |
| `DataSource` | Enum | `TASKS`, `TIME_ENTRIES`, `SPRINTS`, `PROJECTS`, `MEMBERS` |
| `ReportType` | Enum | `PROJECT_SUMMARY`, `TEAM_PERFORMANCE`, `PERIOD_SUMMARY`, `TIME_TRACKING`, `PRODUCTIVITY`, `SPRINT_REPORT` |
| `ExportFormat` | Enum | `PDF`, `EXCEL`, `CSV`, `PNG` |
| `ReportFrequency` | Enum | `DAILY`, `WEEKLY`, `MONTHLY` |
| `ShareAccessLevel` | Enum | `VIEW`, `EDIT` |
| `FilterOperator` | Enum | `EQ`, `NEQ`, `GT`, `LT`, `GTE`, `LTE`, `IN`, `NOT_IN`, `BETWEEN`, `CONTAINS` |
| `WidgetSize` | frozen dataclass | cols: int (1–12), rows: int (1–6) |
| `WidgetPosition` | frozen dataclass | x: int (0–11), y: int |
| `FilterConfig` | frozen dataclass | field: str, operator: FilterOperator, value: str \| list[str] |
| `WidgetConfig` | frozen dataclass | data_source: DataSource, filters: list[FilterConfig], group_by: str \| None, period_days: int \| None |
| `ReportSchedule` | frozen dataclass | frequency: ReportFrequency, time: time, day_of_week: int \| None, day_of_month: int \| None, timezone: str |

> **`WidgetConfig`** — типизированная замена `config: dict`. Каждый виджет описывает DataSource и фильтры.
>
> **`FilterConfig`** — типизированный фильтр с оператором. Новые операторы = значение enum.

### Entities

| Сущность | Поля | Описание |
|---|---|---|
| `Widget` | id, widget_type: WidgetType, title, config: WidgetConfig, size: WidgetSize, position: WidgetPosition | Виджет на дашборде |
| `DashboardShare` | user_id: Id, access_level: ShareAccessLevel, shared_at | Шеринг дашборда |
| `DashboardTemplate` | name, description, widgets: list[Widget] | Шаблон дашборда |
| `ReportShare` | user_id: Id \| None, email: str \| None | Получатель отчёта |

#### Предустановленные шаблоны дашбордов

| name | Виджеты |
|---|---|
| `Project Overview` | TASK_STATUS_DISTRIBUTION, SPRINT_PROGRESS, OVERDUE_TASKS, UPCOMING_DEADLINES |
| `Team Performance` | ASSIGNEE_WORKLOAD, VELOCITY, COMPLETION_RATE, AVG_COMPLETION_TIME |
| `Sprint Dashboard` | BURNDOWN, SPRINT_PROGRESS, TASK_STATUS_DISTRIBUTION, RECENTLY_UPDATED |

### Aggregates

#### Dashboard (Aggregate Root)

Поля:
- workspace_id: Id (opaque)
- project_id: Id | None (null = workspace-level)
- name: str (до 100)
- description: str | None
- is_default: bool
- widgets: list[Widget]
- shares: list[DashboardShare]
- refresh_interval_seconds: int | None
- created_by: Id
- created_at: datetime
- updated_at: datetime

Методы:
- `create(name, workspace_id, created_by, project_id=None)` → `Dashboard`
- `create_from_template(template: DashboardTemplate, workspace_id, created_by, project_id=None)` → `Dashboard`
- `update_info(name=None, description=None, refresh_interval_seconds=None)`
- `set_default()` — снимает default с других дашбордов (app-слой)
- `add_widget(widget_type, title, config, size, position)` → `Widget`
- `update_widget(widget_id, title=None, config=None)`
- `remove_widget(widget_id)`
- `update_layout(positions: list[{widget_id, position, size}])` — batch update
- `share(user_id, access_level)` / `unshare(user_id)`
- `delete()`

Инварианты:
- Один default дашборд на workspace/проект
- Shared: видим всем участникам, edit — только создатель или Admin+
- Виджеты не перекрываются (на app-слое)
- Лимит виджетов — по тарифу

#### Report (Aggregate Root)

Поля:
- workspace_id: Id (opaque)
- name: str
- report_type: ReportType
- config: list[FilterConfig]
- format: ExportFormat
- schedule: ReportSchedule | None
- recipients: list[ReportShare]
- is_active: bool
- last_sent_at: datetime | None
- created_by: Id
- created_at: datetime
- updated_at: datetime

Методы:
- `create(name, workspace_id, report_type, config, format, created_by)` → `Report`
- `update(name=None, config=None, format=None)`
- `set_schedule(schedule: ReportSchedule)`
- `remove_schedule()`
- `add_recipient(user_id=None, email=None)` / `remove_recipient(user_id=None, email=None)`
- `activate()` / `deactivate()`
- `generate()` — запуск генерации (async job)
- `send_now()` — немедленная отправка

Инварианты:
- ReportShare — хотя бы один из user_id/email заполнен
- schedule — при activate() schedule обязателен
- Recipients — минимум 1 для scheduled

---

## 3. Бизнес-правила

1. **Default dashboard**: один дефолтный дашборд на workspace/проект; отображается при открытии
2. **Shared dashboards**: видны всем участникам workspace/проекта, редактировать может только создатель или Admin+
3. **Widget data**: данные кешируются; refresh_interval определяет частоту обновления
4. **Scheduled reports**: отправляются по email в указанном формате в указанное время
5. **Recipients**: могут быть как участники workspace (UserId), так и внешние email (для stakeholders)
6. **Report filters**: сохраняются в config; при генерации применяются к текущим данным
7. **Export**: генерируется асинхронно; пользователь получает notification со ссылкой на скачивание
8. **Data aggregation**: для производительности используются materialized views / pre-computed tables
9. **Retention**: данные для отчётов хранятся за весь период существования workspace

---

## 4. API Endpoints

### 4.1. Дашборды

```
GET /api/v1/workspaces/{ws_id}/dashboards
```

**Query params:** `project_id`, `is_shared`

---

```
POST /api/v1/workspaces/{ws_id}/dashboards
```

**Request:**
```json
{
  "name": "Sprint Overview",
  "project_id": "project_uuid",
  "is_shared": true,
  "refresh_interval_seconds": 300
}
```

---

```
GET /api/v1/workspaces/{ws_id}/dashboards/{dashboard_id}
```

**Response (200):** Dashboard + все widgets с данными

---

```
PATCH /api/v1/workspaces/{ws_id}/dashboards/{dashboard_id}
```

---

```
DELETE /api/v1/workspaces/{ws_id}/dashboards/{dashboard_id}
```

### 4.2. Виджеты

```
POST /api/v1/workspaces/{ws_id}/dashboards/{dashboard_id}/widgets
```

**Request:**
```json
{
  "type": "task_status_distribution",
  "title": "Tasks by Status",
  "config": {
    "project_id": "project_uuid",
    "sprint_id": "current"
  },
  "size": {"cols": 4, "rows": 3},
  "position": {"x": 0, "y": 0}
}
```

---

```
PATCH /api/v1/workspaces/{ws_id}/dashboards/{dashboard_id}/widgets/{widget_id}
```

---

```
DELETE /api/v1/workspaces/{ws_id}/dashboards/{dashboard_id}/widgets/{widget_id}
```

---

```
GET /api/v1/workspaces/{ws_id}/dashboards/{dashboard_id}/widgets/{widget_id}/data
```

**Response (200):** Widget-specific data

---

```
PUT /api/v1/workspaces/{ws_id}/dashboards/{dashboard_id}/layout
```
*Batch update positions/sizes*

**Request:**
```json
{
  "widgets": [
    {"widget_id": "uuid1", "position": {"x": 0, "y": 0}, "size": {"cols": 6, "rows": 3}},
    {"widget_id": "uuid2", "position": {"x": 6, "y": 0}, "size": {"cols": 6, "rows": 3}}
  ]
}
```

### 4.3. Отчёты

```
POST /api/v1/workspaces/{ws_id}/reports/generate
```

**Request:**
```json
{
  "type": "project_summary",
  "config": {
    "project_id": "project_uuid",
    "period": {"from": "2025-02-01", "to": "2025-02-28"}
  },
  "format": "pdf"
}
```

**Response (202):**
```json
{
  "report_job_id": "uuid",
  "status": "processing",
  "estimated_seconds": 15
}
```

---

```
GET /api/v1/workspaces/{ws_id}/reports/jobs/{job_id}
```

**Response (200):**
```json
{
  "id": "uuid",
  "status": "completed",
  "download_url": "https://...",
  "expires_at": "2025-02-28T12:00:00Z"
}
```

---

```
GET /api/v1/workspaces/{ws_id}/reports/download/{job_id}
```

### 4.4. Запланированные отчёты

```
GET /api/v1/workspaces/{ws_id}/reports/scheduled
```

---

```
POST /api/v1/workspaces/{ws_id}/reports/scheduled
```

**Request:**
```json
{
  "name": "Weekly Team Report",
  "report_type": "team_performance",
  "config": {
    "project_ids": ["uuid1", "uuid2"],
    "period_type": "last_7_days"
  },
  "format": "pdf",
  "schedule": {
    "frequency": "weekly",
    "time": "09:00",
    "day_of_week": 0,
    "timezone": "Europe/Moscow"
  },
  "recipient_user_ids": ["uuid1", "uuid2"],
  "recipient_emails": ["stakeholder@company.com"]
}
```

---

```
PATCH /api/v1/workspaces/{ws_id}/reports/scheduled/{report_id}
```

---

```
DELETE /api/v1/workspaces/{ws_id}/reports/scheduled/{report_id}
```

---

```
POST /api/v1/workspaces/{ws_id}/reports/scheduled/{report_id}/send-now
```
*Немедленная отправка*

---

## 5. Схема БД

### Таблица: `dashboards`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| workspace_id | UUID | FK → workspaces.id, NOT NULL | |
| project_id | UUID | FK → projects.id, NULLABLE | |
| name | VARCHAR(100) | NOT NULL | |
| description | TEXT | NULLABLE | |
| is_default | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| is_shared | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| layout | JSONB | NOT NULL, DEFAULT '{}' | |
| refresh_interval_seconds | INTEGER | NULLABLE | |
| created_by | UUID | FK → users.id, NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_dash_ws` — на `workspace_id`
- `idx_dash_project` — на `project_id`

### Таблица: `widgets`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| dashboard_id | UUID | FK → dashboards.id, NOT NULL | |
| type | VARCHAR(50) | NOT NULL | |
| title | VARCHAR(100) | NOT NULL | |
| config | JSONB | NOT NULL, DEFAULT '{}' | |
| size_cols | INTEGER | NOT NULL, DEFAULT 4 | |
| size_rows | INTEGER | NOT NULL, DEFAULT 3 | |
| position_x | INTEGER | NOT NULL, DEFAULT 0 | |
| position_y | INTEGER | NOT NULL, DEFAULT 0 | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_widget_dashboard` — на `dashboard_id`

### Таблица: `scheduled_reports`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| workspace_id | UUID | FK → workspaces.id, NOT NULL | |
| name | VARCHAR(100) | NOT NULL | |
| report_type | VARCHAR(30) | NOT NULL | |
| config | JSONB | NOT NULL | |
| format | VARCHAR(10) | NOT NULL | |
| schedule_frequency | VARCHAR(10) | NOT NULL | |
| schedule_time | TIME | NOT NULL | |
| schedule_day_of_week | INTEGER | NULLABLE | |
| schedule_day_of_month | INTEGER | NULLABLE | |
| schedule_timezone | VARCHAR(50) | NOT NULL | |
| recipients | JSONB | NOT NULL, DEFAULT '[]' | User IDs |
| recipient_emails | JSONB | NOT NULL, DEFAULT '[]' | External emails |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | |
| last_sent_at | TIMESTAMPTZ | NULLABLE | |
| created_by | UUID | FK → users.id, NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_sr_ws` — на `workspace_id`
- `idx_sr_active` — на `is_active` WHERE `is_active = TRUE`

### Таблица: `report_jobs`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| workspace_id | UUID | FK → workspaces.id, NOT NULL | |
| report_type | VARCHAR(30) | NOT NULL | |
| config | JSONB | NOT NULL | |
| format | VARCHAR(10) | NOT NULL | |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | pending/processing/completed/failed |
| result_url | VARCHAR(500) | NULLABLE | |
| result_expires_at | TIMESTAMPTZ | NULLABLE | |
| error_message | TEXT | NULLABLE | |
| requested_by | UUID | FK → users.id, NOT NULL | |
| scheduled_report_id | UUID | FK → scheduled_reports.id, NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| completed_at | TIMESTAMPTZ | NULLABLE | |

**Индексы:**
- `idx_rj_ws` — на `workspace_id`
- `idx_rj_status` — на `status`

---

## 6. Доменные события

| Событие | Поля | Описание |
|---|---|---|
| `DashboardCreated` | dashboard_id, workspace_id, project_id \| None, name | Дашборд создан |
| `DashboardUpdated` | dashboard_id, changed_fields: list[str] | Дашборд обновлён |
| `DashboardDeleted` | dashboard_id | Дашборд удалён |
| `DashboardShared` | dashboard_id, user_id, access_level | Дашборд расшарен |
| `DashboardUnshared` | dashboard_id, user_id | Шеринг снят |
| `WidgetAdded` | dashboard_id, widget_id, widget_type | Виджет добавлен |
| `WidgetUpdated` | dashboard_id, widget_id | Виджет обновлён |
| `WidgetRemoved` | dashboard_id, widget_id | Виджет удалён |
| `DashboardLayoutUpdated` | dashboard_id | Layout обновлён |
| `ReportCreated` | report_id, report_type, workspace_id | Отчёт создан |
| `ReportUpdated` | report_id, changed_fields: list[str] | Отчёт обновлён |
| `ReportDeleted` | report_id | Отчёт удалён |
| `ReportScheduleSet` | report_id, frequency | Расписание установлено |
| `ReportScheduleRemoved` | report_id | Расписание снято |
| `ReportGenerationRequested` | job_id, report_type, format | Генерация запрошена |
| `ReportGenerationCompleted` | job_id, download_url | Генерация завершена |
| `ReportGenerationFailed` | job_id, error | Генерация не удалась |
| `ScheduledReportSent` | report_id, recipient_count | Отчёт отправлен |

---

## 7. Exceptions

| Исключение | Описание |
|---|---|
| `DashboardNotFoundException` | Дашборд не найден |
| `DashboardLimitExceededException` | Превышен лимит дашбордов (тариф) |
| `WidgetNotFoundException` | Виджет не найден |
| `WidgetLimitExceededException` | Превышен лимит виджетов (тариф) |
| `ReportNotFoundException` | Отчёт не найден |
| `ReportGenerationFailedException` | Генерация отчёта не удалась |
| `InvalidFilterConfigException` | Некорректная конфигурация фильтра |
| `InvalidScheduleException` | Некорректное расписание |
| `NoRecipientsException` | Нет получателей для scheduled отчёта |

---

## 8. Repositories

| Репозиторий | Методы |
|---|---|
| `DashboardRepository` | `get_by_id`, `get_by_workspace`, `get_by_project`, `get_default`, `get_shared_with_user`, `get_by_creator` |
| `ReportRepository` | `get_by_id`, `get_by_workspace`, `get_active_scheduled`, `get_by_creator`, `get_by_type` |
