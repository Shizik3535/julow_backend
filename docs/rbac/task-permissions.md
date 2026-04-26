# Проверки разрешений в Task Context

## Обзор механизма авторизации

Авторизация в Task Context реализована через порт `TaskPermissionCheckerPort` с двумя методами:

- **`require_permission(user_id, project_id, permission)`** — проверяет разрешение и выбрасывает `InsufficientTaskPermissionsException` при отсутствии. Используется в большинстве commands и queries.
- **`has_permission(user_id, project_id, permission)`** — возвращает `bool`, используется для фильтрации результатов (когда отсутствие разрешения не является ошибкой).

### Уровень проверки — project

Task BC не содержит собственного агрегата ролей. Все разрешения проверяются на уровне `project_id` проекта, которому принадлежит задача.

Поддерживаемые wildcard-шаблоны (project-уровень):
- `tasks.*` — полный доступ к задачам проекта
- `<group>.*` — все разрешения в группе
- `<group>.<action>` — конкретное разрешение (`tasks.read`, `tasks.update`, ...)

### Task-level participant permissions

Если пользователь является участником задач проекта (assignee, reporter, watcher), ему предоставляются ограниченные разрешения **без** project-роли:

- `tasks.read` — чтение задач проекта
- `tasks.watch` — добавление/удаление наблюдателей

Если пользователь является **исполнителем** (assignee) задач проекта, ему дополнительно предоставляются:

- `tasks.update_own` — обновление информации своих задач (приоритет, тип, метки, чек-листы, вложения, custom fields, recurrence, effort, progress)
- `tasks.update_status` — смена статуса своих задач

Это реализовано через `TaskRoleBasedPermissionChecker._TASK_PARTICIPANT_PERMISSIONS` и `_TASK_ASSIGNEE_PERMISSIONS`.

**Покрытие разрешений:** `tasks.update` покрывает `tasks.update_own` и `tasks.update_status` — проектная роль с `tasks.update` даёт полный доступ ко всем update-операциям.

### Каскад ProjectRole → WorkspaceRole → OrgRole

Если у пользователя нет task-участия, или оно не покрывает требуемое разрешение, проверка делегируется в `ProjectPermissionProvider`, который инкапсулирует каскад:

- **Task BC**: `tasks.<action>` на `project_id`
- **Project**: `tasks.<action>` или `project.*`
- **Workspace**: `projects.tasks.<action>` / `projects.*` / `ws.*`
- **Org**: `workspaces.projects.tasks.<action>` / `workspaces.projects.*` / `workspaces.*` / `org.*`

Каждый handler определяет константу `REQUIRED_PERMISSION` — требуемое разрешение для выполнения операции.

---

## Commands

### Команды с проверкой разрешений

| Команда | Handler | REQUIRED_PERMISSION | Дополнительные проверки |
|---|---|---|---|
| `AddChecklistCommand` | `AddChecklistHandler` | `tasks.update_own`¶ | — |
| `AddChecklistItemCommand` | `AddChecklistItemHandler` | `tasks.update_own`¶ | — |
| `AddTaskAttachmentCommand` | `AddTaskAttachmentHandler` | `tasks.update_own`¶ | Загрузка файла через `FileStoragePort` |
| `AddTaskLabelCommand` | `AddTaskLabelHandler` | `tasks.update_own`¶ | — |
| `AddTaskRelationCommand` | `AddTaskRelationHandler` | `tasks.update` | Проверка circular dependency для `BLOCKS`/`IS_BLOCKED_BY` |
| `ArchiveTaskCommand` | `ArchiveTaskHandler` | `tasks.delete` | — |
| `AssignChecklistItemCommand` | `AssignChecklistItemHandler` | `tasks.assign` | — |
| `AssignTaskCommand` | `AssignTaskHandler` | `tasks.assign`† | Проверка существования пользователя через `IdentityUserPort`; проверка членства в проекте через `ProjectMembershipPort` |
| `AssignTaskToEpicCommand` | `AssignTaskToEpicHandler` | `tasks.update` | Проверка существования и статуса эпика через `EpicPort` (отменённый эпик недоступен) |
| `AssignTaskToSprintCommand` | `AssignTaskToSprintHandler` | `tasks.update` | Проверка существования и статуса спринта через `SprintPort` (допустимы только `PLANNING`/`ACTIVE`) |
| `BulkUpdateTasksCommand` | `BulkUpdateTasksHandler` | `tasks.update` | Проверка разрешения на каждый уникальный проект; валидация перехода статуса через `BoardPort`; валидация спринта/эпика через соответствующие порты |
| `ChangeTaskPriorityCommand` | `ChangeTaskPriorityHandler` | `tasks.update_own`¶ | — |
| `ChangeTaskStatusCommand` | `ChangeTaskStatusHandler` | `tasks.update_status`¶ | Валидация перехода статуса через `BoardPort.is_transition_allowed` |
| `ChangeTaskTypeCommand` | `ChangeTaskTypeHandler` | `tasks.update_own`¶ | — |
| `ComputeTaskProgressCommand` | `ComputeTaskProgressHandler` | `tasks.update_own`¶ | — |
| `CreateTaskCommand` | `CreateTaskHandler` | `tasks.create` | Проверка существования и активности проекта через `ProjectPort`; назначение default workflow status через `BoardPort` |
| `CreateTaskFromTemplateCommand` | `CreateTaskFromTemplateHandler` | `tasks.create` | Проверка существования и активности проекта через `ProjectPort`; проверка существования шаблона; назначение default workflow status через `BoardPort` |
| `CreateTaskTemplateCommand` | `CreateTaskTemplateHandler` | `tasks.templates.manage` | Проверка на дубликат имени шаблона |
| `DeleteTaskCommand` | `DeleteTaskHandler` | `tasks.delete` | Soft-delete |
| `DeleteTaskTemplateCommand` | `DeleteTaskTemplateHandler` | `tasks.templates.manage`‡ | — |
| `MoveTaskCommand` | `MoveTaskHandler` | `tasks.update` | — |
| `RemoveChecklistCommand` | `RemoveChecklistHandler` | `tasks.update_own`¶ | — |
| `RemoveTaskAttachmentCommand` | `RemoveTaskAttachmentHandler` | `tasks.update_own`¶ | — |
| `RemoveTaskCustomFieldCommand` | `RemoveTaskCustomFieldHandler` | `tasks.update_own`¶ | — |
| `RemoveTaskFromEpicCommand` | `RemoveTaskFromEpicHandler` | `tasks.update` | — |
| `RemoveTaskFromSprintCommand` | `RemoveTaskFromSprintHandler` | `tasks.update` | — |
| `RemoveTaskLabelCommand` | `RemoveTaskLabelHandler` | `tasks.update_own`¶ | — |
| `RemoveTaskRecurrenceCommand` | `RemoveTaskRecurrenceHandler` | `tasks.update_own`¶ | — |
| `RemoveTaskRelationCommand` | `RemoveTaskRelationHandler` | `tasks.update` | — |
| `RemoveTaskWatcherCommand` | `RemoveTaskWatcherHandler` | `tasks.watch`† | — |
| `RestoreTaskCommand` | `RestoreTaskHandler` | `tasks.delete` | — |
| `SetActualEffortCommand` | `SetActualEffortHandler` | `tasks.update_own`¶ | — |
| `SetEffortEstimateCommand` | `SetEffortEstimateHandler` | `tasks.update_own`¶ | — |
| `SetTaskCustomFieldCommand` | `SetTaskCustomFieldHandler` | `tasks.update_own`¶ | Валидация имени поля через `ProjectPort` (CustomFieldDefinition) |
| `SetTaskRecurrenceCommand` | `SetTaskRecurrenceHandler` | `tasks.update_own`¶ | — |
| `ToggleChecklistItemCommand` | `ToggleChecklistItemHandler` | `tasks.update_own`¶ | — |
| `UnassignTaskCommand` | `UnassignTaskHandler` | `tasks.assign`† | — |
| `UpdateTaskInfoCommand` | `UpdateTaskInfoHandler` | `tasks.update_own`¶ | Запись изменений в changelog |
| `UpdateTaskProgressCommand` | `UpdateTaskProgressHandler` | `tasks.update_own`¶ | — |
| `UpdateTaskTemplateCommand` | `UpdateTaskTemplateHandler` | `tasks.templates.manage`‡ | — |

† — self-assign/self-unassign/self-watch/self-unwatch разрешены без проверки разрешения (когда `caller_id` совпадает с целевым пользователем)

‡ — проверка разрешения только для кастомных шаблонов (`project_id is not None`); системные шаблоны доступны без проверки

¶ — разрешение доступно assignee без project-роли (через `_TASK_ASSIGNEE_PERMISSIONS`); `tasks.update` покрывает эти разрешения для пользователей с project-ролью

---

## Queries

### Запросы без проверки разрешений

| Запрос | Handler | Описание |
|---|---|---|
| `GetTaskTemplatesQuery` | `GetTaskTemplatesHandler` | Получение системных шаблонов задач. Доступно без авторизации — системные шаблоны общедоступны. |

### Запросы с `require_permission`

| Запрос | Handler | REQUIRED_PERMISSION | Дополнительные проверки |
|---|---|---|---|
| `CountTasksByProjectQuery` | `CountTasksByProjectHandler` | `tasks.read` | — |
| `CountTasksByStatusQuery` | `CountTasksByStatusHandler` | `tasks.read` | — |
| `GetSubtasksQuery` | `GetSubtasksHandler` | `tasks.read` | — |
| `GetTaskQuery` | `GetTaskHandler` | `tasks.read` | — |
| `GetTaskChangelogQuery` | `GetTaskChangelogHandler` | `tasks.read` | — |
| `GetTaskChangelogByFieldQuery` | `GetTaskChangelogByFieldHandler` | `tasks.read` | — |
| `GetTaskTemplatesByProjectQuery` | `GetTaskTemplatesByProjectHandler` | `tasks.read` | — |
| `GetTasksByAssigneeQuery` | `GetTasksByAssigneeHandler` | `tasks.read` | — |
| `GetTasksByEpicQuery` | `GetTasksByEpicHandler` | `tasks.read` | — |
| `GetTasksByLabelsQuery` | `GetTasksByLabelsHandler` | `tasks.read` | — |
| `GetTasksByProjectQuery` | `GetTasksByProjectHandler` | `tasks.read` | — |
| `GetTasksByReporterQuery` | `GetTasksByReporterHandler` | `tasks.read` | — |
| `GetTasksBySprintQuery` | `GetTasksBySprintHandler` | `tasks.read` | — |
| `GetTasksByStatusQuery` | `GetTasksByStatusHandler` | `tasks.read` | — |

### Запросы с условной проверкой `require_permission`

| Запрос | Handler | REQUIRED_PERMISSION | Условие | Дополнительные проверки |
|---|---|---|---|---|
| `GetTaskTemplateQuery` | `GetTaskTemplateHandler` | `tasks.read` | Только для кастомных шаблонов (`project_id is not None`). Системные шаблоны читаемы без проверки. | — |
| `GetOverdueTasksQuery` | `GetOverdueTasksHandler` | `tasks.read` | Если указан `project_id` — `require_permission`. Иначе — фильтрация по участию (assignee, reporter, watcher). | — |
| `SearchTasksQuery` | `SearchTasksHandler` | `tasks.read` | Если указан `project_id` — `require_permission`. Иначе — фильтрация по участию (assignee, reporter, watcher). | — |

---

## Сводная таблица разрешений

| Разрешение | Commands | Queries |
|---|---|---|
| `tasks.create` | `CreateTask`, `CreateTaskFromTemplate` | — |
| `tasks.read` | — | `GetTask`, `GetSubtasks`, `GetTaskChangelog`, `GetTaskChangelogByField`, `GetTaskTemplatesByProject`, `GetTasksByProject`, `GetTasksByAssignee`, `GetTasksByReporter`, `GetTasksByEpic`, `GetTasksBySprint`, `GetTasksByLabels`, `GetTasksByStatus`, `CountTasksByProject`, `CountTasksByStatus`, `GetOverdueTasks`†, `SearchTasks`†, `GetTaskTemplate`‡ |
| `tasks.update` | `AddTaskRelation`, `AssignTaskToEpic`, `AssignTaskToSprint`, `BulkUpdateTasks`, `MoveTask`, `RemoveTaskFromEpic`, `RemoveTaskFromSprint`, `RemoveTaskRelation` | — |
| `tasks.update_own`¶ | `AddChecklist`, `AddChecklistItem`, `AddTaskAttachment`, `AddTaskLabel`, `ChangeTaskPriority`, `ChangeTaskType`, `ComputeTaskProgress`, `RemoveChecklist`, `RemoveTaskAttachment`, `RemoveTaskCustomField`, `RemoveTaskLabel`, `RemoveTaskRecurrence`, `SetActualEffort`, `SetEffortEstimate`, `SetTaskCustomField`, `SetTaskRecurrence`, `ToggleChecklistItem`, `UpdateTaskInfo`, `UpdateTaskProgress` | — |
| `tasks.update_status`¶ | `ChangeTaskStatus` | — |
| `tasks.delete` | `ArchiveTask`, `DeleteTask`, `RestoreTask` | — |
| `tasks.assign` | `AssignTask`†, `UnassignTask`†, `AssignChecklistItem` | — |
| `tasks.watch` | `AddTaskWatcher`†, `RemoveTaskWatcher`† | — |
| `tasks.templates.manage` | `CreateTaskTemplate`, `UpdateTaskTemplate`‡, `DeleteTaskTemplate`‡ | — |
| Без проверки | — | `GetTaskTemplates` |

† — self-операции (self-assign, self-unassign, self-watch, self-unwatch) разрешены без проверки разрешения; для запросов без `project_id` — фильтрация по участию вместо `require_permission`

‡ — `require_permission` применяется только для кастомных шаблонов (`project_id is not None`); системные шаблоны доступны без проверки

---

## Особенности Task BC

### Task-level participant permissions

Пользователь, являющийся участником задач проекта (assignee, reporter, watcher), получает ограниченный доступ без project-роли:
- **`tasks.read`** — чтение задач проекта
- **`tasks.watch`** — управление наблюдателями

Исполнитель (assignee) задач проекта дополнительно получает:
- **`tasks.update_own`** — обновление информации своих задач
- **`tasks.update_status`** — смена статуса своих задач

Это позволяет участникам задач просматривать проектные задачи, управлять своим наблюдением и (для assignee) обновлять свои задачи без явного членства в проекте.

### Self-операции

Следующие операции разрешены пользователю в отношении самого себя без проверки разрешения:
- **Self-assign** (`AssignTask`) — назначение себя исполнителем задачи
- **Self-unassign** (`UnassignTask`) — снятие себя с исполнения задачи
- **Self-watch** (`AddTaskWatcher`) — добавление себя в наблюдатели задачи
- **Self-unwatch** (`RemoveTaskWatcher`) — удаление себя из наблюдателей задачи

### Кросс-BC интеграции

- **`ProjectPort`** — проверка существования и активности проекта при создании задач (`CreateTask`, `CreateTaskFromTemplate`); валидация кастомных полей (`SetTaskCustomField`).
- **`BoardPort`** — получение default workflow status при создании задач; валидация перехода статусов (`ChangeTaskStatus`, `BulkUpdateTasks`).
- **`SprintPort`** — проверка существования и статуса спринта при назначении задачи в спринт (`AssignTaskToSprint`, `BulkUpdateTasks`).
- **`EpicPort`** — проверка существования и статуса эпика при привязке задачи к эпику (`AssignTaskToEpic`, `BulkUpdateTasks`).
- **`IdentityUserPort`** — проверка существования пользователя при назначении исполнителя (`AssignTask`).
- **`ProjectMembershipPort`** — проверка членства в проекте при назначении исполнителя (`AssignTask`).
- **`FileStoragePort`** — загрузка файлов для вложений задач (`AddTaskAttachment`).

### Системные vs кастомные шаблоны

Системные шаблоны задач (`is_system=True`, `project_id=None`) доступны для чтения и создания задач без проверки разрешений. Кастомные шаблоны (`project_id is not None`) требуют соответствующих разрешений на уровне проекта.
