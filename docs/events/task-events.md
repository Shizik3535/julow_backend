# События Task BC

## События, которые отдаёт Task BC

### Task Events

| Событие | Описание | Поля |
|---|---|---|
| `TaskCreated` | Задача создана | `task_id`, `project_id`, `title`, `task_type`, `parent_task_id`, `epic_id` |
| `TaskInfoChanged` | Информация задачи обновлена | `task_id`, `changed_fields` |
| `TaskArchived` | Задача архивирована | `task_id` |
| `TaskRestored` | Задача восстановлена | `task_id` |
| `TaskDeleted` | Задача удалена (soft delete) | `task_id` |
| `TaskStatusChanged` | Workflow статус изменён | `task_id`, `old_status_id`, `new_status_id` |
| `TaskAssigned` | Исполнитель назначен | `task_id`, `assignee_id` |
| `TaskUnassigned` | Исполнитель снят | `task_id`, `assignee_id` |
| `TaskPriorityChanged` | Приоритет изменён | `task_id`, `new_priority` |
| `TaskTypeChanged` | Тип изменён | `task_id`, `new_type` |
| `TaskMoved` | Задача перемещена (drag-n-drop) | `task_id`, `new_column_id`, `new_position` |
| `TaskMovedToSprint` | Задача назначена на спринт | `task_id`, `sprint_id` |
| `TaskRemovedFromSprint` | Задача убрана из спринта | `task_id` |
| `TaskMovedToEpic` | Задача привязана к эпику | `task_id`, `epic_id` |
| `TaskRemovedFromEpic` | Задача отвязана от эпика | `task_id` |
| `BulkTasksUpdated` | Массовое обновление задач | `task_ids`, `changes` |
| `ChecklistAdded` | Чек-лист добавлен | `task_id`, `checklist_id` |
| `ChecklistRemoved` | Чек-лист удалён | `task_id`, `checklist_id` |
| `ChecklistItemAdded` | Пункт чек-листа добавлен | `task_id`, `checklist_id` |
| `ChecklistItemToggled` | Пункт чек-листа отмечен/снят | `task_id`, `checklist_id`, `item_id` |
| `ChecklistItemAssigned` | Исполнитель назначен на пункт чек-листа | `task_id`, `checklist_id`, `assignee_id` |
| `TaskRelationAdded` | Связь добавлена | `task_id`, `related_task_id`, `relation_type` |
| `TaskRelationRemoved` | Связь удалена | `task_id`, `related_task_id`, `relation_type` |
| `TaskProgressUpdated` | Прогресс обновлён | `task_id`, `new_percent` |
| `TaskEffortUpdated` | Оценка/фактическое усилие обновлено | `task_id`, `changed_fields` |
| `TaskWatcherAdded` | Наблюдатель добавлен | `task_id`, `user_id` |
| `TaskWatcherRemoved` | Наблюдатель удалён | `task_id`, `user_id` |
| `TaskAttachmentAdded` | Вложение добавлено | `task_id`, `file_id` |
| `TaskAttachmentRemoved` | Вложение удалено | `task_id`, `file_id` |
| `TaskCustomFieldChanged` | Кастомное поле изменено | `task_id`, `field_name`, `old_value`, `new_value` |
| `TaskDeadlineApproaching` | Дедлайн приближается | `task_id`, `due_date` |
| `TaskOverdue` | Задача просрочена | `task_id`, `due_date` |
| `RecurringTaskCreated` | Повторяющаяся задача создана | `source_task_id`, `new_task_id` |
| `TaskCommentAdded` | Комментарий добавлен (opaque ID из Communication BC) | `task_id`, `comment_id` |

### Changelog Events

| Событие | Описание | Поля |
|---|---|---|
| `ChangelogEntryCreated` | Запись истории изменений создана | `task_id`, `field_name` |

### Task Template Events

| Событие | Описание | Поля |
|---|---|---|
| `TaskTemplateCreated` | Шаблон задачи создан | `template_name` |
| `TaskTemplateUpdated` | Шаблон задачи обновлён | `template_name` |
| `TaskTemplateDeleted` | Шаблон задачи удалён | `template_name` |

**Итого: 37 событий**

---

## События, на которые подписывается Task BC

### Внутренние подписки (внутри Task BC)

| Обработчик | Событие | Описание |
|---|---|---|
| `OnTaskCompletedCreateRecurring` | `TaskStatusChanged` (intra-BC) | Если задача имеет recurrence и статус сменился на «done», автоматически создаёт следующую повторяющуюся задачу. |

### Кросс-BC подписки (из Project BC)

| Обработчик | Источник (BC) | Событие | Топик | Описание |
|---|---|---|---|---|
| `OnProjectArchived` | Project BC | `ProjectArchived` | `project.events` | Архивирует все задачи проекта при архивации проекта. |
| `OnSprintCancelled` | Project BC | `SprintCancelled` | `project.events` | Убирает `sprint_id` у всех задач отменённого спринта. |
| `OnSprintCompleted` | Project BC | `SprintCompleted` | `project.events` | Убирает `sprint_id` у задач завершённого спринта. Если есть `next_sprint_id` — переносит задачи в следующий спринт, иначе убирает из спринта. |
| `OnEpicCancelled` | Project BC | `EpicStatusChanged` (status=CANCELLED) | `project.events` | Убирает `epic_id` у задач, привязанных к отменённому эпику. |
| `OnWorkflowStatusRemoved` | Project BC | `WorkflowStatusRemoved` | `project.events` | Сбрасывает `status_id` у задач с удалённым статусом на default (через `BoardPort`). Если default нет — обнуляет. |
| `OnProjectDeletionRequestedCascade` | Project BC | `ProjectDeletionRequested` | `project.events` | Мягко удаляет все задачи проекта при запросе удаления проекта. Уже удалённые задачи пропускаются. |
| `OnProjectMemberRemovedUnassign` | Project BC | `ProjectMemberRemoved` | `project.events` | Снимает назначение пользователя со всех задач проекта при удалении участника из проекта. |

**Итого: 8 подписок** (1 внутренняя + 7 кросс-BC из Project BC)
