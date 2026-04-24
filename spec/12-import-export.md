# 12. Import / Export — Импорт и экспорт данных

## Обзор

Контекст импорта/экспорта обеспечивает миграцию данных в систему и из неё. Поддерживается импорт из CSV/Excel/JSON с маппингом полей и экспорт задач, проектов и полных бэкапов workspace.

---

## Принципы расширяемости

1. **ImportFormat — расширяемый enum** — `CSV`, `EXCEL`, `JSON`. Новые форматы = значение enum + parser.
2. **ExportFormat — расширяемый enum** — `CSV`, `EXCEL`, `JSON`, `PDF`. Новые форматы = значение enum + generator.
3. **ExportScope — enum** — `TASKS`, `PROJECT`, `WORKSPACE`, `REPORT`, `ALL_DATA` (GDPR).
4. **MappingRule — VO** — типизированное правило маппинга вместо `mapping: dict`.
5. **ImportJob/ExportJob — AR** — каждая операция = job с жизненным циклом.
6. **ColumnMapping — entity** — маппинг колонок с автоматическим предложением.

---

## 1. Функциональные требования

### 1.1. Импорт

| Требование | Free | Start | Business | Enterprise |
|-----------|------|-------|----------|------------|
| Импорт из CSV | ⚡ до 100 строк | ✅ | ✅ | ✅ |
| Импорт из Excel (.xlsx) | ❌ | ✅ | ✅ | ✅ |
| Импорт из JSON | ❌ | ✅ | ✅ | ✅ |
| Маппинг колонок | ✅ | ✅ | ✅ | ✅ |
| Preview перед импортом | ✅ | ✅ | ✅ | ✅ |
| Лог результатов | ✅ | ✅ | ✅ | ✅ |
| Макс. строк за импорт | 100 | 5 000 | 50 000 | ∞ |
| Импорт из других систем | ❌ | ❌ | 🔮 | 🔮 |

**Процесс импорта:**
1. Загрузка файла
2. Парсинг и валидация формата
3. Маппинг колонок → поля задачи (UI step)
4. Preview: показать первые 10 строк с результатом маппинга
5. Подтверждение и запуск импорта
6. Фоновая обработка (async job)
7. Лог: успешно импортированные / ошибки / пропущенные строки
8. Notification о завершении

### 1.2. Экспорт

| Требование | Free | Start | Business | Enterprise |
|-----------|------|-------|----------|------------|
| Экспорт задач (CSV) | ⚡ до 100 | ✅ | ✅ | ✅ |
| Экспорт задач (Excel) | ❌ | ✅ | ✅ | ✅ |
| Экспорт задач (JSON) | ❌ | ✅ | ✅ | ✅ |
| Экспорт задач (PDF) | ❌ | ❌ | ✅ | ✅ |
| Экспорт проекта (full) | ❌ | ❌ | ✅ | ✅ |
| Экспорт workspace (full backup) | ❌ | ❌ | ✅ | ✅ |
| Экспорт отчётов | ❌ | ⚡ CSV | ✅ | ✅ |

---

## 2. Доменная модель

### Value Objects

| VO | Тип | Описание |
|---|---|---|
| `ImportFormat` | Enum | `CSV`, `EXCEL`, `JSON` |
| `ExportFormat` | Enum | `CSV`, `EXCEL`, `JSON`, `PDF` |
| `JobStatus` | Enum | `UPLOADING`, `MAPPING`, `PREVIEWING`, `CONFIRMED`, `PROCESSING`, `COMPLETED`, `FAILED`, `CANCELLED` |
| `ExportScope` | Enum | `TASKS`, `PROJECT`, `WORKSPACE`, `REPORT`, `ALL_DATA` |
| `MappingRule` | frozen dataclass | source_column: str, target_field: str, transform: str \| None |

> **`JobStatus`** — общий жизненный цикл для Import и Export jobs. `MAPPING` / `PREVIEWING` / `CONFIRMED` — только для Import.
>
> **`MappingRule.transform`** — опциональная трансформация (e.g., `date_format:DD/MM/YYYY`, `status_map:{...}`).

### Entities

| Сущность | Поля | Описание |
|---|---|---|
| `ColumnMapping` | source_columns: list[str], rules: list[MappingRule], status_mapping: dict[str, Id] \| None, auto_suggested: bool | Маппинг колонок |
| `ImportResult` | total_rows, processed_rows, success_count, error_count, skipped_count, error_log: list[ImportError] | Результат импорта |
| `ImportError` | row: int, field: str, error: str | Ошибка строки |
| `ExportConfig` | scope: ExportScope, project_id: Id \| None, filters: dict, fields: list[str] \| None | Конфигурация экспорта |

### Aggregates

#### ImportJob (Aggregate Root)

Поля:
- workspace_id: Id (opaque)
- project_id: Id (opaque)
- user_id: Id
- source_format: ImportFormat
- source_file_id: Id (opaque, из FileStorage BC)
- mapping: ColumnMapping | None
- status: JobStatus
- result: ImportResult | None
- started_at: datetime | None
- completed_at: datetime | None
- created_at: datetime

Методы:
- `create(workspace_id, project_id, user_id, source_format, source_file_id, total_rows)` → `ImportJob` (factory, status=UPLOADING)
- `set_mapping(mapping: ColumnMapping)` → status=MAPPING
- `preview()` → status=PREVIEWING
- `confirm()` → status=CONFIRMED
- `start_processing()` → status=PROCESSING
- `complete(result: ImportResult)` → status=COMPLETED
- `fail(error_message)` → status=FAILED
- `cancel()` → status=CANCELLED
- `update_progress(processed_rows)`

Инварианты:
- Один импорт одновременно на workspace
- Маппинг обязателен до confirm
- Отмена возможна до PROCESSING
- Status transitions: UPLOADING → MAPPING → PREVIEWING → CONFIRMED → PROCESSING → COMPLETED/FAILED

#### ExportJob (Aggregate Root)

Поля:
- workspace_id: Id (opaque)
- user_id: Id
- export_config: ExportConfig
- format: ExportFormat
- status: JobStatus
- result_file_id: Id | None
- result_url: str | None
- result_expires_at: datetime | None
- error_message: str | None
- started_at: datetime | None
- completed_at: datetime | None
- created_at: datetime

Методы:
- `create(workspace_id, user_id, config, format)` → `ExportJob` (factory, status=PROCESSING)
- `complete(result_file_id, result_url, expires_at)` → status=COMPLETED
- `fail(error_message)` → status=FAILED

Инварианты:
- Ссылка на скачивание действительна 24 часа
- ALL_DATA — GDPR export, доступен только владельцу аккаунта

---

## 3. Бизнес-правила

### Импорт
1. Файл загружается и сохраняется перед обработкой
2. Маппинг: пользователь сопоставляет колонки файла с полями задачи
3. Обязательные поля: title; остальные опциональны
4. Автоматический маппинг: система пытается сопоставить по названию колонки
5. Preview: первые 10 строк после маппинга (dry-run)
6. При ошибке в строке: строка пропускается, добавляется в error_log
7. Дублирование: не проверяется (каждая строка создаёт новую задачу)
8. Status mapping: если в файле есть статусы — сопоставление с workflow проекта
9. Assignee mapping: по email или display_name → participant workspace
10. Rate limit: 1 импорт одновременно на workspace

### Экспорт
11. Экспорт задач: применяются текущие фильтры пользователя
12. Full project export: включает задачи, комментарии, вложения (ссылки), workflow, sprints
13. Workspace backup: JSON формат, все проекты и данные
14. GDPR all_data: все данные пользователя (для запроса на экспорт по GDPR)
15. Ссылка на скачивание: действительна 24 часа
16. Большие экспорты (>10 000 записей): async job с notification

---

## 4. API Endpoints

### 4.1. Импорт

```
POST /api/v1/workspaces/{ws_id}/projects/{project_id}/import/upload
```

**Request (multipart/form-data):**
- `file` — CSV/Excel/JSON файл
- `format` — csv / excel / json

**Response (201):**
```json
{
  "import_job_id": "uuid",
  "status": "mapping",
  "detected_columns": ["Title", "Description", "Priority", "Due Date", "Assignee"],
  "total_rows": 150,
  "suggested_mapping": {
    "Title": "title",
    "Description": "description",
    "Priority": "priority",
    "Due Date": "due_date",
    "Assignee": "assignee_email"
  }
}
```

---

```
PUT /api/v1/workspaces/{ws_id}/import/{job_id}/mapping
```

**Request:**
```json
{
  "mapping": {
    "Title": "title",
    "Description": "description",
    "Priority": "priority",
    "Due Date": "due_date",
    "Assignee": "assignee_email",
    "Status": "status",
    "Tags": "tags"
  },
  "status_mapping": {
    "Open": "backlog_status_uuid",
    "In Progress": "in_progress_status_uuid",
    "Done": "done_status_uuid"
  }
}
```

---

```
GET /api/v1/workspaces/{ws_id}/import/{job_id}/preview
```

**Response (200):**
```json
{
  "rows": [
    {
      "row_number": 1,
      "data": {"title": "Task 1", "priority": "high", "due_date": "2025-03-01"},
      "valid": true,
      "errors": []
    },
    {
      "row_number": 2,
      "data": {"title": "", "priority": "medium"},
      "valid": false,
      "errors": [{"field": "title", "error": "Title is required"}]
    }
  ],
  "total_rows": 150,
  "valid_rows": 148,
  "invalid_rows": 2
}
```

---

```
POST /api/v1/workspaces/{ws_id}/import/{job_id}/confirm
```

**Response (202):**
```json
{
  "import_job_id": "uuid",
  "status": "processing",
  "total_rows": 150
}
```

---

```
GET /api/v1/workspaces/{ws_id}/import/{job_id}/status
```

**Response (200):**
```json
{
  "id": "uuid",
  "status": "completed",
  "total_rows": 150,
  "processed_rows": 150,
  "success_count": 148,
  "error_count": 2,
  "skipped_count": 0,
  "errors": [
    {"row": 2, "field": "title", "error": "Title is required"},
    {"row": 45, "field": "assignee_email", "error": "User not found: unknown@example.com"}
  ],
  "started_at": "2025-02-01T10:00:00Z",
  "completed_at": "2025-02-01T10:00:15Z"
}
```

---

```
POST /api/v1/workspaces/{ws_id}/import/{job_id}/cancel
```

### 4.2. Экспорт

```
POST /api/v1/workspaces/{ws_id}/export
```

**Request:**
```json
{
  "type": "tasks",
  "format": "excel",
  "config": {
    "project_id": "project_uuid",
    "filters": {
      "status_id": ["uuid1", "uuid2"],
      "assignee_id": "uuid"
    },
    "fields": ["key", "title", "status", "priority", "assignee", "due_date", "tags"]
  }
}
```

**Response (202):**
```json
{
  "export_job_id": "uuid",
  "status": "processing"
}
```

---

```
POST /api/v1/workspaces/{ws_id}/export/project/{project_id}
```
*Full project export*

---

```
POST /api/v1/workspaces/{ws_id}/export/workspace
```
*Full workspace backup*

---

```
GET /api/v1/workspaces/{ws_id}/export/{job_id}/status
```

---

```
GET /api/v1/workspaces/{ws_id}/export/{job_id}/download
```

**Response (302):** Redirect to download URL

---

```
GET /api/v1/workspaces/{ws_id}/import-export/history
```

**Query params:** `type` (import/export), `page`, `limit`

---

## 5. Схема БД

### Таблица: `import_jobs`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| workspace_id | UUID | FK → workspaces.id, NOT NULL | |
| project_id | UUID | FK → projects.id, NOT NULL | |
| user_id | UUID | FK → users.id, NOT NULL | |
| source_format | VARCHAR(10) | NOT NULL | |
| source_file_id | UUID | FK → files.id, NOT NULL | |
| mapping | JSONB | NULLABLE | |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'uploading' | |
| total_rows | INTEGER | NOT NULL, DEFAULT 0 | |
| processed_rows | INTEGER | NOT NULL, DEFAULT 0 | |
| success_count | INTEGER | NOT NULL, DEFAULT 0 | |
| error_count | INTEGER | NOT NULL, DEFAULT 0 | |
| skipped_count | INTEGER | NOT NULL, DEFAULT 0 | |
| error_log | JSONB | NOT NULL, DEFAULT '[]' | |
| started_at | TIMESTAMPTZ | NULLABLE | |
| completed_at | TIMESTAMPTZ | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_ij_ws` — на `workspace_id`
- `idx_ij_user` — на `user_id`
- `idx_ij_status` — на `status`

### Таблица: `export_jobs`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| workspace_id | UUID | FK → workspaces.id, NOT NULL | |
| user_id | UUID | FK → users.id, NOT NULL | |
| type | VARCHAR(20) | NOT NULL | |
| format | VARCHAR(10) | NOT NULL | |
| config | JSONB | NOT NULL, DEFAULT '{}' | |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | |
| result_file_id | UUID | FK → files.id, NULLABLE | |
| result_url | VARCHAR(500) | NULLABLE | |
| result_expires_at | TIMESTAMPTZ | NULLABLE | |
| error_message | TEXT | NULLABLE | |
| started_at | TIMESTAMPTZ | NULLABLE | |
| completed_at | TIMESTAMPTZ | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_ej_ws` — на `workspace_id`
- `idx_ej_user` — на `user_id`
- `idx_ej_status` — на `status`

---

## 6. Доменные события

| Событие | Поля | Описание |
|---|---|---|
| `ImportJobCreated` | job_id, workspace_id, project_id, format, total_rows | Импорт создан |
| `ImportMappingSet` | job_id | Маппинг установлен |
| `ImportPreviewGenerated` | job_id, valid_rows, invalid_rows | Preview готов |
| `ImportConfirmed` | job_id | Импорт подтверждён |
| `ImportProcessing` | job_id, processed_rows, total_rows | Прогресс |
| `ImportCompleted` | job_id, success_count, error_count, skipped_count | Импорт завершён |
| `ImportFailed` | job_id, error | Импорт не удался |
| `ImportCancelled` | job_id | Импорт отменён |
| `ExportJobCreated` | job_id, workspace_id, scope, format | Экспорт создан |
| `ExportCompleted` | job_id, download_url, file_size | Экспорт завершён |
| `ExportFailed` | job_id, error | Экспорт не удался |

---

## 7. Exceptions

| Исключение | Описание |
|---|---|
| `ImportJobNotFoundException` | Job не найден |
| `ImportAlreadyRunningException` | Импорт уже выполняется в workspace |
| `InvalidMappingException` | Некорректный маппинг |
| `ImportFileParseException` | Ошибка парсинга файла |
| `ImportRowLimitExceededException` | Превышен лимит строк (тариф) |
| `ImportCancelledException` | Импорт отменён |
| `ExportJobNotFoundException` | Job не найден |
| `ExportFailedException` | Экспорт не удался |
| `ExportLinkExpiredException` | Ссылка на скачивание истекла |
| `UnsupportedFormatException` | Формат не поддерживается |

---

## 8. Repositories

| Репозиторий | Методы |
|---|---|
| `ImportJobRepository` | `get_by_id`, `get_by_workspace`, `get_running_by_workspace`, `get_by_user`, `get_by_status` |
| `ExportJobRepository` | `get_by_id`, `get_by_workspace`, `get_by_user`, `get_by_status`, `get_expired` |
