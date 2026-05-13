# Analytics BC — Спецификация

> Путь: `app/context/analytics/domain`
> Исходные требования: §11 (Отчётность и аналитика)

## Контекст

Analytics BC отвечает за дашборды, виджеты, отчёты, их планирование и шаринг. Данные для виджетов и отчётов формируются на infrastructure слое (запросы к другим BC через ACL). Analytics BC не хранит бизнес-данные — только конфигурацию отображения. Сюда перенесены `TimeReportPeriod` и `TimeReportGrouping` из TimeTracking BC.

---

## Принципы расширяемости

1. **WidgetType — расширяемый enum** — новые типы виджетов (BURNDOWN, HEATMAP, GAUGE и т.д.) = значение enum.
2. **DataSource — кросс-BC enum** — каждое значение принадлежит конкретному BC (см. `bounded_context`). Новый источник = значение enum + ACL-резолвер на infrastructure слое. Domain слой Analytics BC не импортирует другие BC.
3. **BoundedContextRef — enum-маркер** — opaque-ссылка на BC для маршрутизации запросов через ACL.
4. **AnalyticsQuery — единый кросс-BC запрос** — описывает «что считать» (metrics), «как группировать» (dimensions), «откуда брать» (data_source → BC), фильтры и период. Виджет/отчёт ссылается на `AnalyticsQuery`.
5. **FilterOperator — enum** — вместо магической строки `operator: str`. Новые операторы = значение enum.
6. **ReportSchedule.frequency — enum** — вместо магической строки. Новые частоты = значение enum.
7. **ReportType — расширяемый enum** — новые типы отчётов (в т.ч. кросс-BC: USER_ACTIVITY, AUDIT_SUMMARY и т.д.) = значение enum.
8. **Шаринг — entity** — `DashboardShare`/`ReportShare` для совместного доступа. Новые уровни доступа = расширение.
9. **Шаблоны — entity** — `DashboardTemplate` для предустановленных дашбордов. Новые шаблоны = запись.
10. **TimeReportPeriod/Grouping — здесь** — перенесены из TimeTracking BC, т.к. это аналитические концепты.

---

## Value Objects

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `WidgetType` | Enum | `PIE_CHART`, `LINE_CHART`, `BAR_CHART`, `NUMBER`, `TABLE`, `LIST`, `BURNDOWN_CHART`, `CUMULATIVE_FLOW`, `HEATMAP`, `GAUGE`, `KANBAN_BOARD`, `SCATTER_PLOT`, `HISTOGRAM` | §11.1 |
| `BoundedContextRef` | Enum | `IDENTITY`, `PROFILE`, `ORGANIZATION`, `WORKSPACE`, `PROJECT`, `TASK`, `COMMUNICATION`, `FILESTORAGE`, `TIMETRACKING`, `NOTIFICATION`, `SECURITY`, `BILLING`, `ANALYTICS` | §11.1 |
| `DataSource` | Enum (кросс-BC) | Task BC: `TASKS`, `TASK_STATUS_HISTORY`, `TASK_ASSIGNMENTS`, `TASK_TAGS`, `SPRINTS`, `SPRINT_BURNDOWN`, `SPRINT_VELOCITY`, `EPICS`; Project BC: `PROJECTS`, `PROJECT_MEMBERS`, `PROJECT_MILESTONES`, `PROJECT_PROGRESS`; TimeTracking BC: `TIME_ENTRIES`, `ACTIVITY_CATEGORIES`, `TIME_ENTRY_TAGS`, `WORKLOAD`; Communication BC: `COMMENTS`, `MENTIONS`, `REACTIONS`; FileStorage BC: `FILES`, `FILE_VERSIONS`, `FILE_STORAGE_USAGE`; Notification BC: `NOTIFICATIONS`, `NOTIFICATION_DELIVERIES`; Identity BC: `USERS`, `USER_SESSIONS`, `LOGIN_ATTEMPTS`; Profile BC: `PROFILES`; Organization BC: `ORGANIZATIONS`, `ORGANIZATION_MEMBERS`; Workspace BC: `WORKSPACES`, `WORKSPACE_MEMBERS`, `WORKSPACE_INVITATIONS`; Security BC: `AUDIT_LOGS`, `SECURITY_EVENTS`; Billing BC: `SUBSCRIPTIONS`, `INVOICES`, `PAYMENTS`; `CUSTOM` (произвольный) | §11.1 |
| `ReportType` | Enum | `BY_PROJECT`, `BY_TEAM`, `BY_PERIOD`, `BY_EFFORT`, `BY_PERFORMANCE`, `BURNDOWN`, `VELOCITY`, `CUMULATIVE_FLOW`, `TIME_TRACKING`, `BILLING_SUMMARY`, `WORKLOAD`, `USER_ACTIVITY`, `LOGIN_ACTIVITY`, `COMMUNICATION_VOLUME`, `STORAGE_USAGE`, `NOTIFICATION_DELIVERY`, `AUDIT_SUMMARY`, `SECURITY_INCIDENTS`, `SUBSCRIPTION_SUMMARY`, `CUSTOM` | §11.3 |
| `MetricAggregation` | Enum | `COUNT`, `COUNT_DISTINCT`, `SUM`, `AVG`, `MIN`, `MAX`, `MEDIAN`, `P90`, `P95`, `P99`, `RATE` | §11.1 |
| `TimeGranularity` | Enum | `HOUR`, `DAY`, `WEEK`, `MONTH`, `QUARTER`, `YEAR` | §11.1 |
| `SortOrder` | Enum | `ASC`, `DESC` | §11.1 |
| `ExportFormat` | Enum | `PDF`, `EXCEL`, `CSV`, `PNG`, `JSON`, `HTML` | §11.3 |
| `FilterOperator` | Enum | `EQ`, `NEQ`, `GT`, `GTE`, `LT`, `LTE`, `IN`, `NOT_IN`, `CONTAINS`, `STARTS_WITH`, `IS_NULL`, `IS_NOT_NULL`, `BETWEEN` | — |
| `FilterConfig` | frozen dataclass | field: str, operator: FilterOperator, value: str, value_to: str \| None (для BETWEEN) | — |
| `MetricDefinition` | frozen dataclass | field: str (default `*`), aggregation: MetricAggregation (default COUNT), alias: str \| None | §11.1 |
| `Dimension` | frozen dataclass | field: str, time_granularity: TimeGranularity \| None, alias: str \| None | §11.1 |
| `SortConfig` | frozen dataclass | field: str, order: SortOrder (default DESC) | §11.1 |
| `AnalyticsQuery` | frozen dataclass | data_source: DataSource, metrics: list[MetricDefinition], dimensions: list[Dimension], filters: list[FilterConfig], date_range: DateRange \| None, sort: list[SortConfig], limit: int \| None, raw: bool | §11.1 |
| `WidgetConfig` | frozen dataclass | widget_type: WidgetType, query: AnalyticsQuery, display_params: dict[str, Any] | §11.1 |
| `WidgetSize` | frozen dataclass | cols: int (1–12), rows: int (1–12) | §11.1 |
| `ReportFrequency` | Enum | `DAILY`, `WEEKLY`, `BIWEEKLY`, `MONTHLY`, `QUARTERLY` | §11.3 |
| `TimeReportPeriod` | Enum | `DAY`, `WEEK`, `MONTH`, `QUARTER`, `YEAR`, `CUSTOM` | §9.2 |
| `TimeReportGrouping` | Enum | `BY_USER`, `BY_TEAM`, `BY_PROJECT`, `BY_TASK`, `BY_CLIENT`, `BY_CATEGORY`, `BY_EPIC`, `BY_TAG` | §9.2 |
| `ShareAccessLevel` | Enum | `VIEW`, `EDIT`, `ADMIN` | §11.1 |

> **`WidgetType`** — `BURNDOWN_CHART` — sprint burndown, `CUMULATIVE_FLOW` — CFD, `HEATMAP` — heatmap активности, `GAUGE` — KPI gauge, `KANBAN_BOARD` — mini kanban, `SCATTER_PLOT` — scatter plot, `HISTOGRAM` — distribution. Новые типы виджетов = значение enum.
>
> **`BoundedContextRef`** — opaque-маркер BC. Domain слой Analytics BC не импортирует другие BC; маршрутизация запросов выполняется на infrastructure слое через ACL по `DataSource.bounded_context`.
>
> **`DataSource`** — каждое значение принадлежит ровно одному BC (`DataSource.bounded_context: BoundedContextRef`). `CUSTOM` маппится в `BoundedContextRef.ANALYTICS` и раскрывается на app-слое. Новые источники = значение enum + ACL-резолвер на infrastructure.
>
> **`AnalyticsQuery`** — единый запрос аналитики. Инварианты: либо хотя бы одна метрика, либо `raw=True`; `limit > 0`; `date_range` валидируется в `DateRange`. Свойства: `bounded_context` (делегирует к `data_source`), `has_time_series` (есть `Dimension` с `time_granularity`).
>
> **`MetricDefinition`** — поле + агрегация. `field='*'` допустим только с `COUNT`. `alias` — имя колонки в результате.
>
> **`Dimension`** — измерение группировки. Если задан `time_granularity` — поле трактуется как timestamp и группируется по интервалу (для временных рядов).
>
> **`SortConfig`** — сортировка по полю/алиасу метрики или измерения.
>
> **`WidgetConfig`** — `query` определяет данные (кросс-BC), `display_params` — параметры отображения (цвета, легенда, формат и т.д.) и не влияют на данные.
>
> **`ReportType`** — обычные отчёты (`BURNDOWN`, `VELOCITY`, `CUMULATIVE_FLOW`, `TIME_TRACKING`, `BILLING_SUMMARY`, `WORKLOAD`) + кросс-BC отчёты (`USER_ACTIVITY`, `LOGIN_ACTIVITY`, `COMMUNICATION_VOLUME`, `STORAGE_USAGE`, `NOTIFICATION_DELIVERY`, `AUDIT_SUMMARY`, `SECURITY_INCIDENTS`, `SUBSCRIPTION_SUMMARY`) + `CUSTOM`. Новые типы = значение enum.
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

| name | Описание | widget_configs (data_source → widget_type) |
|---|---|---|
| `Project Overview` | Обзор проекта | [`TASKS` (NUMBER), `TASKS` group by status (PIE_CHART), `SPRINT_BURNDOWN` (LINE_CHART), `PROJECT_PROGRESS` (GAUGE)] |
| `Sprint Dashboard` | Спринт дашборд | [`SPRINT_BURNDOWN` (LINE_CHART), `TASKS` group by status (BAR_CHART), `SPRINT_VELOCITY` (NUMBER), `WORKLOAD` (HEATMAP)] |
| `Time Tracking` | Учёт времени | [`TIME_ENTRIES` group by user (BAR_CHART), `TIME_ENTRIES` group by project (PIE_CHART), `TIME_ENTRIES` (TABLE)] |
| `Team Workload` | Нагрузка команды | [`WORKLOAD` (HEATMAP), `TASKS` group by priority (BAR_CHART), `TASKS` (NUMBER)] |

> Группировки и агрегации задаются через `AnalyticsQuery.dimensions`/`metrics`. Новые шаблоны = запись `DashboardTemplate` с `is_system=False`.

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
| `InvalidAnalyticsQueryException` | Некорректный аналитический запрос (`AnalyticsQuery`) |
| `InvalidDateRangeException` | Некорректный диапазон дат |
| `InvalidFilterOperatorException` | Некорректный оператор фильтра |
| `InvalidWidgetSizeException` | Некорректный размер виджета (cols/rows вне 1–12) |
| `NoRecipientsException` | У запланированного отчёта должен быть хотя бы один получатель |
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
- query: AnalyticsQuery — что и как считать (кросс-BC, см. VO выше)
- schedule: ReportSchedule | None
- shares: list[ReportShare]
- last_generated_at: datetime | None
- last_export_format: ExportFormat | None
- created_at: datetime
- updated_at: datetime

Методы:
- `create(name, report_type, query, owner_id, workspace_id=None, description=None)` → `Report` (factory)
- `update_info(name=None, description=None)`
- `update_query(query: AnalyticsQuery)` — no-op, если запрос не изменился
- `set_schedule(schedule: ReportSchedule)` — бросает `NoRecipientsException`, если `recipients` пуст
- `remove_schedule()`
- `deactivate_schedule()`
- `mark_generated(generated_by: Id)`
- `mark_exported(format: ExportFormat)`
- `share(user_id, access_level: ShareAccessLevel)`
- `unshare(user_id)`
- `delete()`

Инварианты:
- `ReportSchedule.recipients` не пустой при `set_schedule` (контролируется через `NoRecipientsException`)
- `ReportSchedule.frequency` — значение `ReportFrequency` enum
- `AnalyticsQuery` валиден (см. инварианты VO): метрики или `raw=True`, `limit > 0`, корректный `date_range`
- Шаринг уникален по user_id в рамках отчёта
- Нельзя расшарить с самим собой (owner_id ≠ user_id)
- `query.data_source` должен быть совместим с `report_type` (проверка на app-слое)

## Repositories

| Репозиторий | Методы |
|---|---|
| `DashboardRepository` | `get_by_id`, `get_by_owner`, `get_by_workspace`, `get_shared_with_user`, `get_default_by_workspace`, `search` |
| `ReportRepository` | `get_by_id`, `get_by_owner`, `get_by_workspace`, `get_shared_with_user`, `get_scheduled_reports`, `get_by_type`, `get_by_data_source`, `get_by_bounded_context`, `search` |
| `DashboardTemplateRepository` | `get_by_id`, `get_system_templates`, `get_by_workspace`, `get_by_name`, `search` |

> **`DashboardRepository.get_shared_with_user`** — дашборды, расшаренные с пользователем.
>
> **`DashboardRepository.get_default_by_workspace`** — дашборд по умолчанию для workspace.
>
> **`ReportRepository.get_by_type`/`get_by_data_source`/`get_by_bounded_context`** — фильтрация отчётов по типу, источнику данных или BC-источнику. `data_source` и `bounded_context` лежат внутри `Report.query`, поэтому инфраструктурный слой должен денормализовать их в индексируемые колонки (или использовать JSON-индексы).
>
> **`DashboardTemplateRepository`** — управление шаблонами дашбордов.
