# ImportExport BC — Спецификация

> Путь: `app/context/importexport/domain`
> Исходные требования: §12 (Импорт / Экспорт)

## Контекст

ImportExport BC отвечает за импорт данных (CSV, Excel, JSON с маппингом колонок) и экспорт (задач, проектов, отчётов, workspace). Каждый импорт/экспорт — это job с жизненным циклом.

---

## Value Objects

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `ImportFormat` | Enum | `CSV`, `EXCEL`, `JSON` | §12.1 |
| `ExportFormat` | Enum | `CSV`, `EXCEL`, `JSON`, `PDF` | §12.2 |
| `JobStatus` | Enum | `PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`, `CANCELLED` | — |
| `MappingRule` | frozen dataclass | source_column: str, target_field: str | §12.1 |
| `ExportScope` | Enum | `TASKS`, `PROJECT`, `WORKSPACE`, `REPORT` | §12.2 |

## Entities

| Сущность | Поля | Описание | Исходное требование |
|---|---|---|---|
| `ColumnMapping` | source_column: str, target_field: str, transform: str \| None | Маппинг колонок при импорте | §12.1 |
| `ImportResult` | success_count: int, error_count: int, errors: list[str] | Результат импорта | §12.1 |
| `ExportConfig` | scope: ExportScope, filters: dict, include_attachments: bool | Конфигурация экспорта | §12.2 |

## Domain Events

| Событие | Поля | Описание | Исходное требование |
|---|---|---|---|
| `ImportStarted` | job_id | Импорт начат | §12.1 |
| `ImportCompleted` | job_id, success_count, error_count | Импорт завершён | §12.1 |
| `ImportFailed` | job_id, error | Импорт не удался | §12.1 |
| `ImportCancelled` | job_id | Импорт отменён | §12.1 |
| `ExportStarted` | job_id | Экспорт начат | §12.2 |
| `ExportCompleted` | job_id, result_file_id | Экспорт завершён | §12.2 |
| `ExportFailed` | job_id, error | Экспорт не удался | §12.2 |
| `ExportCancelled` | job_id | Экспорт отменён | §12.2 |

## Exceptions

| Исключение | Описание |
|---|---|
| `ImportJobNotFoundException` | Job импорта не найден |
| `ExportJobNotFoundException` | Job экспорта не найден |
| `InvalidFileFormatException` | Некорректный формат файла |
| `MappingNotFoundException` | Маппинг не найден |
| `ImportInProgressException` | Импорт уже выполняется |
| `ExportInProgressException` | Экспорт уже выполняется |

## Aggregates

### ImportJob (Aggregate Root)

Поля:
- workspace_id: Id (opaque, из Workspace BC)
- initiator_id: Id
- format: ImportFormat
- status: JobStatus
- column_mappings: list[ColumnMapping]
- result: ImportResult | None
- file_id: Id | None (opaque, из FileStorage BC)
- target_type: str (task, project, etc.)
- created_at, updated_at

Методы:
- `create(workspace_id, initiator_id, format, target_type, column_mappings)` → `ImportJob` (factory)
- `start()`
- `complete(result)`
- `fail(error)`
- `cancel()`

Инварианты:
- Статус: PENDING → PROCESSING → COMPLETED/FAILED/CANCELLED
- Нельзя завершить/провалить job, который не в PROCESSING

### ExportJob (Aggregate Root)

Поля:
- workspace_id: Id (opaque)
- initiator_id: Id
- format: ExportFormat
- scope: ExportScope
- status: JobStatus
- config: ExportConfig | None
- result_file_id: Id | None (opaque, из FileStorage BC)
- created_at, updated_at

Методы:
- `create(workspace_id, initiator_id, format, scope, config)` → `ExportJob` (factory)
- `start()`
- `complete(result_file_id)`
- `fail(error)`
- `cancel()`

Инварианты:
- Статус: PENDING → PROCESSING → COMPLETED/FAILED/CANCELLED
- result_file_id заполняется только при COMPLETED

## Repositories

| Репозиторий | Методы |
|---|---|
| `ImportJobRepository` | `get_by_id`, `get_by_workspace`, `get_active_by_workspace` |
| `ExportJobRepository` | `get_by_id`, `get_by_workspace`, `get_active_by_workspace` |
