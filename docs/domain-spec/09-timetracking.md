# TimeTracking BC — Спецификация

> Путь: `app/context/timetracking/domain`
> Исходные требования: §9 (Учёт времени)

## Контекст

TimeTracking BC отвечает за трекинг времени: таймер (start/stop/pause), ручной ввод, привязка к задаче/проекту/эпику, категории деятельности, billable/non-billable, утверждение записей, напоминания о незаполненном времени. Отчёты по времени — в Analytics BC. Биллинг — в Billing BC.

---

## Принципы расширяемости

1. **TimeEntryStatus — enum** — жизненный цикл записи (DRAFT → SUBMITTED → APPROVED/REJECTED). Новые статусы = значение enum.
2. **ActivityCategory — entity** — вместо захардкоженных категорий. Новые категории = запись, не правка домена.
3. **Billable — поле** — `is_billable: bool` + `hourly_rate: Money | None`. Интеграция с Billing BC.
4. **TimeLog — entity** — детализация таймера (старты/паузы/стопы). Без захардкоженного `paused_duration`.
5. **TimeEntryTag — entity** — гибкая категоризация записей. Новые теги = запись.
6. **Аналитика — вне BC** — `TimeReportPeriod`/`TimeReportGrouping` перенесены в Analytics BC, не захардкожены в домене.
7. **Правила округления — VO** — `TimeRoundingRule` для настройки округления. Новые правила = расширение enum.

---

## Value Objects

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `TimerState` | Enum | `RUNNING`, `PAUSED`, `STOPPED` | §9.1 |
| `TimeEntryStatus` | Enum | `DRAFT`, `SUBMITTED`, `APPROVED`, `REJECTED`, `LOCKED` | §9.1 |
| `Duration` | frozen dataclass | seconds: int (≥0) | §9.1 |
| `Money` | frozen dataclass | amount: float, currency: str (ISO 4217) | §9.1 |
| `TimeRoundingRule` | Enum | `NONE`, `ROUND_UP_15`, `ROUND_UP_30`, `ROUND_NEAREST_15`, `ROUND_NEAREST_30` | §9.1 |
| `TimeRoundingConfig` | frozen dataclass | rule: TimeRoundingRule, apply_to: RoundingApplyTo | §9.1 |
| `RoundingApplyTo` | Enum | `TIMER_ONLY`, `MANUAL_ONLY`, `ALL` | §9.1 |
| `AccentColor` | frozen dataclass | hex: str (validated #RRGGBB) | §9.1 |

> **`TimeEntryStatus`** — жизненный цикл записи. `DRAFT` — черновик (можно редактировать), `SUBMITTED` — отправлено на утверждение, `APPROVED` — утверждено менеджером, `REJECTED` — отклонено (с причиной), `LOCKED` — заблокировано (прошедший период закрыт). Новые статусы = значение enum.
>
> **`Duration`** — типизированная замена `duration_seconds: int`. Инкапсулирует валидацию (≥0) и конверсии (в часы, минуты).
>
> **`Money`** — денежное значение для `hourly_rate`. `currency` — ISO 4217 (USD, EUR, RUB и т.д.). Используется для billable записей.
>
> **`TimeRoundingRule`** — правила округления времени. `ROUND_UP_15` — округление вверх до 15 минут, `ROUND_NEAREST_15` — до ближайших 15 минут. Новые правила (например, `ROUND_UP_6` для 6-минутных интервалов) = значение enum.
>
> **`TimeRoundingConfig`** — настраивает, к каким записям применять округление. `TIMER_ONLY` — только таймер, `MANUAL_ONLY` — только ручной ввод, `ALL` — ко всем.
>
> **`TimeReportPeriod`/`TimeReportGrouping`** — **перенесены в Analytics BC**. Это аналитические концепты, не доменные. TimeTracking BC только хранит записи, Analytics BC — агрегирует и группирует.

## Entities

| Сущность | Поля | Описание | Исходное требование |
|---|---|---|---|
| `TimeLog` | id: Id, action: TimerState, timestamp: datetime, accumulated_seconds: int | Запись старта/паузы/стопа таймера | §9.1 |
| `ActivityCategory` | id: Id, name: str, color: AccentColor \| None, is_system: bool, description: str \| None | Категория деятельности | §9.1 |
| `TimeEntryTag` | id: Id, name: str, color: AccentColor \| None | Тег записи времени | §9.1 |
| `RejectionReason` | id: Id, reason: str, rejected_by: Id, rejected_at: datetime | Причина отклонения записи | §9.1 |

> **`TimeLog`** — детализация работы таймера. Каждый старт/пауза/стоп = одна запись. `accumulated_seconds` — накопленное время на момент действия. Позволяет точно вычислить duration без захардкоженного `paused_duration`.
>
> **`ActivityCategory`** — категории деятельности (development, meeting, code review, testing, documentation, etc.). `is_system=True` — предустановленные, нельзя удалить. Новые категории = запись с `is_system=False`. Не enum — т.к. список динамический и расширяемый.
>
> **`TimeEntryTag`** — гибкая категоризация записей (например, "overtime", "weekend", "on-call"). Новые теги = запись, не правка домена.
>
> **`RejectionReason`** — при отклонении записи менеджером. Связана с `TimeEntryStatus.REJECTED`.

### Предустановленные системные категории

При инициализации создаются записи `ActivityCategory` с `is_system=True`:

| name | Описание |
|---|---|
| `development` | Разработка |
| `meeting` | Совещания |
| `code_review` | Ревью кода |
| `testing` | Тестирование |
| `documentation` | Документация |
| `planning` | Планирование |
| `communication` | Коммуникация |
| `admin` | Администрирование |
| `other` | Прочее |

> Новые категории (например, "mentoring", "training", "support") = запись `ActivityCategory` с `is_system=False`.

## Domain Events

| Событие | Поля | Описание | Исходное требование |
|---|---|---|---|
| `TimerStarted` | entry_id, user_id, task_id \| None, project_id \| None | Таймер запущен | §9.1 |
| `TimerPaused` | entry_id, accumulated_seconds | Таймер приостановлен | §9.1 |
| `TimerResumed` | entry_id | Таймер возобновлён | §9.1 |
| `TimerStopped` | entry_id, duration: Duration | Таймер остановлен | §9.1 |
| `TimeEntryCreated` | entry_id, user_id, entry_date, duration: Duration | Запись времени создана (ручной ввод) | §9.1 |
| `TimeEntryUpdated` | entry_id, changed_fields: list[str] | Запись обновлена | §9.1 |
| `TimeEntryDeleted` | entry_id | Запись удалена | §9.1 |
| `TimeEntrySubmitted` | entry_id, user_id | Запись отправлена на утверждение | §9.1 |
| `TimeEntryApproved` | entry_id, approved_by | Запись утверждена | §9.1 |
| `TimeEntryRejected` | entry_id, rejected_by, reason: str | Запись отклонена | §9.1 |
| `TimeEntryLocked` | entry_id | Запись заблокирована (период закрыт) | §9.1 |
| `TimeEntryCategoryChanged` | entry_id, category_name | Категория изменена | §9.1 |
| `TimeEntryBillableChanged` | entry_id, is_billable | Billable статус изменён | §9.1 |
| `TimeEntryTagAdded` | entry_id, tag_name | Тег добавлен | §9.1 |
| `TimeEntryTagRemoved` | entry_id, tag_name | Тег удалён | §9.1 |
| `ActivityCategoryCreated` | category_id, name | Категория создана | §9.1 |
| `ActivityCategoryDeleted` | category_id | Категория удалена | §9.1 |
| `UnfilledTimeReminderTriggered` | user_id, entry_date | Напоминание о незаполненном времени | §9.1 |
| `TimePeriodLocked` | workspace_id, period_start, period_end | Период времени заблокирован | §9.1 |

> **`TimerResumed`** — отдельный event от `TimerStarted`, т.к. это возобновление после паузы, а не новый старт.
>
> **`TimeEntrySubmitted`/`Approved`/`Rejected`** — workflow утверждения. `Rejected` включает причину. После `Approved` запись нельзя редактировать (только `LOCKED`).
>
> **`TimeEntryLocked`** — блокировка записей за прошедший период. Выпускается при закрытии периода (app-layer handler).
>
> **`TimePeriodLocked`** — закрытие временного периода (например, конец месяца). Все записи за этот период переходят в `LOCKED`.

## Exceptions

| Исключение | Описание |
|---|---|
| `TimeEntryNotFoundException` | Запись не найдена |
| `TimerAlreadyRunningException` | У пользователя уже есть запущенный таймер |
| `TimerNotRunningException` | Таймер не запущен |
| `TimerNotPausedException` | Таймер не на паузе (нельзя возобновить) |
| `CannotEditLockedTimeEntryException` | Нельзя редактировать заблокированную запись |
| `CannotEditApprovedTimeEntryException` | Нельзя редактировать утверждённую запись |
| `CannotSubmitDraftTimeEntryException` | Нельзя отправить черновик без обязательных полей |
| `CannotApproveOwnTimeEntryException` | Нельзя утвердить свою же запись |
| `TimeEntryAlreadySubmittedException` | Запись уже отправлена на утверждение |
| `TimeEntryAlreadyApprovedException` | Запись уже утверждена |
| `InvalidTimeEntryDurationException` | Некорректная длительность (≤0 или превышает лимит) |
| `DuplicateTimerException` | Только один активный таймер на пользователя |
| `ActivityCategoryNotFoundException` | Категория не найдена |
| `CannotDeleteSystemCategoryException` | Нельзя удалить системную категорию |
| `ActivityCategoryInUseException` | Категория используется в записях |
| `DuplicateTimeEntryTagException` | Тег с таким именем уже существует |
| `TimePeriodLockedException` | Период заблокирован, нельзя добавлять/редактировать записи |

## Aggregates

### TimeEntry (Aggregate Root)

Поля:
- user_id: Id
- task_id: Id | None (opaque, из Task BC)
- project_id: Id | None (opaque, из Project BC)
- epic_id: Id | None (opaque, из Epic AR в Project BC)
- workspace_id: Id (opaque, из Workspace BC)
- description: str | None
- timer_state: TimerState
- status: TimeEntryStatus
- started_at: datetime | None
- stopped_at: datetime | None
- duration: Duration
- entry_date: date
- is_billable: bool
- hourly_rate: Money | None — только если is_billable=True
- category: ActivityCategory | None
- tags: list[TimeEntryTag]
- time_logs: list[TimeLog] — детализация таймера
- rejection_reason: RejectionReason | None
- rounding_config: TimeRoundingConfig | None — применяется при stop_timer
- created_at: datetime
- updated_at: datetime

Методы:
- `create_manual(user_id, duration, entry_date, workspace_id, task_id=None, project_id=None, epic_id=None, description=None, is_billable=False, hourly_rate=None, category=None)` → `TimeEntry` (factory, timer_state=STOPPED, status=DRAFT)
- `start_timer(task_id=None, project_id=None, epic_id=None)` — из STOPPED → RUNNING, создаёт TimeLog
- `pause_timer()` — RUNNING → PAUSED, создаёт TimeLog с accumulated_seconds
- `resume_timer()` — PAUSED → RUNNING, создаёт TimeLog
- `stop_timer()` — RUNNING/PAUSED → STOPPED, подсчёт duration из time_logs, применение rounding_config
- `update(description=None, is_billable=None, hourly_rate=None, category=None)` — только если status=DRAFT
- `set_task(task_id)` — привязка к задаче
- `set_project(project_id)` — привязка к проекту
- `set_epic(epic_id)` — привязка к эпику
- `add_tag(tag: TimeEntryTag)`
- `remove_tag(tag_name)`
- `submit()` — DRAFT → SUBMITTED
- `approve(approved_by)` — SUBMITTED → APPROVED (только не свой собственный)
- `reject(rejected_by, reason)` — SUBMITTED → REJECTED
- `resubmit()` — REJECTED → SUBMITTED (после исправления)
- `lock()` — → LOCKED (вызывается app-layer handler при закрытии периода)
- `delete()` — только если status=DRAFT

Инварианты:
- Только один активный таймер на пользователя (проверка на repository/app-слое)
- `duration.seconds` ≥ 0
- Нельзя запустить уже запущенный таймер
- Нельзя остановить/паузировать не запущенный таймер
- Нельзя возобновить не приостановленный таймер
- `status=DRAFT` — можно редактировать
- `status=SUBMITTED` — нельзя редактировать, можно только reject/approve
- `status=APPROVED` — нельзя редактировать
- `status=REJECTED` — можно resubmit после исправления
- `status=LOCKED` — нельзя редактировать, удалять
- `is_billable=True` → `hourly_rate` должен быть задан
- `hourly_rate` не может быть задан если `is_billable=False`
- Заблокированные записи (прошедший период) нельзя редактировать
- Нельзя утвердить свою собственную запись
- `time_logs` — только для записей созданных через таймер, не для ручного ввода

## Repositories

| Репозиторий | Методы |
|---|---|
| `TimeEntryRepository` | `get_by_id`, `get_by_user`, `get_by_user_and_date`, `get_by_task`, `get_by_project`, `get_by_epic`, `get_by_workspace`, `get_running_timer`, `get_by_status`, `get_submitted_for_approval`, `get_by_category`, `sum_duration_by_user`, `sum_duration_by_project`, `search` |
| `ActivityCategoryRepository` | `get_by_id`, `get_by_name`, `get_system_categories`, `get_by_workspace`, `search` |
| `TimeEntryTagRepository` | `get_by_id`, `get_by_name`, `get_by_workspace` |

> **`TimeEntryRepository.get_submitted_for_approval`** — записи со статусом SUBMITTED для менеджера.
>
> **`TimeEntryRepository.sum_duration_by_user`/`sum_duration_by_project`** — агрегация для аналитики (используется Analytics BC через ACL).
>
> **`TimeEntryRepository.get_by_user_and_date`** — записи пользователя за конкретный день (для напоминаний о незаполненном времени).

## Интеграция с другими BC

| Поле TimeEntry | Сущность BC | Проверка на app-слое |
|---|---|---|
| `task_id` | Task AR (Task BC) | Существование задачи, пользователь — assignee/watcher |
| `project_id` | Project AR (Project BC) | Существование проекта, пользователь — участник |
| `epic_id` | Epic AR (Project BC) | Существование эпика, `MethodologyCapabilities.has_epics` |
| `workspace_id` | Workspace AR (Workspace BC) | Существование workspace, пользователь — член |
| `is_billable` + `hourly_rate` | Billing BC | Отправка утверждённых billable записей в Billing BC через events |

> **Связь через events** — `TimeEntryApproved` с `is_billable=True` → app-layer handler отправляет данные в Billing BC. `TimePeriodLocked` → блокировка всех записей за период.
