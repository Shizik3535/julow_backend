# 18. Search & Filtering — Поиск, фильтрация, сортировка

## Обзор

Контекст поиска и фильтрации обеспечивает полнотекстовый поиск, фасетную фильтрацию, сортировку и группировку данных. Используется search engine (Elasticsearch / Meilisearch) для быстрого полнотекстового поиска.

---

## Принципы расширяемости

1. **FilterOperator — enum** — типизированные операторы: `EQ`, `NEQ`, `IN`, `NOT_IN`, `GT`, `GTE`, `LT`, `LTE`, `IS_NULL`, `IS_NOT_NULL`, `CONTAINS`, `NOT_CONTAINS`.
2. **SortDirection — enum** — `ASC`, `DESC`.
3. **SearchableEntityType — enum** — `TASK`, `PROJECT`, `COMMENT`, `FILE`.
4. **FilterConditions — VO** — типизированные условия фильтрации вместо сырых dict.
5. **SavedFilter — AR** — сохранённый фильтр с правами доступа.
6. **SearchIndex — infrastructure** — sync через доменные события.

---

## 1. Функциональные требования

### 1.1. Фильтрация

| Требование | Free | Start | Business | Enterprise |
|-----------|------|-------|----------|------------|
| По встроенным полям | ✅ | ✅ | ✅ | ✅ |
| По кастомным полям | ❌ | ✅ | ✅ | ✅ |
| Комбинация условий (AND/OR) | ⚡ AND only | ✅ | ✅ | ✅ |
| Быстрые фильтры (presets) | ✅ | ✅ | ✅ | ✅ |
| Сохранённые фильтры | ❌ | ⚡ 5 | ⚡ 25 | ∞ |

**Быстрые фильтры (presets):**
- «Мои задачи» — assignee = current_user
- «Просроченные» — due_date < today AND status ∉ final
- «Без исполнителя» — assignee IS NULL
- «Созданные мной» — reporter = current_user
- «Обновлённые сегодня» — updated_at >= today
- «Высокий приоритет» — priority IN (critical, high)

### 1.2. Сортировка

| Требование | Описание |
|-----------|----------|
| По любому полю | ✅ |
| Мультисортировка | Первичная + вторичная |
| Направление | ASC / DESC |

### 1.3. Группировка

| Группировка по | Описание |
|----------------|----------|
| Статус | Задачи группируются по workflow-статусам |
| Приоритет | Critical → None |
| Исполнитель | По assignee (+ "Без исполнителя") |
| Спринт | По sprint (+ "Backlog") |
| Тег | По тегу |
| Тип задачи | Epic / Story / Task / Bug и т.д. |
| Milestone | По milestone (+ "Без milestone") |

**Функции:**
- Сворачивание/разворачивание групп
- Подсчёт количества в группе
- Суммарная оценка в группе (если estimation field)

### 1.4. Глобальный поиск

| Требование | Free | Start | Business | Enterprise |
|-----------|------|-------|----------|------------|
| Полнотекстовый поиск | ✅ | ✅ | ✅ | ✅ |
| По задачам | ✅ | ✅ | ✅ | ✅ |
| По проектам | ✅ | ✅ | ✅ | ✅ |
| По комментариям | ❌ | ✅ | ✅ | ✅ |
| По файлам (имя) | ❌ | ✅ | ✅ | ✅ |
| По файлам (содержимое) | ❌ | ❌ | ❌ | ✅ (OCR) |
| Поиск по ID задачи | ✅ | ✅ | ✅ | ✅ |
| Фасетный поиск | ❌ | ✅ | ✅ | ✅ |
| Autocomplete | ✅ | ✅ | ✅ | ✅ |
| Недавние запросы | ✅ | ✅ | ✅ | ✅ |
| Макс. результатов | 100 | 500 | 5000 | ∞ |

---

## 2. Доменная модель

### Value Objects

| VO | Тип | Описание |
|---|---|---|
| `FilterOperator` | Enum | `EQ`, `NEQ`, `IN`, `NOT_IN`, `GT`, `GTE`, `LT`, `LTE`, `IS_NULL`, `IS_NOT_NULL`, `CONTAINS`, `NOT_CONTAINS` |
| `FilterLogic` | Enum | `AND`, `OR` |
| `SortDirection` | Enum | `ASC`, `DESC` |
| `SearchableEntityType` | Enum | `TASK`, `PROJECT`, `COMMENT`, `FILE` |
| `FilterRule` | frozen dataclass | field: str, operator: FilterOperator, value: Any |
| `FilterConditions` | frozen dataclass | logic: FilterLogic, rules: list[FilterRule] |
| `SortRule` | frozen dataclass | field: str, direction: SortDirection |

### Entities

| Сущность | Поля | Описание |
|---|---|---|
| `RecentSearch` | user_id: Id, workspace_id: Id, query: str, result_count: int, searched_at | Недавний поиск |

### Aggregates

#### SavedFilter (Aggregate Root)

Поля:
- user_id: Id
- workspace_id: Id (opaque)
- project_id: Id | None (null = cross-project)
- name: str
- conditions: FilterConditions
- sort: list[SortRule]
- group_by: str | None
- is_default: bool
- is_shared: bool
- created_at: datetime
- updated_at: datetime

Методы:
- `create(user_id, workspace_id, name, conditions, sort=[], group_by=None, project_id=None)` → `SavedFilter`
- `update(name=None, conditions=None, sort=None, group_by=None)`
- `set_default(is_default)` / `set_shared(is_shared)`
- `delete()`

Инварианты:
- Один default filter на (user, workspace, project)
- Shared filters видны всем в workspace
- Лимит saved filters по тарифу

### Search Index Schema (Elasticsearch/Meilisearch)

```json
{
  "tasks": {
    "id": "uuid",
    "key": "API-42",
    "title": "Implement auth",
    "description": "OAuth 2.0...",
    "status": "In Progress",
    "status_category": "in_progress",
    "priority": "high",
    "type": "story",
    "assignee_names": ["John Doe"],
    "assignee_ids": ["uuid"],
    "reporter_name": "Jane Smith",
    "reporter_id": "uuid",
    "tags": ["auth", "backend"],
    "project_id": "uuid",
    "project_name": "Backend API",
    "workspace_id": "uuid",
    "sprint_id": "uuid",
    "sprint_name": "Sprint 1",
    "due_date": "2025-02-14",
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-02-01T12:00:00Z"
  },
  "projects": {
    "id": "uuid",
    "name": "Backend API",
    "prefix": "API",
    "description": "...",
    "workspace_id": "uuid",
    "status": "active",
    "methodology": "scrum",
    "tags": ["backend"]
  },
  "comments": {
    "id": "uuid",
    "task_id": "uuid",
    "task_key": "API-42",
    "content": "Looks good! ...",
    "author_name": "John Doe",
    "project_id": "uuid",
    "workspace_id": "uuid",
    "created_at": "2025-02-01T12:00:00Z"
  },
  "files": {
    "id": "uuid",
    "name": "screenshot.png",
    "context_type": "task",
    "context_id": "uuid",
    "workspace_id": "uuid",
    "category": "image",
    "uploader_name": "John Doe",
    "created_at": "2025-02-01T12:00:00Z"
  }
}
```

---

## 3. Бизнес-правила

1. **Scope**: поиск ограничен текущим workspace; cross-workspace поиск не поддерживается
2. **Visibility**: результаты фильтруются по правам доступа (private projects скрыты от non-members)
3. **Index sync**: при создании/изменении/удалении задачи/проекта/комментария/файла — обновление индекса (async)
4. **Autocomplete**: top-5 предложений по мере ввода; включает задачи (по key и title) и проекты
5. **Recent searches**: последние 20 запросов на пользователя; автоматическая очистка старых
6. **Saved filters**: видны только создателю (если не shared)
7. **Filter operators**: зависят от типа поля (date → gt/lt, string → contains, enum → in/eq)
8. **Grouping**: null-значения группируются в отдельную группу ("Без исполнителя", "Backlog")
9. **Ranking**: полнотекстовый поиск — relevance scoring; title имеет вес 3x, key — exact match boost
10. **OCR (Enterprise)**: содержимое изображений индексируется через OCR (async pipeline)

---

## 4. API Endpoints

### 4.1. Глобальный поиск

```
GET /api/v1/workspaces/{ws_id}/search
```

**Query params:**
- `q` — поисковый запрос
- `types` — task,project,comment,file (comma-separated)
- `project_id` — ограничить проектом
- `page`, `limit`

**Response (200):**
```json
{
  "query": "auth",
  "total": 25,
  "results": [
    {
      "type": "task",
      "id": "uuid",
      "key": "API-42",
      "title": "Implement user <em>auth</em>entication",
      "project": {"id": "uuid", "name": "Backend API"},
      "status": "In Progress",
      "priority": "high",
      "score": 0.95
    },
    {
      "type": "comment",
      "id": "uuid",
      "task_key": "API-42",
      "excerpt": "...please review the <em>auth</em> flow...",
      "author": "John Doe",
      "score": 0.72
    }
  ],
  "facets": {
    "type": {"task": 15, "comment": 5, "project": 3, "file": 2},
    "project": {"Backend API": 20, "Frontend": 5},
    "status": {"In Progress": 10, "Done": 8, "Backlog": 7}
  }
}
```

### 4.2. Autocomplete

```
GET /api/v1/workspaces/{ws_id}/search/autocomplete
```

**Query params:** `q`, `limit` (default 5)

**Response (200):**
```json
{
  "suggestions": [
    {"type": "task", "id": "uuid", "key": "API-42", "title": "Implement auth"},
    {"type": "task", "id": "uuid", "key": "API-10", "title": "Auth middleware"},
    {"type": "project", "id": "uuid", "name": "Auth Service"}
  ]
}
```

### 4.3. Task Filtering

```
POST /api/v1/workspaces/{ws_id}/projects/{project_id}/tasks/filter
```

**Request:**
```json
{
  "conditions": {
    "logic": "and",
    "rules": [
      {"field": "priority", "operator": "in", "value": ["critical", "high"]},
      {"field": "assignee_id", "operator": "eq", "value": "current_user"},
      {"field": "due_date", "operator": "lte", "value": "2025-02-28"},
      {"field": "status_category", "operator": "neq", "value": "done"}
    ]
  },
  "sort": [
    {"field": "priority", "direction": "desc"},
    {"field": "due_date", "direction": "asc"}
  ],
  "group_by": "status",
  "page": 1,
  "limit": 50
}
```

**Response (200):**
```json
{
  "groups": [
    {
      "key": "in_progress_status_uuid",
      "label": "In Progress",
      "color": "#F39C12",
      "count": 8,
      "estimation_sum": 24,
      "items": [...]
    },
    {
      "key": "todo_status_uuid",
      "label": "To Do",
      "color": "#3498DB",
      "count": 12,
      "estimation_sum": 36,
      "items": [...]
    }
  ],
  "total": 20,
  "page": 1,
  "limit": 50
}
```

### 4.4. Saved Filters

```
GET /api/v1/workspaces/{ws_id}/saved-filters
```

**Query params:** `project_id`

---

```
POST /api/v1/workspaces/{ws_id}/saved-filters
```

**Request:**
```json
{
  "name": "My overdue tasks",
  "project_id": null,
  "conditions": {
    "logic": "and",
    "rules": [
      {"field": "assignee_id", "operator": "eq", "value": "current_user"},
      {"field": "due_date", "operator": "lt", "value": "today"},
      {"field": "status_category", "operator": "neq", "value": "done"}
    ]
  },
  "sort": [{"field": "due_date", "direction": "asc"}],
  "group_by": "project",
  "is_shared": false
}
```

---

```
PATCH /api/v1/workspaces/{ws_id}/saved-filters/{filter_id}
```

---

```
DELETE /api/v1/workspaces/{ws_id}/saved-filters/{filter_id}
```

### 4.5. Recent Searches

```
GET /api/v1/workspaces/{ws_id}/search/recent
```

**Response (200):**
```json
{
  "recent": [
    {"query": "auth", "result_count": 25, "searched_at": "2025-02-01T12:00:00Z"},
    {"query": "API-42", "result_count": 1, "searched_at": "2025-02-01T11:30:00Z"}
  ]
}
```

---

```
DELETE /api/v1/workspaces/{ws_id}/search/recent
```
*Очистить историю*

---

## 5. Схема БД

### Таблица: `saved_filters`

| Колонка | Тип | Constraints |
|---------|-----|-------------|
| id | UUID | PK |
| user_id | UUID | FK → users.id, NOT NULL |
| workspace_id | UUID | FK → workspaces.id, NOT NULL |
| project_id | UUID | FK → projects.id, NULLABLE |
| name | VARCHAR(100) | NOT NULL |
| conditions | JSONB | NOT NULL |
| sort | JSONB | NOT NULL, DEFAULT '[]' |
| group_by | VARCHAR(50) | NULLABLE |
| is_default | BOOLEAN | NOT NULL, DEFAULT FALSE |
| is_shared | BOOLEAN | NOT NULL, DEFAULT FALSE |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |

**Индексы:**
- `idx_sf_user_ws` — на `(user_id, workspace_id)`
- `idx_sf_ws_shared` — на `(workspace_id, is_shared)` WHERE `is_shared = TRUE`

### Таблица: `recent_searches`

| Колонка | Тип | Constraints |
|---------|-----|-------------|
| id | UUID | PK |
| user_id | UUID | FK → users.id, NOT NULL |
| workspace_id | UUID | FK → workspaces.id, NOT NULL |
| query | VARCHAR(200) | NOT NULL |
| result_count | INTEGER | NOT NULL, DEFAULT 0 |
| searched_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |

**Индексы:**
- `idx_rs_user_ws` — на `(user_id, workspace_id, searched_at DESC)`

---

## 6. Доменные события

| Событие | Поля | Описание |
|---|---|---|
| `SearchPerformed` | user_id, workspace_id, query, types, result_count | Поиск выполнен |
| `SavedFilterCreated` | filter_id, user_id, workspace_id, name | Фильтр создан |
| `SavedFilterUpdated` | filter_id, changed_fields: list[str] | Фильтр обновлён |
| `SavedFilterDeleted` | filter_id | Фильтр удалён |
| `SearchIndexUpdated` | entity_type, entity_id, action: index \| delete | Индекс обновлён |
| `SearchIndexRebuilt` | workspace_id, entity_type, count | Индекс перестроен |

---

## 7. Exceptions

| Исключение | Описание |
|---|---|
| `SavedFilterNotFoundException` | Фильтр не найден |
| `SavedFilterLimitExceededException` | Превышен лимит фильтров (тариф) |
| `InvalidFilterConditionException` | Некорректное условие фильтра |
| `InvalidSortFieldException` | Некорректное поле сортировки |
| `SearchIndexUnavailableException` | Search engine недоступен |

---

## 8. Repositories

| Репозиторий | Методы |
|---|---|
| `SavedFilterRepository` | `get_by_id`, `get_by_user_and_workspace`, `get_shared_by_workspace`, `get_default`, `count_by_user` |
| `RecentSearchRepository` | `get_by_user_and_workspace`, `delete_all_by_user`, `prune_old` |
