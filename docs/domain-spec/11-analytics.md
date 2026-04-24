# Analytics BC — Спецификация

> Путь: `app/context/analytics/domain`
> Исходные требования: §11 (Отчётность и аналитика)

## Контекст

Analytics BC отвечает за дашборды, виджеты, отчёты, их планирование и шаринг. Данные для виджетов и отчётов формируются на infrastructure слое (запросы к другим BC через ACL). Analytics BC не хранит бизнес-данные — только конфигурацию отображения. Сюда перенесены `TimeReportPeriod` и `TimeReportGrouping` из TimeTracking BC.

---

## Принципы расширяемости

1. **WidgetType — расширяемый enum** — новые типы виджетов (BURNDOWN, HEATMAP, GAUGE и т.д.) = значение enum.
2. **DataSource — enum** — вместо магической строки `data_source: str`. Новые источники данных = значение enum.
3. **FilterOperator — enum** — вместо магической строки `operator: str`. Новые операторы = значение enum.
4. **ReportSchedule.frequency — enum** — вместо магической строки. Новые частоты = значение enum.
5. **ReportType — расширяемый enum** — новые типы отчётов = значение enum.
6. **Шаринг — entity** — `DashboardShare`/`ReportShare` для совместного доступа. Новые уровни доступа = расширение.
7. **Шаблоны — entity** — `DashboardTemplate` для предустановленных дашбордов. Новые шаблоны = запись.
8. **TimeReportPeriod/Grouping — здесь** — перенесены из TimeTracking BC, т.к. это аналитические концепты.

---

## Value Objects

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `WidgetType` | Enum | `PIE_CHART`, `LINE_CHART`, `BAR_CHART`, `NUMBER`, `TABLE`, `LIST`, `BURNDOWN_CHART`, `CUMULATIVE_FLOW`, `HEATMAP`, `GAUGE`, `KANBAN_BOARD`, `SCATTER_PLOT`, `HISTOGRAM` | §11.1 |
| `DataSource` | Enum | `TASK_SUMMARY`, `TASK_STATUS`, `TASK_PRIORITY`, `TIME_ENTRY`, `TIME_BY_USER`, `TIME_BY_PROJECT`, `SPRINT_VELOCITY`, `SPRINT_BURNDOWN`, `PROJECT_PROGRESS`, `WORKLOAD`, `BILLING`, `FILE_STORAGE`, `CUSTOM` | §11.1 |
| `ReportType` | Enum | `BY_PROJECT`, `BY_TEAM`, `BY_PERIOD`, `BY_EFFORT`, `BY_PERFORMANCE`, `BURNDOWN`, `VELOCITY`, `CUMULATIVE_FLOW`, `TIME_TRACKING`, `BILLING_SUMMARY`, `WORKLOAD`, `CUSTOM` | §11.3 |
| `ExportFormat` | Enum | `PDF`, `EXCEL`, `CSV`, `PNG`, `JSON`, `HTML` | §11.3 |
| `FilterOperator` | Enum | `EQ`, `NEQ`, `GT`, `GTE`, `LT`, `LTE`, `IN`, `NOT_IN`, `CONTAINS`, `STARTS_WITH`, `IS_NULL`, `IS_NOT_NULL`, `BETWEEN` | — |
| `FilterConfig` | frozen dataclass | field: str, operator: FilterOperator, value: str, value_to: str \| None (для BETWEEN) | — |
| `WidgetConfig` | frozen dataclass | widget_type: WidgetType, data_source: DataSource, filters: list[FilterConfig], parameters: dict[str, str] \| None | §11.1 |
| `WidgetSize` | frozen dataclass | cols: int (1–12), rows: int (1–12) | §11.1 |
| `ReportFrequency` | Enum | `DAILY`, `WEEKLY`, `BIWEEKLY`, `MONTHLY`, `QUARTERLY` | §11.3 |
| `TimeReportPeriod` | Enum | `DAY`, `WEEK`, `MONTH`, `QUARTER`, `YEAR`, `CUSTOM` | §9.2 |
| `TimeReportGrouping` | Enum | `BY_USER`, `BY_TEAM`, `BY_PROJECT`, `BY_TASK`, `BY_CLIENT`, `BY_CATEGORY`, `BY_EPIC`, `BY_TAG` | §9.2 |
| `ShareAccessLevel` | Enum | `VIEW`, `EDIT`, `ADMIN` | §11.1 |

> **`WidgetType`** — `BURNDOWN_CHART` — sprint burndown, `CUMULATIVE_FLOW` — CFD, `HEATMAP` — heatmap активности, `GAUGE` — KPI gauge, `KANBAN_BOARD` — mini kanban, `SCATTER_PLOT` — scatter plot, `HISTOGRAM` — distribution. Новые типы виджетов = значение enum.
>
> **`DataSource`** — определяет, откуда виджет/отчёт берёт данные. Каждый источник соответствует запросу на infrastructure слое. `CUSTOM` — произвольный запрос (для продвинутых пользователей). Новые источники = значение enum.
>
> **`ReportType`** — `BURNDOWN` — sprint burndown report, `VELOCITY` — velocity report, `CUMULATIVE_FLOW` — CFD report, `TIME_TRACKING` — time tracking report (перенесено из TimeTracking BC), `BILLING_SUMMARY` — billing report, `WORKLOAD` — workload distribution, `CUSTOM` — произвольный отчёт. Новые типы = значение enum.
>
> **`FilterOperator`** — типизированная замена `operator: str`. Новые операторы = значение enum. `BETWEEN` — использует `value` и `value_to`.
>
> **`WidgetSize`** — валидированный размер виджета на grid (1–12 колонок/строк). Grid = 12 колонок.
>
> **`ReportFrequency`** — enum вместо `frequency: str`. Новые частоты = значение enum.
>
> **`TimeReportPeriod`/`TimeReportGrouping`** — перенесены из TimeTracking BC. Это аналитические концепты, не домен TimeTracking. `BY_CATEGORY` — группировка по ActivityCategory, `BY_EPIC` — по эпикам, `BY_TAG` — по тегам.
>
> **`ShareAccessLevel`** — уровень доступа при шаринге дашборда/отчёта. `VIEW` — только просмотр, `EDIT` — может изменять фильтры/параметры, `ADMIN` — может изменять структуру.

## Entities

| Сущность | Поля | Описание | Исходное требование |
|---|---|---|---|
| `Widget` | id: Id, title: str, widget_type: WidgetType, config: WidgetConfig \| None, order: int, size: WidgetSize, position: WidgetPosition \| None | Виджет дашборда | §11.1 |
| `WidgetPosition` | row: int, col: int | Позиция виджета на grid | §11.1 |
| `ReportSchedule` | frequency: ReportFrequency, recipients: list[Id], is_active: bool, next_run_at: datetime \| None, last_run_at: datetime \| None | Расписание отчёта | §11.3 |
| `DashboardShare` | user_id: Id, access_level: ShareAccessLevel, shared_at: datetime | Шаринг дашборда с пользователем | §11.1 |
| `ReportShare` | user_id: Id, access_level: ShareAccessLevel, shared_at: datetime | Шаринг отчёта с пользователем | §11.3 |
| `DashboardTemplate` | id: Id, name: str, description: str \| None, widget_configs: list[WidgetConfig], is_system: bool | Шаблон дашборда | §11.1 |

> **`Widget`** — добавлены `id` для уникальной идентификации, `size: WidgetSize` вместо `size_cols`/`size_rows`, `position: WidgetPosition` для явного позиционирования на grid.
>
> **`WidgetPosition`** — позиция (row, col) на 12-колоночном grid. Позволяет гибко размещать виджеты.
>
> **`ReportSchedule`** — `frequency: ReportFrequency` enum вместо строки. `recipients: list[Id]` вместо `list[str]` — типобезопасные ссылки на пользователей. `next_run_at`/`last_run_at` — для планировщика.
>
> **`DashboardShare`/`ReportShare`** — шаринг дашборда/отчёта с другими пользователями. `ShareAccessLevel` определяет уровень доступа. Новые уровни = значение enum.
>
> **`DashboardTemplate`** — шаблон для быстрого создания дашборда. `is_system=True` — предустановленные шаблоны. Новые шаблоны = запись, не правка домена.

### Предустановленные шаблоны дашбордов

| name | Описание | widget_configs |
|---|---|---|
| `Project Overview` | Обзор проекта | [TASK_SUMMARY (NUMBER), TASK_STATUS (PIE_CHART), SPRINT_BURNDOWN (LINE_CHART), PROJECT_PROGRESS (GAUGE)] |
| `Sprint Dashboard` | Спринт дашборд | [SPRINT_BURNDOWN (LINE_CHART), TASK_STATUS (BAR_CHART), SPRINT_VELOCITY (NUMBER), WORKLOAD (HEATMAP)] |
| `Time Tracking` | Учёт времени | [TIME_BY_USER (BAR_CHART), TIME_BY_PROJECT (PIE_CHART), TIME_ENTRY (TABLE)] |
| `Team Workload` | Нагрузка команды | [WORKLOAD (HEATMAP), TASK_PRIORITY (BAR_CHART), TASK_SUMMARY (NUMBER)] |

> Новые шаблоны = запись `DashboardTemplate` с `is_system=False`.

## Domain Events

| Событие | Поля | Описание | Исходное требование |
|---|---|---|---|
| `DashboardCreated` | dashboard_id, owner_id, workspace_id \| None | Дашборд создан | §11.1 |
| `DashboardCreatedFromTemplate` | dashboard_id, template_id | Дашборд создан из шаблона | §11.1 |
| `DashboardUpdated` | dashboard_id, changed_fields: list[str] | Дашборд обновлён | §11.1 |
| `DashboardDeleted` | dashboard_id | Дашборд удалён | §11.1 |
| `DashboardShared` | dashboard_id, user_id, access_level | Дашборд расшарен | §11.1 |
| `DashboardUnshared` | dashboard_id, user_id | Доступ к дашборду закрыт | §11.1 |
| `WidgetAdded` | dashboard_id, widget_id, widget_type | Виджет добавлен | §11.1 |
| `WidgetUpdated` | dashboard_id, widget_id | Виджет обновлён | §11.1 |
| `WidgetRemoved` | dashboard_id, widget_id | Виджет удалён | §11.1 |
| `WidgetReordered` | dashboard_id | Порядок виджетов изменён | §11.1 |
| `ReportCreated` | report_id, report_type | Отчёт создан | §11.3 |
| `ReportUpdated` | report_id, changed_fields: list[str] | Отчёт обновлён | §11.3 |
| `ReportGenerated` | report_id, generated_by | Отчёт сгенерирован | §11.3 |
| `ReportScheduled` | report_id, frequency | Отчёт запланирован | §11.3 |
| `ReportScheduleDeactivated` | report_id | Расписание отчёта деактивировано | §11.3 |
| `ReportExported` | report_id, format: ExportFormat | Отчёт экспортирован | §11.3 |
| `ReportShared` | report_id, user_id, access_level | Отчёт расшарен | §11.3 |
| `ReportUnshared` | report_id, user_id | Доступ к отчёту закрыт | §11.3 |
| `ReportDeleted` | report_id | Отчёт удалён | §11.3 |

> **`DashboardCreatedFromTemplate`** — отдельный event для отслеживания использования шаблонов.
>
> **`DashboardShared`/`ReportShared`** — шаринг с указанием уровня доступа. Позволяет уведомлять пользователя о новом доступе.
>
> **`WidgetReordered`** — отдельный event при изменении порядка виджетов (drag-and-drop).
>
> **`ReportScheduleDeactivated`** — деактивация расписания без удаления отчёта.

## Exceptions

| Исключение | Описание |
|---|---|
| `DashboardNotFoundException` | Дашборд не найден |
| `WidgetNotFoundException` | Виджет не найден |
| `ReportNotFoundException` | Отчёт не найден |
| `InvalidDataSourceException` | Некорректный источник данных (DataSource) |
| `InvalidFilterOperatorException` | Некорректный оператор фильтра |
| `InvalidWidgetSizeException` | Некорректный размер виджета (cols/rows вне 1–12) |
| `ReportScheduleNotFoundException` | Расписание не найдено |
| `DashboardShareNotFoundException` | Шаринг не найден |
| `ReportShareNotFoundException` | Шаринг отчёта не найден |
| `DuplicateShareException` | Шаринг уже существует для этого пользователя |
| `CannotShareWithSelfException` | Нельзя расшарить с самим собой |
| `DashboardTemplateNotFoundException` | Шаблон не найден |
| `CannotDeleteSystemTemplateException` | Нельзя удалить системный шаблон |
| `ReportExportFormatException` | Некорректный формат экспорта |
| `InvalidReportFrequencyException` | Некорректная частота расписания |

## Aggregates

### Dashboard (Aggregate Root)

Поля:
- owner_id: Id
- workspace_id: Id | None (opaque, из Workspace BC)
- name: str
- description: str | None
- widgets: list[Widget]
- shares: list[DashboardShare]
- is_auto_refresh: bool
- refresh_interval_seconds: int | None
- is_default: bool — дашборд по умолчанию для workspace
- created_at: datetime
- updated_at: datetime

Методы:
- `create(name, owner_id, workspace_id=None)` → `Dashboard` (factory)
- `create_from_template(template: DashboardTemplate, owner_id, workspace_id=None)` → `Dashboard` (factory, заполняет виджеты из шаблона)
- `update_info(name=None, description=None)`
- `add_widget(widget: Widget)`
- `remove_widget(widget_id)`
- `update_widget(widget_id, config=None, size=None, position=None)`
- `reorder_widgets(widget_ids: list[Id])`
- `share(user_id, access_level: ShareAccessLevel)`
- `unshare(user_id)`
- `set_auto_refresh(enabled, interval_seconds=None)`
- `set_default()` / `unset_default()`
- `delete()`

Инварианты:
- Виджеты уникальны по id в рамках дашборда
- Порядок виджетов определяется `order`
- `WidgetSize.cols` и `rows` в диапазоне 1–12
- Шаринг уникален по user_id в рамках дашборда
- Нельзя расшарить с самим собой (owner_id ≠ user_id)
- `is_default=True` — только один дашборд по умолчанию на workspace (проверка на app-слое)
- `refresh_interval_seconds` ≥ 30 (если auto_refresh включён)

### Report (Aggregate Root)

Поля:
- owner_id: Id
- workspace_id: Id | None (opaque, из Workspace BC)
- name: str
- description: str | None
- report_type: ReportType
- data_source: DataSource
- filters: list[FilterConfig]
- parameters: dict[str, str] — параметры отчёта (период, project_id и т.д.)
- schedule: ReportSchedule | None
- shares: list[ReportShare]
- last_generated_at: datetime | None
- last_export_format: ExportFormat | None
- created_at: datetime
- updated_at: datetime

Методы:
- `create(name, report_type, data_source, owner_id, workspace_id=None)` → `Report` (factory)
- `update_info(name=None, description=None)`
- `update_filters(filters: list[FilterConfig])`
- `set_parameter(key, value)`
- `remove_parameter(key)`
- `set_schedule(schedule: ReportSchedule)`
- `remove_schedule()`
- `deactivate_schedule()`
- `mark_generated()`
- `mark_exported(format: ExportFormat)`
- `share(user_id, access_level: ShareAccessLevel)`
- `unshare(user_id)`
- `delete()`

Инварианты:
- `ReportSchedule.recipients` не пустой, если schedule активна
- `ReportSchedule.frequency` — значение `ReportFrequency` enum
- Шаринг уникален по user_id в рамках отчёта
- Нельзя расшарить с самим собой (owner_id ≠ user_id)
- `data_source` должен быть совместим с `report_type` (проверка на app-слое)

## Repositories

| Репозиторий | Методы |
|---|---|
| `DashboardRepository` | `get_by_id`, `get_by_owner`, `get_by_workspace`, `get_shared_with_user`, `get_default_by_workspace`, `search` |
| `ReportRepository` | `get_by_id`, `get_by_owner`, `get_by_workspace`, `get_shared_with_user`, `get_scheduled_reports`, `get_by_type`, `get_by_data_source`, `search` |
| `DashboardTemplateRepository` | `get_by_id`, `get_system_templates`, `get_by_workspace`, `get_by_name`, `search` |

> **`DashboardRepository.get_shared_with_user`** — дашборды, расшаренные с пользователем.
>
> **`DashboardRepository.get_default_by_workspace`** — дашборд по умолчанию для workspace.
>
> **`ReportRepository.get_by_type`/`get_by_data_source`** — фильтрация отчётов по типу и источнику данных.
>
> **`DashboardTemplateRepository`** — управление шаблонами дашбордов.
