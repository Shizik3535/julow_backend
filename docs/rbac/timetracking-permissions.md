# Проверки разрешений в TimeTracking Context

## Обзор механизма авторизации

TimeTracking BC использует workspace-уровневую авторизацию через порт `TimeTrackingPermissionCheckerPort`, который делегирует в `WorkspaceMembershipProvider.has_permission` (outboard Workspace BC).

Каждое разрешение TimeTracking имеет каскад в орг-роль:
`time.<perm>` (workspace) ← `workspaces.time.<perm>` (organization).

Поддерживаются wildcard-разрешения:
- `time.*` — полный доступ к записям, категориям и тегам в workspace
- `time.read` / `time.write` / `time.delete` / `time.submit` / `time.approve` / `time.admin` — конкретные

Дополнительно к проверке разрешений на ряд операций (редактирование, удаление, submit) накладывается доменная проверка владельца: только автор записи может изменить/удалить/отправить её, даже если у пользователя есть `time.write`/`time.delete`/`time.submit` на workspace. Это инвариант агрегата `TimeEntry` (см. `TimeEntryNotOwnerException`).

## Сводная таблица разрешений

### Workspace-разрешения

| Разрешение | Commands | Queries |
|---|---|---|
| `time.read` | — | `GetTimeEntry`, `GetTimeEntriesByWorkspace`, `GetActivityCategories`, `GetTimeEntryTags` |
| `time.write` | `StartTimer`, `PauseTimer`, `ResumeTimer`, `StopTimer`, `CreateManualTimeEntry`, `UpdateTimeEntry`, `AddTimeEntryTag`, `RemoveTimeEntryTag` | — |
| `time.delete` | `DeleteTimeEntry` | — |
| `time.submit` | `SubmitTimeEntry`, `ResubmitTimeEntry` | — |
| `time.approve` | `ApproveTimeEntry`, `RejectTimeEntry` | `GetSubmittedForApproval` |
| `time.admin` | `CreateActivityCategory`, `UpdateActivityCategory`, `DeleteActivityCategory`, `CreateTimeEntryTag`, `UpdateTimeEntryTag`, `DeleteTimeEntryTag` | — |

### Кросс-BC (Organization) разрешения

| Разрешение | Покрывает в TimeTracking |
|---|---|
| `workspaces.time.*` | Все `time.*` в workspace |
| `workspaces.time.read` | `time.read` |
| `workspaces.time.write` | `time.write` |
| `workspaces.time.delete` | `time.delete` |
| `workspaces.time.submit` | `time.submit` |
| `workspaces.time.approve` | `time.approve` |
| `workspaces.time.admin` | `time.admin` |

### Дополнительные доменные проверки (поверх RBAC)

| Операция | Дополнительное правило |
|---|---|
| `UpdateTimeEntry`, `DeleteTimeEntry`, `Pause/Resume/StopTimer`, `Add/RemoveTimeEntryTag`, `SubmitTimeEntry`, `ResubmitTimeEntry` | `caller_id == time_entry.user_id` (только владелец) |
| `ApproveTimeEntry` | `caller_id != time_entry.user_id` (нельзя утвердить свою же запись — `CannotApproveOwnTimeEntryException`) |
| `StartTimer` | У пользователя не должно быть активного таймера (`TimerAlreadyRunningException`) |
| `UpdateTimeEntry` | Только в статусе `DRAFT` (`CannotEditApprovedTimeEntryException`, `CannotEditLockedTimeEntryException`, `TimeEntryAlreadySubmittedException`) |
| `DeleteTimeEntry` | Только в статусе `DRAFT` |
| `DeleteActivityCategory` | Категория не должна быть системной (`CannotDeleteSystemCategoryException`) и не использоваться в записях (`ActivityCategoryInUseException`) |
| `CreateTimeEntryTag` | Уникальность `name` в пределах workspace (`DuplicateTimeEntryTagException`) |

## Системные роли (после seed)

| Роль | Разрешения TimeTracking |
|---|---|
| **workspace.owner** | `ws.*` (включает `time.*` через wildcard) |
| **workspace.admin** | `time.*` |
| **workspace.manager** | `time.read`, `time.write`, `time.submit`, `time.approve`, `time.admin` |
| **workspace.member** | `time.read`, `time.write`, `time.delete`, `time.submit` |
| **org.owner** | `org.*` + `workspaces.*` (cascade) |
| **org.admin** | `workspaces.time.*` |
| **org.moderator** | `workspaces.time.read`, `workspaces.time.write`, `workspaces.time.submit`, `workspaces.time.approve` |
| **org.member** | `workspaces.time.read` |

> Manager workspace-роли назначен `time.admin`, потому что управление словарями (категории/теги) — административная функция руководителя команды, а не платформы.
>
> Member workspace-роли получает `time.delete` (а не только `time.write`), чтобы пользователь мог удалить свою же черновую запись. Доменная проверка `user_id == caller_id` всё равно гарантирует, что удаляются только свои записи.
