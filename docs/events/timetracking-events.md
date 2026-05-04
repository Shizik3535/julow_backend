# События TimeTracking BC

## События, которые отдаёт TimeTracking BC

### Time Entry Events

| Событие | Описание | Поля |
|---|---|---|
| `TimerStarted` | Таймер запущен | `entry_id`, `user_id`, `task_id`, `project_id` |
| `TimerPaused` | Таймер приостановлен | `entry_id`, `accumulated_seconds` |
| `TimerResumed` | Таймер возобновлён | `entry_id` |
| `TimerStopped` | Таймер остановлен | `entry_id`, `duration_seconds` |
| `TimeEntryCreated` | Запись времени создана (ручной ввод) | `entry_id`, `user_id`, `entry_date`, `duration_seconds` |
| `TimeEntryUpdated` | Запись обновлена | `entry_id`, `changed_fields` |
| `TimeEntryDeleted` | Запись удалена | `entry_id` |
| `TimeEntrySubmitted` | Запись отправлена на утверждение | `entry_id`, `user_id` |
| `TimeEntryApproved` | Запись утверждена | `entry_id`, `approved_by` |
| `TimeEntryRejected` | Запись отклонена | `entry_id`, `rejected_by`, `reason` |
| `TimeEntryLocked` | Запись заблокирована (период закрыт) | `entry_id` |
| `TimeEntryCategoryChanged` | Категория изменена | `entry_id`, `category_name` |
| `TimeEntryBillableChanged` | Billable статус изменён | `entry_id`, `is_billable` |
| `TimeEntryTagAdded` | Тег добавлен | `entry_id`, `tag_name` |
| `TimeEntryTagRemoved` | Тег удалён | `entry_id`, `tag_name` |
| `UnfilledTimeReminderTriggered` | Напоминание о незаполненном времени | `user_id`, `entry_date` |
| `TimePeriodLocked` | Период времени заблокирован | `workspace_id`, `period_start`, `period_end` |

### Category Events

| Событие | Описание | Поля |
|---|---|---|
| `ActivityCategoryCreated` | Категория деятельности создана | `category_id`, `name` |
| `ActivityCategoryDeleted` | Категория деятельности удалена | `category_id` |

**Итого: 19 событий**

---

## События, на которые подписывается TimeTracking BC

Нет. TimeTracking BC не подписывается на события других BC.
