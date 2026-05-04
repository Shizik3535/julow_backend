# События Analytics BC

## События, которые отдаёт Analytics BC

### Dashboard Events

| Событие | Описание | Поля |
|---|---|---|
| `DashboardCreated` | Дашборд создан | `dashboard_id`, `owner_id`, `workspace_id` |
| `DashboardCreatedFromTemplate` | Дашборд создан из шаблона | `dashboard_id`, `template_id` |
| `DashboardUpdated` | Дашборд обновлён | `dashboard_id`, `changed_fields` |
| `DashboardDeleted` | Дашборд удалён | `dashboard_id` |
| `DashboardShared` | Дашборд расшарен | `dashboard_id`, `user_id`, `access_level` |
| `DashboardUnshared` | Доступ к дашборду отозван | `dashboard_id`, `user_id` |
| `WidgetAdded` | Виджет добавлен | `dashboard_id`, `widget_id`, `widget_type` |
| `WidgetUpdated` | Виджет обновлён | `dashboard_id`, `widget_id` |
| `WidgetRemoved` | Виджет удалён | `dashboard_id`, `widget_id` |
| `WidgetReordered` | Виджеты переупорядочены | `dashboard_id` |

### Report Events

| Событие | Описание | Поля |
|---|---|---|
| `ReportCreated` | Отчёт создан | `report_id`, `report_type` |
| `ReportUpdated` | Отчёт обновлён | `report_id`, `changed_fields` |
| `ReportGenerated` | Отчёт сгенерирован | `report_id`, `generated_by` |
| `ReportScheduled` | Отчёт запланирован | `report_id`, `frequency` |
| `ReportScheduleDeactivated` | Расписание отчёта деактивировано | `report_id` |
| `ReportExported` | Отчёт экспортирован | `report_id`, `format` |
| `ReportShared` | Отчёт расшарен | `report_id`, `user_id`, `access_level` |
| `ReportUnshared` | Доступ к отчёту отозван | `report_id`, `user_id` |
| `ReportDeleted` | Отчёт удалён | `report_id` |

**Итого: 19 событий**

---

## События, на которые подписывается Analytics BC

Нет. Analytics BC не подписывается на события других BC.
