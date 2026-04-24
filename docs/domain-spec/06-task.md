# Task BC — Спецификация

> Путь: `app/context/task/domain`
> Исходные требования: §6 (Задачи)

## Контекст

Task BC отвечает за задачи: поля, иерархию, связи, чек-листы, drag-n-drop, массовые действия, историю изменений, кастомные поля, watchers. Статусы задач берутся из Project BC (workflow). Кастомные поля определяются в Project BC (`CustomFieldDefinition`), значения хранятся в Task BC. Эпики — отдельный AR в Project BC, задачи ссылаются на них через opaque ID.

---

## Принципы расширяемости

1. **TaskType — расширяемый enum** — новые типы задач (Test Case, Spike, Documentation) = значение enum. Иерархия определяется через `parent_task_id`, не через тип.
2. **Кастомные поля — dict** — `custom_fields: dict[str, str]` на задаче. Определения в Project BC (`CustomFieldDefinition`), значения в Task BC. Новое поле = запись в Project BC, не правка Task BC.
3. **EffortUnit — enum** — вместо магической строки "hours"/"story_points". Новые единицы оценки = значение enum.
4. **Гибкая иерархия** — `parent_task_id` + проверка `depth` на app-слое (лимит из Project BC). Нет захардкоженного "≤ 4 уровней".
5. **Events с changed_fields** — детализация изменений без взрыва количества events.
6. **Интеграция с Project BC** — `status_id`, `sprint_id`, `epic_id`, `column_id` — opaque ID, проверка валидности на app-слое. Task BC не импортирует Project BC.

---

## Value Objects

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `TaskPriority` | Enum | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `NONE` | §6.2 |
| `TaskType` | Enum | `EPIC`, `STORY`, `TASK`, `SUBTASK`, `BUG`, `FEATURE`, `IMPROVEMENT`, `TEST_CASE`, `SPIKE`, `DOCUMENTATION` | §6.2 |
| `TaskStatus` | Enum | `ACTIVE`, `ARCHIVED`, `DELETED` | §6.1 |
| `TaskProgress` | frozen dataclass | value: int (0–100) | §6.2 |
| `EffortUnit` | Enum | `HOURS`, `STORY_POINTS`, `DAYS`, `T_SHIRT` | §6.2 |
| `EffortEstimate` | frozen dataclass | value: float, unit: EffortUnit | §6.2 |
| `ActualEffort` | frozen dataclass | value: float, unit: EffortUnit | §6.2 |
| `TShirtSize` | Enum | `XS`, `S`, `M`, `L`, `XL` | §6.2 |
| `RelationType` | Enum | `BLOCKS`, `IS_BLOCKED_BY`, `RELATES_TO`, `DUPLICATES`, `IS_DUPLICATED_BY`, `CAUSES`, `IS_CAUSED_BY`, `PARENT`, `CHILD`, `FOLLOWS`, `PRECEDES` | §6.3 |
| `Label` | frozen dataclass | name: str, color: AccentColor \| None | §6.2 |
| `AccentColor` | frozen dataclass | hex: str (validated #RRGGBB) | §6.2 |
| `TaskOrder` | frozen dataclass | position: float, column_id: Id (opaque, из Project BC) | §6.1 |
| `RecurrencePattern` | Enum | `DAILY`, `WEEKLY`, `BIWEEKLY`, `MONTHLY`, `QUARTERLY` | — |
| `RecurrenceConfig` | frozen dataclass | pattern: RecurrencePattern, interval: int, end_date: date \| None, max_occurrences: int \| None | — |

> **`TaskType`** — новые типы задач = значение enum. UI может показывать разные иконки/поля по типу. `EPIC` — корневой тип для иерархии, но задачи любого типа могут быть родителями через `parent_task_id`.
>
> **`TaskStatus`** — жизненный цикл задачи в рамках Task BC (не путать с workflow status из Project BC). `ACTIVE` — рабочее состояние, `ARCHIVED` — архив, `DELETED` — soft delete (данные сохраняются).
>
> **`EffortUnit`** — `T_SHIRT` размер использует `TShirtSize` enum вместо float. Валидация на app-слое: если unit=T_SHIRT, value интерпретируется как индекс TShirtSize. Новые единицы (например, `POINTS`, `IDEAL_DAYS`) = значение enum.
>
> **`EffortEstimate`/`ActualEffort`** — типизированная замена `hours: float, unit: str`. Оба используют `EffortUnit`, что гарантирует совместимость при сравнении оценки и факта.
>
> **`RelationType`** — `FOLLOWS`/`PRECEDES` для последовательных задач (pipeline). Новые типы связей = значение enum.
>
> **`TaskOrder.column_id`** — `Id` вместо `str` для типобезопасности. Opaque ID из Board AR (Project BC).
>
> **`RecurrenceConfig`** — конфигурация повторяющихся задач. При завершении задачи с `recurrence` app-layer handler автоматически создаёт следующую задачу.

## Entities

| Сущность | Поля | Описание | Исходное требование |
|---|---|---|---|
| `ChecklistItem` | id: Id, text: str, is_checked: bool, assignee_id: Id \| None, due_date: date \| None, checked_at: datetime \| None, order: int | Пункт чек-листа | §6.4 |
| `Checklist` | id: Id, title: str, items: list[ChecklistItem] | Чек-лист внутри задачи | §6.4 |
| `TaskRelation` | related_task_id: Id, relation_type: RelationType, created_at: datetime, created_by: Id | Связь с другой задачей | §6.3 |
| `TaskWatcher` | user_id: Id, watched_at: datetime | Наблюдатель задачи | — |
| `TaskAttachment` | file_id: Id (opaque, из FileStorage BC), filename: str, size_bytes: int, uploaded_by: Id, uploaded_at: datetime | Вложение задачи | — |
| `ChangelogEntry` | id: Id, field_name: str, old_value: str \| None, new_value: str \| None, changed_by: Id, changed_at: datetime | Запись истории изменений | §6.1 |
| `TaskTemplate` | name: str, description: RichText \| None, task_type: TaskType, default_labels: list[Label], default_checklists: list[Checklist], default_custom_fields: dict[str, str] | Шаблон задачи | — |

> **`ChecklistItem`** — добавлены `id` и `order` для уникальной идентификации и упорядочивания пунктов внутри чек-листа.
>
> **`TaskRelation`** — добавлен `created_by` для аудита: кто и когда установил связь.
>
> **`TaskWatcher`** — подписка на изменения задачи без назначения исполнителем. Watcher получает уведомления о всех изменениях задачи (статус, приоритет, комментарий, назначение). Добавляется/удаляется через методы AR.
>
> **`TaskAttachment`** — ссылка на файл в FileStorage BC. Сам файл не хранится в Task BC. Opaque `file_id` для слабой связи. Удаление вложения из задачи не удаляет файл из FileStorage.
>
> **`ChangelogEntry`** — entity для хранения истории изменений. Каждое изменение поля = одна запись. Не загружается полностью в агрегат Task — доступ через `ChangelogRepository` с пагинацией. Записывается на app-слое при каждом изменении задачи. Тысячи записей не загружаются в память.
>
> **`TaskTemplate`** — шаблон для создания типовых задач. Определяется на уровне проекта (Project BC), но используется в Task BC при создании. `default_custom_fields` — предзаполненные значения кастомных полей. Новые шаблоны = новая запись, не правка домена.

## Domain Events

| Событие | Поля | Описание | Исходное требование |
|---|---|---|---|
| `TaskCreated` | task_id, project_id, title, task_type, parent_task_id \| None, epic_id \| None | Задача создана | §6.1 |
| `TaskInfoChanged` | task_id, changed_fields: list[str] | Информация обновлена (title, description, start_date, due_date) | §6.1 |
| `TaskArchived` | task_id | Задача архивирована | §6.1 |
| `TaskRestored` | task_id | Задача восстановлена | §6.1 |
| `TaskDeleted` | task_id | Задача удалена (soft delete) | §6.1 |
| `TaskStatusChanged` | task_id, old_status_id, new_status_id | Workflow статус изменён | §6.2 |
| `TaskAssigned` | task_id, assignee_id | Исполнитель назначен | §6.2 |
| `TaskUnassigned` | task_id, assignee_id | Исполнитель снят | §6.2 |
| `TaskPriorityChanged` | task_id, new_priority | Приоритет изменён | §6.2 |
| `TaskTypeChanged` | task_id, new_type | Тип изменён | §6.2 |
| `TaskMoved` | task_id, new_column_id, new_position | Задача перемещена (drag-n-drop) | §6.1 |
| `TaskMovedToSprint` | task_id, sprint_id | Задача назначена на спринт | §6.2 |
| `TaskRemovedFromSprint` | task_id | Задача убрана из спринта | §6.2 |
| `TaskMovedToEpic` | task_id, epic_id | Задача привязана к эпику | §6.2 |
| `TaskRemovedFromEpic` | task_id | Задача отвязана от эпика | §6.2 |
| `BulkTasksUpdated` | task_ids, changes: dict[str, str] | Массовое обновление | §6.1 |
| `ChecklistAdded` | task_id, checklist_id | Чек-лист добавлен | §6.4 |
| `ChecklistRemoved` | task_id, checklist_id | Чек-лист удалён | §6.4 |
| `ChecklistItemAdded` | task_id, checklist_id | Пункт добавлен | §6.4 |
| `ChecklistItemToggled` | task_id, checklist_id, item_id | Пункт отмечен/снят | §6.4 |
| `ChecklistItemAssigned` | task_id, checklist_id, assignee_id | Исполнитель назначен на пункт | §6.4 |
| `TaskRelationAdded` | task_id, related_task_id, relation_type | Связь добавлена | §6.3 |
| `TaskRelationRemoved` | task_id, related_task_id, relation_type | Связь удалена | §6.3 |
| `TaskProgressUpdated` | task_id, new_percent | Прогресс обновлён | §6.2 |
| `TaskEffortUpdated` | task_id, changed_fields: list[str] | Оценка/фактическое усилие обновлено | §6.2 |
| `TaskWatcherAdded` | task_id, user_id | Наблюдатель добавлен | — |
| `TaskWatcherRemoved` | task_id, user_id | Наблюдатель удалён | — |
| `TaskAttachmentAdded` | task_id, file_id | Вложение добавлено | — |
| `TaskAttachmentRemoved` | task_id, file_id | Вложение удалено | — |
| `TaskCustomFieldChanged` | task_id, field_name, old_value, new_value | Кастомное поле изменено | — |
| `TaskDeadlineApproaching` | task_id, due_date | Дедлайн приближается | §10.2 |
| `TaskOverdue` | task_id, due_date | Задача просрочена | §10.2 |
| `RecurringTaskCreated` | source_task_id, new_task_id | Повторяющаяся задача создана | — |
| `TaskCommentAdded` | task_id, comment_id (opaque, из Communication BC) | Комментарий добавлен | §7 |

> **`TaskStatusChanged`** — отдельный event (не через `TaskInfoChanged`), т.к. это ключевое действие, триггерит автоматизации (AutomationRule в Board AR) и уведомления.
>
> **`TaskInfoChanged.changed_fields`** — список имён изменённых полей. Например, `TaskInfoChanged(changed_fields=["title", "due_date"])`. Добавление нового поля в задачу не требует нового event.
>
> **`BulkTasksUpdated.changes`** — dict с именами полей и их новыми значениями. Детализация массового обновления вместо одного безликого event.
>
> **`TaskEffortUpdated.changed_fields`** — может быть `["effort_estimate"]`, `["actual_effort"]` или оба. Один event покрывает оба поля усилия.
>
> **`TaskMovedToEpic`/`TaskRemovedFromEpic`** — эпики теперь отдельный AR в Project BC, задачи ссылаются на них через `epic_id`. Эти events позволяют Epic AR реагировать (обновить счётчик задач).
>
> **`TaskCommentAdded`** — событие-мост: комментарий создаётся в Communication BC, но Task BC выпускает событие для watchers и уведомлений. `comment_id` — opaque ID из Communication BC.
>
> **`RecurringTaskCreated`** — выпускается app-layer handler при автоматическом создании следующей задачи из `RecurrenceConfig`.

## Exceptions

| Исключение | Описание |
|---|---|
| `TaskNotFoundException` | Задача не найдена |
| `TaskArchivedException` | Задача архивирована, действие невозможно |
| `CannotChangeStatusException` | Переход статуса не разрешён workflow (Project BC) |
| `CircularDependencyException` | Циклическая зависимость между задачами |
| `TaskHierarchyDepthExceededException` | Превышена максимальная глубина иерархии (лимит из Project BC) |
| `InvalidTaskRelationException` | Некорректная связь |
| `CannotRelateTaskToSelfException` | Нельзя связать задачу саму с собой |
| `DuplicateRelationException` | Связь уже существует (same related_task_id + relation_type) |
| `ChecklistNotFoundException` | Чек-лист не найден |
| `ChecklistItemNotFoundException` | Пункт чек-листа не найден |
| `DuplicateWatcherException` | Наблюдатель уже подписан |
| `AttachmentNotFoundException` | Вложение не найдено |
| `EffortUnitMismatchException` | Единицы оценки и факта не совпадают |
| `InvalidEffortValueException` | Некорректное значение усилия |
| `RecurringTaskConfigurationException` | Некорректная конфигурация повторения |
| `DuplicateLabelException` | Метка с таким именем уже существует на задаче |

## Aggregates

### Task (Aggregate Root)

Поля:
- project_id: Id (opaque, из Project BC)
- parent_task_id: Id | None (для иерархии)
- epic_id: Id | None (opaque, из Epic AR в Project BC)
- title: str
- description: RichText | None
- status_id: Id | None (opaque, из WorkflowStatus Board AR в Project BC)
- priority: TaskPriority
- task_type: TaskType
- assignee_ids: list[Id]
- reporter_id: Id | None
- labels: list[Label]
- progress: TaskProgress
- effort_estimate: EffortEstimate | None
- actual_effort: ActualEffort | None
- start_date: date | None
- due_date: date | None
- completed_at: datetime | None
- custom_fields: dict[str, str] — значения кастомных полей (ключи из CustomFieldDefinition в Project BC)
- checklists: list[Checklist]
- relations: list[TaskRelation]
- watchers: list[TaskWatcher]
- attachments: list[TaskAttachment]
- order: TaskOrder
- sprint_id: Id | None (opaque, из Sprint AR в Project BC)
- status: TaskStatus (ACTIVE / ARCHIVED / DELETED)
- recurrence: RecurrenceConfig | None
- created_at: datetime
- updated_at: datetime

Методы:
- `create(title, project_id, task_type, reporter_id, parent_task_id=None, epic_id=None)` → `Task` (factory)
- `create_from_template(template: TaskTemplate, project_id, reporter_id)` → `Task` (factory, заполняет поля из шаблона)
- `update_info(title=None, description=None, start_date=None, due_date=None)`
- `change_status(new_status_id)` — проверка перехода на app-слое через workflow Board AR
- `change_priority(priority)`
- `change_type(task_type)`
- `assign(user_id)`
- `unassign(user_id)`
- `update_progress(progress)` — может авто-вычисляться из чек-листа
- `compute_progress_from_checklists()` — auto-calculate based on checked/total items
- `set_effort_estimate(estimate)`
- `set_actual_effort(effort)`
- `add_label(label)` / `remove_label(label_name)`
- `move(column_id, position)` — drag-n-drop
- `archive()` / `restore()`
- `soft_delete()`
- `add_relation(related_task_id, relation_type)`
- `remove_relation(related_task_id, relation_type)`
- `add_checklist(title)` → `Checklist`
- `remove_checklist(checklist_id)`
- `add_checklist_item(checklist_id, text, assignee_id=None, due_date=None)`
- `toggle_checklist_item(checklist_id, item_id)`
- `assign_checklist_item(checklist_id, item_id, assignee_id)`
- `assign_to_sprint(sprint_id)`
- `remove_from_sprint()`
- `assign_to_epic(epic_id)`
- `remove_from_epic()`
- `add_watcher(user_id)`
- `remove_watcher(user_id)`
- `add_attachment(file_id, filename, size_bytes, uploaded_by)`
- `remove_attachment(file_id)`
- `set_custom_field(field_name, value)` — валидация типа на app-слое через CustomFieldDefinition
- `remove_custom_field(field_name)`
- `set_recurrence(config: RecurrenceConfig)`
- `remove_recurrence()`

Инварианты:
- Нельзя связать задачу саму с собой
- Нельзя создать дублирующую связь (same related_task_id + relation_type)
- Circular dependency: задача A блокирует B, B блокирует C → C не может блокировать A (проверка на app-слое, обход графа связей)
- Прогресс 0–100
- Статус берётся из Project BC через opaque ID, валидация перехода на app-слое через workflow
- `effort_estimate` и `actual_effort` должны использовать совместимые `EffortUnit` (проверка при установке)
- `TaskStatus.DELETED` — soft delete, данные сохраняются для восстановления
- Глубина иерархии проверяется на app-слое (лимит из Project BC или WorkspaceLimits). Нет захардкоженного "≤ 4 уровней"
- Ключи `custom_fields` должны соответствовать `CustomFieldDefinition` в Project BC (проверка на app-слое)
- Задача с `recurrence` при завершении может автоматически создавать следующую (app-layer handler)
- Labels уникальны по имени в рамках задачи
- Watchers уникальны по user_id в рамках задачи

## Repositories

| Репозиторий | Методы |
|---|---|
| `TaskRepository` | `get_by_id`, `get_by_project`, `get_by_assignee`, `get_by_reporter`, `get_subtasks`, `get_by_sprint`, `get_by_epic`, `get_overdue_tasks`, `get_by_status`, `get_by_parent`, `get_by_labels`, `search`, `count_by_project`, `count_by_status` |
| `ChangelogRepository` | `get_by_task_id`, `get_by_task_and_field`, `get_recent_changes`, `count_by_task` |
| `TaskTemplateRepository` | `get_by_id`, `get_by_project`, `get_system_templates`, `get_by_name` |

## Интеграция с Project BC

Task BC ссылается на Project BC через opaque ID. Все проверки валидности — на app-слое. Task BC не импортирует Project BC.

| Поле Task | Сущность Project BC | Проверка на app-слое |
|---|---|---|
| `project_id` | Project AR | Существование проекта, статус не ARCHIVED/SUSPENDED |
| `status_id` | WorkflowStatus (Board AR) | Валидность статуса, разрешённые переходы (WorkflowTransition) |
| `sprint_id` | Sprint AR | Существование спринта, статус PLANNING/ACTIVE, `MethodologyCapabilities.has_sprints` |
| `epic_id` | Epic AR | Существование эпика, статус не CANCELLED, `MethodologyCapabilities.has_epics` |
| `order.column_id` | BoardColumn (Board AR) | Существование колонки, WIP-лимит не превышен |
| `custom_fields` keys | CustomFieldDefinition (Project AR) | Валидность имени поля, тип значения соответствует `CustomFieldType` |
| `parent_task_id` depth | MethodologyCapabilities / WorkspaceLimits | Максимальная глубина иерархии не превышена |
| `task_type` | MethodologyCapabilities | Доступность типа для текущей методологии |

> **Связь через events** — Project BC выпускает события при изменении workflow, удалении спринта, архивации проекта. App-layer handlers в Task BC реагируют на эти события (например, отменяют назначение задач на удалённый спринт).

## Предустановленные шаблоны задач

| name | task_type | default_labels | default_checklists |
|---|---|---|---|
| `Bug Report` | BUG | [bug] | [Steps to Reproduce, Expected Result, Actual Result] |
| `Feature Request` | FEATURE | [feature] | [Acceptance Criteria] |
| `Spike` | SPIKE | [spike] | [Findings, Recommendation] |
| `User Story` | STORY | [story] | [Acceptance Criteria] |
| `Task` | TASK | [] | [] |

> Новые шаблоны = новая запись `TaskTemplate`. Без правки домена. Шаблоны могут создаваться на уровне проекта (Project BC) или как системные.
