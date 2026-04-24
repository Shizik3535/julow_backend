# 06. Task — Задачи

## Обзор

Задача — центральная сущность системы. Задачи создаются внутри проекта, имеют иерархию (Epic → Story → Task → Subtask), связи между собой, чек-листы, привязку к спринтам, и полный changelog изменений.

---

## Принципы расширяемости

1. **TaskType — расширяемый enum** — новые типы задач (Test Case, Spike, Documentation) = значение enum. Иерархия через `parent_task_id`, не через тип.
2. **Кастомные поля — dict** — `custom_fields: dict[str, str]` на задаче. Определения в Project BC (`CustomFieldDefinition`), значения в Task BC.
3. **EffortUnit — enum** — вместо магической строки. `HOURS`, `STORY_POINTS`, `DAYS`, `T_SHIRT`. Новые единицы = значение enum.
4. **Гибкая иерархия** — `parent_task_id` + проверка `depth` на app-слое (лимит из Project BC). Нет захардкоженного "≤ 4 уровней".
5. **Events с `changed_fields`** — детализация изменений без взрыва количества events.
6. **Интеграция с Project BC** — `status_id`, `sprint_id`, `epic_id`, `column_id` — opaque ID, проверка валидности на app-слое. Task BC не импортирует Project BC.
7. **RecurrenceConfig** — повторяющиеся задачи. App-layer handler при завершении создаёт следующую.
8. **TaskWatcher** — подписка на изменения без назначения исполнителем.

---

## 1. Функциональные требования

### 1.1. Управление задачами

| Требование | Free | Start | Business | Enterprise |
|-----------|------|-------|----------|------------|
| Количество задач на workspace | 500 | 10 000 | 100 000 | ∞ |
| Создание задачи | ✅ | ✅ | ✅ | ✅ |
| Изменение информации | ✅ | ✅ | ✅ | ✅ |
| Удаление/архивация | ✅ | ✅ | ✅ | ✅ |
| Восстановление | ✅ | ✅ | ✅ | ✅ |
| Drag-n-drop | ✅ | ✅ | ✅ | ✅ |
| Bulk actions | ❌ | ✅ | ✅ | ✅ |
| История изменений | ⚡ 30 дней | ✅ 90 дней | ✅ 1 год | ✅ ∞ |
| Кастомные поля | ❌ | ⚡ 5 | ⚡ 50 | ∞ |

### 1.2. Поля задачи

| Поле | Тип | Обязательное | Описание |
|------|-----|-------------|----------|
| Название | str (3–500) | ✅ | |
| Описание | Rich text (MD/WYSIWYG) | ❌ | До 100 000 символов |
| Статус | WorkflowStatus ref | ✅ | Из workflow проекта |
| Приоритет | enum | ❌ | Critical, High, Medium, Low, None |
| Тип задачи | enum | ✅ | Epic, Story, Task, Subtask, Bug, Feature, Improvement |
| Исполнитель(и) | List[UserId] | ❌ | Множественные assignees |
| Дата создания | datetime | auto | |
| Дата обновления | datetime | auto | |
| Дата начала | date | ❌ | |
| Дедлайн (due date) | date | ❌ | |
| Оценка трудозатрат | decimal | ❌ | Story points / hours / days |
| Фактические трудозатраты | decimal | ❌ | Автоматически из time tracking |
| Теги/метки | List[str] | ❌ | |
| Прогресс (%) | int (0–100) | ❌ | Ручной или auto (из subtasks/checklist) |
| Спринт | SprintId | ❌ | Привязка к спринту |
| Фаза | PhaseId | ❌ | Привязка к фазе Waterfall |
| Milestone | MilestoneId | ❌ | |
| Position | int | auto | Порядок в списке/колонке |
| Номер | str | auto | PREFIX-N (e.g., "API-42") |

### 1.3. Иерархия и связи

| Требование | Free | Start | Business | Enterprise |
|-----------|------|-------|----------|------------|
| Иерархия (уровни) | 2 (Task → Subtask) | 4 (Epic → Subtask) | 4 | 4 |
| Связи между задачами | ❌ | ✅ | ✅ | ✅ |
| Dependency graph | ❌ | ❌ | ✅ | ✅ |

**Иерархия:** Epic → Story → Task → Subtask
- Epic может содержать Stories
- Story может содержать Tasks
- Task может содержать Subtasks
- Subtask не может иметь дочерних элементов
- Bug, Feature, Improvement — на уровне Task (могут иметь Subtasks)

**Типы связей:**
| Связь | Обратная связь | Описание |
|-------|---------------|----------|
| blocks | is_blocked_by | Задача блокирует другую |
| relates_to | relates_to | Связанные задачи (симметричная) |
| duplicates | is_duplicated_by | Задача дублирует другую |
| causes | is_caused_by | Задача является причиной другой |
| parent | child | Родительская/дочерняя связь (иерархия) |

### 1.4. Чек-листы

| Требование | Free | Start | Business | Enterprise |
|-----------|------|-------|----------|------------|
| Чек-листы в задаче | ✅ (1) | ✅ (5) | ✅ (20) | ✅ (∞) |
| Пункты с assignee | ❌ | ✅ | ✅ | ✅ |
| Пункты с due date | ❌ | ✅ | ✅ | ✅ |
| Прогресс чек-листа | ✅ | ✅ | ✅ | ✅ |

---

## 2. Доменная модель

### Value Objects

| VO | Тип | Описание |
|---|---|---|
| `TaskPriority` | Enum | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `NONE` |
| `TaskType` | Enum | `EPIC`, `STORY`, `TASK`, `SUBTASK`, `BUG`, `FEATURE`, `IMPROVEMENT`, `TEST_CASE`, `SPIKE`, `DOCUMENTATION` |
| `TaskStatus` | Enum | `ACTIVE`, `ARCHIVED`, `DELETED` |
| `RelationType` | Enum | `BLOCKS`, `IS_BLOCKED_BY`, `RELATES_TO`, `DUPLICATES`, `IS_DUPLICATED_BY`, `CAUSES`, `IS_CAUSED_BY`, `PARENT`, `CHILD`, `FOLLOWS`, `PRECEDES` |
| `EffortUnit` | Enum | `HOURS`, `STORY_POINTS`, `DAYS`, `T_SHIRT` |
| `TShirtSize` | Enum | `XS`, `S`, `M`, `L`, `XL` |
| `RecurrencePattern` | Enum | `DAILY`, `WEEKLY`, `BIWEEKLY`, `MONTHLY`, `QUARTERLY` |
| `TaskProgress` | frozen dataclass | value: int (0–100) |
| `EffortEstimate` | frozen dataclass | value: float, unit: EffortUnit |
| `ActualEffort` | frozen dataclass | value: float, unit: EffortUnit |
| `Label` | frozen dataclass | name: str, color: AccentColor \| None |
| `AccentColor` | frozen dataclass | hex: str (validated `#RRGGBB`) |
| `TaskOrder` | frozen dataclass | position: float, column_id: Id (opaque, из Board AR) |
| `RecurrenceConfig` | frozen dataclass | pattern: RecurrencePattern, interval: int, end_date: date \| None, max_occurrences: int \| None |
| `RichText` | frozen dataclass | content: str, format: RichTextFormat (`MARKDOWN` \| `WYSIWYG`) |

> **`TaskType`** — расширяемый. Новые типы = значение enum. Иерархия через `parent_task_id`, не тип.
>
> **`TaskStatus`** — жизненный цикл задачи в Task BC (не workflow status из Project BC).
>
> **`EffortEstimate`/`ActualEffort`** — типизированная замена `hours: float`. `EffortUnit` гарантирует совместимость.
>
> **`RelationType`** — `FOLLOWS`/`PRECEDES` для sequential задач. Новые типы связей = значение enum.

### Entities

| Сущность | Поля | Описание |
|---|---|---|
| `Checklist` | id, title, items: list[ChecklistItem] | Чек-лист внутри задачи |
| `ChecklistItem` | id, text, is_checked, assignee_id: Id \| None, due_date: date \| None, checked_at, order | Пункт чек-листа |
| `TaskRelation` | related_task_id: Id, relation_type: RelationType, created_at, created_by: Id | Связь с другой задачей |
| `TaskWatcher` | user_id: Id, watched_at: datetime | Наблюдатель задачи |
| `TaskAttachment` | file_id: Id (opaque, из FileStorage BC), filename, size_bytes, uploaded_by, uploaded_at | Вложение |
| `ChangelogEntry` | id, field_name, old_value, new_value, changed_by: Id, changed_at | Запись истории изменений |
| `TaskTemplate` | name, description: RichText \| None, task_type, default_labels: list[Label], default_checklists: list[Checklist], default_custom_fields: dict | Шаблон задачи |

> **`ChangelogEntry`** — не загружается полностью в AR Task. Доступ через `ChangelogRepository` с пагинацией.
>
> **`TaskAttachment`** — ссылка на файл в FileStorage BC. Удаление вложения не удаляет файл.
>
> **`TaskTemplate`** — предзаполняет поля при создании задачи.

#### Предустановленные шаблоны задач

| name | task_type | default_labels | default_checklists |
|---|---|---|---|
| `Bug Report` | BUG | [bug] | [Steps to Reproduce, Expected Result, Actual Result] |
| `Feature Request` | FEATURE | [feature] | [Acceptance Criteria] |
| `Spike` | SPIKE | [spike] | [Findings, Recommendation] |
| `User Story` | STORY | [story] | [Acceptance Criteria] |
| `Task` | TASK | [] | [] |

### Aggregates

#### Task (Aggregate Root)

Поля:
- project_id: Id (opaque, из Project BC)
- parent_task_id: Id | None (для иерархии)
- epic_id: Id | None (opaque, из Epic AR в Project BC)
- number: int — автоинкремент внутри проекта
- key: str — computed: `{project.prefix}-{number}` (e.g., "API-42")
- title: str (3–500)
- description: RichText | None
- status_id: Id | None (opaque, из WorkflowStatus в Board AR)
- priority: TaskPriority
- task_type: TaskType
- assignee_ids: list[Id]
- reporter_id: Id
- labels: list[Label]
- progress: TaskProgress
- effort_estimate: EffortEstimate | None
- actual_effort: ActualEffort | None
- start_date: date | None
- due_date: date | None
- completed_at: datetime | None
- custom_fields: dict[str, str] — значения (ключи из CustomFieldDefinition в Project BC)
- checklists: list[Checklist]
- relations: list[TaskRelation]
- watchers: list[TaskWatcher]
- attachments: list[TaskAttachment]
- order: TaskOrder
- sprint_id: Id | None (opaque, из Sprint AR)
- status: TaskStatus (ACTIVE / ARCHIVED / DELETED)
- recurrence: RecurrenceConfig | None
- created_at: datetime
- updated_at: datetime

Методы:
- `create(title, project_id, task_type, reporter_id, parent_task_id=None, epic_id=None)` → `Task` (factory)
- `create_from_template(template: TaskTemplate, project_id, reporter_id)` → `Task`
- `update_info(title=None, description=None, start_date=None, due_date=None)`
- `change_status(new_status_id)` — проверка перехода на app-слое через workflow
- `change_priority(priority)` / `change_type(task_type)`
- `assign(user_id)` / `unassign(user_id)`
- `update_progress(progress)` / `compute_progress_from_checklists()`
- `set_effort_estimate(estimate)` / `set_actual_effort(effort)`
- `add_label(label)` / `remove_label(label_name)`
- `move(column_id, position)` — drag-n-drop
- `archive()` / `restore()` / `soft_delete()`
- `add_relation(related_task_id, relation_type)` / `remove_relation(related_task_id, relation_type)`
- `add_checklist(title)` / `remove_checklist(checklist_id)`
- `add_checklist_item(checklist_id, text, assignee_id=None, due_date=None)`
- `toggle_checklist_item(checklist_id, item_id)`
- `assign_checklist_item(checklist_id, item_id, assignee_id)`
- `assign_to_sprint(sprint_id)` / `remove_from_sprint()`
- `assign_to_epic(epic_id)` / `remove_from_epic()`
- `add_watcher(user_id)` / `remove_watcher(user_id)`
- `add_attachment(file_id, filename, size_bytes, uploaded_by)` / `remove_attachment(file_id)`
- `set_custom_field(field_name, value)` / `remove_custom_field(field_name)`
- `set_recurrence(config)` / `remove_recurrence()`

Инварианты:
- Нельзя связать задачу саму с собой
- Нельзя дублировать связь (same related_task_id + relation_type)
- Circular dependency: проверка на app-слое (обход графа)
- Прогресс 0–100
- Статус из Project BC через opaque ID, валидация перехода на app-слое
- `effort_estimate` и `actual_effort` — совместимые `EffortUnit`
- Глубина иерархии — app-слой (лимит из Project BC), нет захардкоженного ограничения
- Ключи `custom_fields` → `CustomFieldDefinition` в Project BC (проверка на app-слое)
- Labels уникальны по имени, Watchers уникальны по user_id
- Максимум 10 assignees, 50 items на checklist

### Интеграция с Project BC

Task BC ссылается на Project BC через opaque ID. Все проверки — на app-слое.

| Поле Task | Сущность Project BC | Проверка |
|---|---|---|
| `project_id` | Project AR | Существование, статус не ARCHIVED/SUSPENDED |
| `status_id` | WorkflowStatus (Board AR) | Валидность, разрешённые переходы |
| `sprint_id` | Sprint AR | Существование, статус PLANNING/ACTIVE |
| `epic_id` | Epic AR | Существование, статус не CANCELLED |
| `order.column_id` | BoardColumn (Board AR) | Существование, WIP-лимит |
| `custom_fields` keys | CustomFieldDefinition (Project AR) | Имя поля, тип значения |
| `parent_task_id` depth | MethodologyCapabilities / WorkspaceLimits | Макс. глубина иерархии |

---

## 3. Бизнес-правила

1. **Task key**: формируется автоматически `{project.prefix}-{project.task_counter++}`, неизменяемый
2. **Статус**: при создании задачи устанавливается начальный статус workflow
3. **Переходы**: статус можно изменить только по разрешённым переходам workflow (если transitions настроены)
4. **Иерархия**:
   - Epic не может быть дочерним элементом
   - Subtask не может иметь дочерних элементов
   - Задача не может быть родителем самой себя
   - Нельзя создать циклические зависимости
   - Parent и child должны быть в одном проекте
5. **Связи**:
   - При создании `blocks` автоматически создаётся `is_blocked_by` у target
   - `relates_to` — симметричная (создаётся в обе стороны)
   - `duplicates` → `is_duplicated_by`
   - `causes` → `is_caused_by`
   - Нельзя создать связь задачи с самой собой
   - Нельзя дублировать связь
6. **Прогресс (auto_subtasks)**: `progress = completed_subtasks / total_subtasks * 100`
7. **Прогресс (auto_checklist)**: `progress = completed_items / total_items * 100` (по всем чек-листам)
8. **Sprint**: задача может быть в одном спринте; при перемещении — удаляется из текущего
9. **Bulk actions**: максимум 100 задач за раз
10. **Deletion**: soft-delete; задачи в корзине 30 дней
11. **Assignees**: максимум 10 исполнителей на задачу
12. **Checklists**: максимум 50 items на checklist
13. **Custom fields**: значения валидируются по типу поля
14. **Due date warning**: если due_date < today и задача не в финальном статусе → overdue
15. **Position**: при drag-n-drop пересчитывается для задач в той же колонке/списке

---

## 4. API Endpoints

### 4.1. CRUD задач

```
POST /api/v1/workspaces/{ws_id}/projects/{project_id}/tasks
```

**Request:**
```json
{
  "title": "Implement user authentication",
  "description": "## Requirements\n- OAuth 2.0\n- JWT tokens",
  "type": "story",
  "priority": "high",
  "assignee_ids": ["uuid1"],
  "parent_id": null,
  "sprint_id": "sprint_uuid",
  "start_date": "2025-02-01",
  "due_date": "2025-02-14",
  "estimation": 8,
  "tags": ["auth", "backend"]
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "key": "API-42",
  "number": 42,
  "title": "Implement user authentication",
  "status": {
    "id": "status_uuid",
    "name": "Backlog",
    "category": "todo",
    "color": "#95A5A6"
  },
  "priority": "high",
  "type": "story",
  "assignees": [{"id": "uuid1", "display_name": "John Doe", "avatar_url": "..."}],
  "reporter": {"id": "current_user_uuid", "display_name": "Jane Smith"},
  "sprint_id": "sprint_uuid",
  "estimation": 8,
  "progress": 0,
  "created_at": "2025-01-15T10:00:00Z"
}
```

---

```
GET /api/v1/workspaces/{ws_id}/projects/{project_id}/tasks
```

**Query params:**
- `page`, `limit`
- `status_id`, `priority`, `type`, `assignee_id`, `sprint_id`, `milestone_id`
- `parent_id` — для получения дочерних задач
- `tag`, `is_overdue`
- `search` — по title
- `sort_by` (created_at, updated_at, priority, due_date, position)
- `order` (asc, desc)
- `group_by` (status, priority, assignee, sprint, type)

---

```
GET /api/v1/workspaces/{ws_id}/projects/{project_id}/tasks/{task_id}
```

**Response (200):** полная информация включая checklists, relations, custom fields, history (last 10)

---

```
PATCH /api/v1/workspaces/{ws_id}/projects/{project_id}/tasks/{task_id}
```

**Request:**
```json
{
  "title": "Updated title",
  "priority": "critical",
  "status_id": "new_status_uuid"
}
```

---

```
POST /api/v1/workspaces/{ws_id}/projects/{project_id}/tasks/{task_id}/archive
```

---

```
POST /api/v1/workspaces/{ws_id}/projects/{project_id}/tasks/{task_id}/restore
```

---

```
DELETE /api/v1/workspaces/{ws_id}/projects/{project_id}/tasks/{task_id}
```

### 4.2. Bulk Actions

```
POST /api/v1/workspaces/{ws_id}/projects/{project_id}/tasks/bulk
```

**Request:**
```json
{
  "action": "update",
  "task_ids": ["uuid1", "uuid2", "uuid3"],
  "changes": {
    "priority": "high",
    "assignee_ids": ["uuid"],
    "sprint_id": "sprint_uuid"
  }
}
```

или

```json
{
  "action": "archive",
  "task_ids": ["uuid1", "uuid2"]
}
```

или

```json
{
  "action": "delete",
  "task_ids": ["uuid1", "uuid2"]
}
```

или

```json
{
  "action": "move",
  "task_ids": ["uuid1", "uuid2"],
  "target_project_id": "other_project_uuid"
}
```

### 4.3. Позиционирование (Drag-n-Drop)

```
PUT /api/v1/workspaces/{ws_id}/projects/{project_id}/tasks/{task_id}/position
```

**Request:**
```json
{
  "status_id": "new_status_uuid",
  "position": 3,
  "sprint_id": "sprint_uuid_or_null"
}
```

### 4.4. Связи

```
GET /api/v1/workspaces/{ws_id}/projects/{project_id}/tasks/{task_id}/relations
```

---

```
POST /api/v1/workspaces/{ws_id}/projects/{project_id}/tasks/{task_id}/relations
```

**Request:**
```json
{
  "target_task_id": "other_task_uuid",
  "type": "blocks"
}
```

---

```
DELETE /api/v1/workspaces/{ws_id}/projects/{project_id}/tasks/{task_id}/relations/{relation_id}
```

---

```
GET /api/v1/workspaces/{ws_id}/projects/{project_id}/tasks/{task_id}/dependency-graph
```

**Response (200):**
```json
{
  "nodes": [
    {"id": "uuid", "key": "API-42", "title": "...", "status": "..."},
    {"id": "uuid2", "key": "API-43", "title": "...", "status": "..."}
  ],
  "edges": [
    {"source": "uuid", "target": "uuid2", "type": "blocks"}
  ]
}
```

### 4.5. Чек-листы

```
POST /api/v1/workspaces/{ws_id}/projects/{project_id}/tasks/{task_id}/checklists
```

**Request:**
```json
{
  "name": "Acceptance Criteria",
  "items": [
    {"content": "OAuth 2.0 works", "assignee_id": null, "due_date": null},
    {"content": "JWT refresh works", "assignee_id": "uuid", "due_date": "2025-02-10"}
  ]
}
```

---

```
PATCH /api/v1/workspaces/{ws_id}/projects/{project_id}/tasks/{task_id}/checklists/{checklist_id}
```

---

```
DELETE /api/v1/workspaces/{ws_id}/projects/{project_id}/tasks/{task_id}/checklists/{checklist_id}
```

---

```
POST /api/v1/workspaces/{ws_id}/projects/{project_id}/tasks/{task_id}/checklists/{checklist_id}/items
```

**Request:**
```json
{
  "content": "New checklist item",
  "assignee_id": "uuid",
  "due_date": "2025-02-15"
}
```

---

```
PATCH /api/v1/.../checklists/{checklist_id}/items/{item_id}
```

---

```
PUT /api/v1/.../checklists/{checklist_id}/items/{item_id}/toggle
```

---

```
DELETE /api/v1/.../checklists/{checklist_id}/items/{item_id}
```

### 4.6. Кастомные поля

```
GET /api/v1/workspaces/{ws_id}/projects/{project_id}/custom-fields
```

---

```
POST /api/v1/workspaces/{ws_id}/projects/{project_id}/custom-fields
```

**Request:**
```json
{
  "name": "Story Points",
  "type": "number",
  "is_required": false,
  "default_value": "0"
}
```

или

```json
{
  "name": "Environment",
  "type": "select",
  "options": ["Development", "Staging", "Production"],
  "is_required": true
}
```

---

```
PATCH /api/v1/workspaces/{ws_id}/projects/{project_id}/custom-fields/{field_id}
```

---

```
DELETE /api/v1/workspaces/{ws_id}/projects/{project_id}/custom-fields/{field_id}
```

---

```
PUT /api/v1/workspaces/{ws_id}/projects/{project_id}/tasks/{task_id}/custom-fields/{field_id}
```

**Request:**
```json
{
  "value": "Production"
}
```

### 4.7. История

```
GET /api/v1/workspaces/{ws_id}/projects/{project_id}/tasks/{task_id}/history
```

**Query params:** `page`, `limit`, `action`, `field`, `user_id`

**Response (200):**
```json
{
  "items": [
    {
      "id": "uuid",
      "user": {"id": "uuid", "display_name": "John Doe"},
      "action": "status_changed",
      "field": "status",
      "old_value": "Backlog",
      "new_value": "In Progress",
      "created_at": "2025-01-15T12:00:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "limit": 20
}
```

### 4.8. Подзадачи

```
GET /api/v1/workspaces/{ws_id}/projects/{project_id}/tasks/{task_id}/subtasks
```

---

```
POST /api/v1/workspaces/{ws_id}/projects/{project_id}/tasks/{task_id}/subtasks
```

*Shortcut для создания subtask с parent_id = task_id*

---

## 5. Схема БД

### Таблица: `tasks`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| project_id | UUID | FK → projects.id, NOT NULL | |
| number | INTEGER | NOT NULL | Auto-increment per project |
| title | VARCHAR(500) | NOT NULL | |
| description | TEXT | NULLABLE | Rich text |
| status_id | UUID | FK → workflow_statuses.id, NOT NULL | |
| priority | VARCHAR(20) | NOT NULL, DEFAULT 'none' | |
| type | VARCHAR(20) | NOT NULL, DEFAULT 'task' | |
| reporter_id | UUID | FK → users.id, NOT NULL | |
| parent_id | UUID | FK → tasks.id, NULLABLE | |
| sprint_id | UUID | FK → sprints.id, NULLABLE | |
| phase_id | UUID | FK → waterfall_phases.id, NULLABLE | |
| milestone_id | UUID | FK → milestones.id, NULLABLE | |
| start_date | DATE | NULLABLE | |
| due_date | DATE | NULLABLE | |
| estimation | DECIMAL(10,2) | NULLABLE | |
| actual_effort | DECIMAL(10,2) | NULLABLE | |
| tags | JSONB | NOT NULL, DEFAULT '[]' | |
| progress | INTEGER | NOT NULL, DEFAULT 0 | 0–100 |
| progress_mode | VARCHAR(20) | NOT NULL, DEFAULT 'manual' | |
| position | INTEGER | NOT NULL, DEFAULT 0 | |
| is_archived | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| archived_at | TIMESTAMPTZ | NULLABLE | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

**Индексы:**
- `idx_task_project` — на `project_id`
- `idx_task_project_number` — UNIQUE на `(project_id, number)`
- `idx_task_status` — на `status_id`
- `idx_task_parent` — на `parent_id`
- `idx_task_sprint` — на `sprint_id`
- `idx_task_priority` — на `(project_id, priority)`
- `idx_task_due_date` — на `due_date`
- `idx_task_position` — на `(project_id, status_id, position)`
- `idx_task_type` — на `(project_id, type)`
- `idx_task_milestone` — на `milestone_id`
- `idx_task_tags` — GIN на `tags`
- `idx_task_deleted` — на `deleted_at` WHERE `deleted_at IS NOT NULL`

### Таблица: `task_assignees`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| task_id | UUID | FK → tasks.id, NOT NULL | |
| user_id | UUID | FK → users.id, NOT NULL | |
| assigned_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| assigned_by | UUID | FK → users.id, NOT NULL | |

**Индексы:**
- `idx_ta_task_user` — UNIQUE на `(task_id, user_id)`
- `idx_ta_user` — на `user_id`

### Таблица: `task_relations`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| source_task_id | UUID | FK → tasks.id, NOT NULL | |
| target_task_id | UUID | FK → tasks.id, NOT NULL | |
| type | VARCHAR(30) | NOT NULL | |
| created_by | UUID | FK → users.id, NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_tr_source` — на `source_task_id`
- `idx_tr_target` — на `target_task_id`
- `idx_tr_unique` — UNIQUE на `(source_task_id, target_task_id, type)`

### Таблица: `checklists`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| task_id | UUID | FK → tasks.id, NOT NULL | |
| name | VARCHAR(200) | NOT NULL | |
| position | INTEGER | NOT NULL, DEFAULT 0 | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_cl_task` — на `task_id`

### Таблица: `checklist_items`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| checklist_id | UUID | FK → checklists.id, NOT NULL | |
| content | VARCHAR(500) | NOT NULL | |
| is_completed | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| assignee_id | UUID | FK → users.id, NULLABLE | |
| due_date | DATE | NULLABLE | |
| position | INTEGER | NOT NULL, DEFAULT 0 | |
| completed_at | TIMESTAMPTZ | NULLABLE | |
| completed_by | UUID | FK → users.id, NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_ci_checklist` — на `checklist_id`

### Таблица: `task_history`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| task_id | UUID | FK → tasks.id, NOT NULL | |
| user_id | UUID | FK → users.id, NOT NULL | |
| action | VARCHAR(30) | NOT NULL | |
| field | VARCHAR(50) | NULLABLE | |
| old_value | TEXT | NULLABLE | |
| new_value | TEXT | NULLABLE | |
| metadata | JSONB | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_th_task` — на `task_id`
- `idx_th_task_created` — на `(task_id, created_at DESC)`
- `idx_th_user` — на `user_id`

### Таблица: `custom_fields`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| project_id | UUID | FK → projects.id, NOT NULL | |
| name | VARCHAR(100) | NOT NULL | |
| slug | VARCHAR(100) | NOT NULL | |
| type | VARCHAR(20) | NOT NULL | |
| options | JSONB | NULLABLE | Для select/multi_select |
| is_required | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| default_value | TEXT | NULLABLE | |
| position | INTEGER | NOT NULL, DEFAULT 0 | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_cf_project` — на `project_id`
- `idx_cf_project_slug` — UNIQUE на `(project_id, slug)`

### Таблица: `custom_field_values`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| task_id | UUID | FK → tasks.id, NOT NULL | |
| field_id | UUID | FK → custom_fields.id, NOT NULL | |
| value | TEXT | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_cfv_task_field` — UNIQUE на `(task_id, field_id)`
- `idx_cfv_field` — на `field_id`

---

## 6. Доменные события

| Событие | Поля | Описание |
|---|---|---|
| `TaskCreated` | task_id, project_id, title, task_type, parent_task_id, epic_id | Задача создана |
| `TaskInfoChanged` | task_id, changed_fields: list[str] | Информация обновлена |
| `TaskArchived` | task_id | Архивирована |
| `TaskRestored` | task_id | Восстановлена |
| `TaskDeleted` | task_id | Soft delete |
| `TaskStatusChanged` | task_id, old_status_id, new_status_id | Workflow статус изменён |
| `TaskAssigned` | task_id, assignee_id | Исполнитель назначен |
| `TaskUnassigned` | task_id, assignee_id | Исполнитель снят |
| `TaskPriorityChanged` | task_id, new_priority | Приоритет изменён |
| `TaskTypeChanged` | task_id, new_type | Тип изменён |
| `TaskMoved` | task_id, new_column_id, new_position | Drag-n-drop |
| `TaskMovedToSprint` | task_id, sprint_id | Назначена на спринт |
| `TaskRemovedFromSprint` | task_id | Убрана из спринта |
| `TaskMovedToEpic` | task_id, epic_id | Привязана к эпику |
| `TaskRemovedFromEpic` | task_id | Отвязана от эпика |
| `BulkTasksUpdated` | task_ids, changes: dict | Массовое обновление |
| `ChecklistAdded` | task_id, checklist_id | Чек-лист добавлен |
| `ChecklistRemoved` | task_id, checklist_id | Чек-лист удалён |
| `ChecklistItemAdded` | task_id, checklist_id | Пункт добавлен |
| `ChecklistItemToggled` | task_id, checklist_id, item_id | Пункт отмечен/снят |
| `ChecklistItemAssigned` | task_id, checklist_id, assignee_id | Исполнитель назначен на пункт |
| `TaskRelationAdded` | task_id, related_task_id, relation_type | Связь добавлена |
| `TaskRelationRemoved` | task_id, related_task_id, relation_type | Связь удалена |
| `TaskProgressUpdated` | task_id, new_percent | Прогресс обновлён |
| `TaskEffortUpdated` | task_id, changed_fields: list[str] | Оценка/факт усилие |
| `TaskWatcherAdded` | task_id, user_id | Наблюдатель добавлен |
| `TaskWatcherRemoved` | task_id, user_id | Наблюдатель удалён |
| `TaskAttachmentAdded` | task_id, file_id | Вложение добавлено |
| `TaskAttachmentRemoved` | task_id, file_id | Вложение удалено |
| `TaskCustomFieldChanged` | task_id, field_name, old_value, new_value | Кастомное поле изменено |
| `TaskDeadlineApproaching` | task_id, due_date | Дедлайн приближается |
| `TaskOverdue` | task_id, due_date | Просрочена |
| `RecurringTaskCreated` | source_task_id, new_task_id | Повторяющаяся задача создана |
| `TaskCommentAdded` | task_id, comment_id (opaque, из Communication BC) | Комментарий добавлен |

---

## 7. Exceptions

| Исключение | Описание |
|---|---|
| `TaskNotFoundException` | Задача не найдена |
| `TaskArchivedException` | Задача архивирована, действие невозможно |
| `CannotChangeStatusException` | Переход статуса не разрешён workflow |
| `CircularDependencyException` | Циклическая зависимость |
| `TaskHierarchyDepthExceededException` | Превышена макс. глубина иерархии |
| `InvalidTaskRelationException` | Некорректная связь |
| `CannotRelateTaskToSelfException` | Нельзя связать задачу с собой |
| `DuplicateRelationException` | Связь уже существует |
| `ChecklistNotFoundException` | Чек-лист не найден |
| `ChecklistItemNotFoundException` | Пункт не найден |
| `DuplicateWatcherException` | Наблюдатель уже подписан |
| `AttachmentNotFoundException` | Вложение не найдено |
| `EffortUnitMismatchException` | Единицы оценки и факта не совпадают |
| `InvalidEffortValueException` | Некорректное значение усилия |
| `RecurringTaskConfigurationException` | Некорректная конфигурация повторения |
| `DuplicateLabelException` | Метка уже существует на задаче |

---

## 8. Repositories

| Репозиторий | Методы |
|---|---|
| `TaskRepository` | `get_by_id`, `get_by_project`, `get_by_assignee`, `get_by_reporter`, `get_subtasks`, `get_by_sprint`, `get_by_epic`, `get_overdue_tasks`, `get_by_status`, `get_by_parent`, `get_by_labels`, `search`, `count_by_project`, `count_by_status` |
| `ChangelogRepository` | `get_by_task_id`, `get_by_task_and_field`, `get_recent_changes`, `count_by_task` |
| `TaskTemplateRepository` | `get_by_id`, `get_by_project`, `get_system_templates`, `get_by_name` |
