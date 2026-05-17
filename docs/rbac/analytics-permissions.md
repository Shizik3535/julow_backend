# Проверки разрешений в Analytics Context

## Обзор механизма авторизации

Analytics BC не содержит собственного агрегата ролей. Проверка разрешений выполняется через порт `AnalyticsPermissionCheckerPort`, который делегирует в `WorkspaceMembershipProvider.has_permission` (outboard Workspace BC) — то есть Analytics-разрешения проверяются как workspace-разрешения с каскадом в орг-роль.

- **`require_permission(user_id, workspace_id, permission)`** — проверяет разрешение и выбрасывает `InsufficientAnalyticsPermissionsException` при отсутствии. Используется во всех commands и queries.
- **`has_permission(user_id, workspace_id, permission)`** — возвращает `bool`, используется для фильтрации результатов.

Каждое analytics-разрешение имеет каскад в орг-роль:
`analytics.<perm>` (workspace) ← `workspaces.analytics.<perm>` (organization).

Поддерживаются wildcard-разрешения:
- `ws.*` — полный доступ в workspace (включая `analytics.*`)
- `analytics.*` — полный доступ к аналитике в workspace
- `analytics.report.*` — все операции с отчётами
- точные разрешения: `analytics.read`, `analytics.write`, `analytics.delete`, `analytics.share`, `analytics.report.write`, `analytics.report.run`, `analytics.report.schedule`, `analytics.admin`

Каждый handler определяет константу `REQUIRED_PERMISSION` — требуемое разрешение для выполнения операции.

---

## Commands

| Команда | Handler | REQUIRED_PERMISSION |
|---|---|---|
| `CreateDashboardCommand` | `CreateDashboardHandler` | `analytics.write` |
| `UpdateDashboardCommand` | `UpdateDashboardHandler` | `analytics.write` |
| `UpdateDashboardLayoutCommand` | `UpdateDashboardLayoutHandler` | `analytics.write` |
| `SetDashboardAutoRefreshCommand` | `SetDashboardAutoRefreshHandler` | `analytics.write` |
| `CreateDashboardFromTemplateCommand` | `CreateDashboardFromTemplateHandler` | `analytics.write` |
| `DeleteDashboardCommand` | `DeleteDashboardHandler` | `analytics.delete` |
| `SetDefaultDashboardCommand` | `SetDefaultDashboardHandler` | `analytics.admin` |
| `AddWidgetCommand` | `AddWidgetHandler` | `analytics.write` |
| `UpdateWidgetCommand` | `UpdateWidgetHandler` | `analytics.write` |
| `RemoveWidgetCommand` | `RemoveWidgetHandler` | `analytics.write` |
| `ShareDashboardCommand` | `ShareDashboardHandler` | `analytics.share` |
| `UnshareDashboardCommand` | `UnshareDashboardHandler` | `analytics.share` |
| `ShareReportCommand` | `ShareReportHandler` | `analytics.share` |
| `UnshareReportCommand` | `UnshareReportHandler` | `analytics.share` |
| `CreateReportCommand` | `CreateReportHandler` | `analytics.report.write` |
| `UpdateReportCommand` | `UpdateReportHandler` | `analytics.report.write` |
| `DeleteReportCommand` | `DeleteReportHandler` | `analytics.report.write` |
| `GenerateReportCommand` | `GenerateReportHandler` | `analytics.report.run` |
| `SendReportNowCommand` | `SendReportNowHandler` | `analytics.report.run` |
| `SetReportScheduleCommand` | `SetReportScheduleHandler` | `analytics.report.schedule` |
| `RemoveReportScheduleCommand` | `RemoveReportScheduleHandler` | `analytics.report.schedule` |
| `DeactivateReportScheduleCommand` | `DeactivateReportScheduleHandler` | `analytics.report.schedule` |
| `CreateCustomTemplateCommand` | `CreateCustomTemplateHandler` | `analytics.admin` |
| `DeleteTemplateCommand` | `DeleteTemplateHandler` | `analytics.admin` |

---

## Queries

| Запрос | Handler | REQUIRED_PERMISSION |
|---|---|---|
| `GetDashboardQuery` | `GetDashboardHandler` | `analytics.read` |
| `ListDashboardsByWorkspaceQuery` | `ListDashboardsByWorkspaceHandler` | `analytics.read` |
| `GetWidgetDataQuery` | `GetWidgetDataHandler` | `analytics.read` |
| `ExecuteAnalyticsQueryQuery` | `ExecuteAnalyticsQueryHandler` | `analytics.read` |
| `GetReportQuery` | `GetReportHandler` | `analytics.read` |
| `ListReportsByWorkspaceQuery` | `ListReportsByWorkspaceHandler` | `analytics.read` |

---

## Сводная таблица разрешений

### Workspace-разрешения

| Разрешение | Commands | Queries |
|---|---|---|
| `analytics.read` | — | `GetDashboard`, `ListDashboardsByWorkspace`, `GetWidgetData`, `ExecuteAnalyticsQuery`, `GetReport`, `ListReportsByWorkspace` |
| `analytics.write` | `CreateDashboard`, `UpdateDashboard`, `UpdateDashboardLayout`, `SetDashboardAutoRefresh`, `CreateDashboardFromTemplate`, `AddWidget`, `UpdateWidget`, `RemoveWidget` | — |
| `analytics.delete` | `DeleteDashboard` | — |
| `analytics.share` | `ShareDashboard`, `UnshareDashboard`, `ShareReport`, `UnshareReport` | — |
| `analytics.report.write` | `CreateReport`, `UpdateReport`, `DeleteReport` | — |
| `analytics.report.run` | `GenerateReport`, `SendReportNow` | — |
| `analytics.report.schedule` | `SetReportSchedule`, `RemoveReportSchedule`, `DeactivateReportSchedule` | — |
| `analytics.admin` | `SetDefaultDashboard`, `CreateCustomTemplate`, `DeleteTemplate` | — |

### Кросс-BC (Organization) разрешения

| Разрешение | Покрывает в Analytics |
|---|---|
| `workspaces.analytics.*` | Все `analytics.*` в workspace |
| `workspaces.analytics.read` | `analytics.read` |
| `workspaces.analytics.write` | `analytics.write` |
| `workspaces.analytics.delete` | `analytics.delete` |
| `workspaces.analytics.share` | `analytics.share` |
| `workspaces.analytics.report.write` | `analytics.report.write` |
| `workspaces.analytics.report.run` | `analytics.report.run` |
| `workspaces.analytics.report.schedule` | `analytics.report.schedule` |
| `workspaces.analytics.admin` | `analytics.admin` |

## Системные роли (после seed)

| Роль | Разрешения Analytics |
|---|---|
| **workspace.owner** | `ws.*` (включает `analytics.*` через wildcard) |
| **workspace.admin** | `analytics.*` |
| **workspace.manager** | `analytics.read`, `analytics.write`, `analytics.delete`, `analytics.share`, `analytics.report.write`, `analytics.report.run`, `analytics.report.schedule` |
| **workspace.member** | `analytics.read` |
| **org.owner** | `org.*` + `workspaces.*` (cascade) |
| **org.admin** | `workspaces.analytics.*` |
| **org.moderator** | `workspaces.analytics.read`, `workspaces.analytics.report.run` |
| **org.member** | `workspaces.analytics.read` |

> Manager workspace-роли не получает `analytics.admin` — управление шаблонами дашбордов и установка дефолтного дашборда workspace остаются за `admin`/`owner`.
>
> Org.moderator получает `workspaces.analytics.report.run`, чтобы модератор мог запускать готовые отчёты, но не может создавать/изменять отчёты или управлять расписаниями.
