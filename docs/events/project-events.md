# События Project BC

## События, которые отдаёт Project BC

### Project Events

| Событие | Описание | Поля |
|---|---|---|
| `ProjectCreated` | Проект создан | `project_id`, `workspace_id`, `name`, `methodology` |
| `ProjectInfoChanged` | Информация проекта обновлена | `project_id`, `changed_fields` |
| `ProjectArchived` | Проект архивирован | `project_id` |
| `ProjectRestored` | Проект восстановлен | `project_id` |
| `ProjectSuspended` | Проект приостановлен | `project_id`, `reason` |
| `ProjectReactivated` | Проект реактивирован | `project_id` |
| `ProjectDeletionRequested` | Запрос удаления проекта | `project_id` |
| `MethodologyChanged` | Методология изменена | `project_id`, `old_methodology`, `new_methodology` |
| `ProjectVisibilityChanged` | Видимость проекта изменена | `project_id`, `new_visibility` |
| `MilestoneCreated` | Milestone создан | `project_id`, `milestone_id` |
| `MilestoneUpdated` | Milestone обновлён | `project_id`, `milestone_id`, `changed_fields` |
| `MilestoneStatusChanged` | Статус milestone изменён | `project_id`, `milestone_id`, `new_status` |
| `ProjectDeadlineApproaching` | Приближение дедлайна проекта | `project_id`, `deadline` |

### Project Membership Events

| Событие | Описание | Поля |
|---|---|---|
| `ProjectMemberJoined` | Участник добавлен в проект | `project_id`, `user_id`, `role_id` |
| `ProjectMemberRemoved` | Участник удалён из проекта | `project_id`, `user_id` |
| `ProjectMemberRoleChanged` | Роль участника проекта изменена | `project_id`, `user_id`, `new_role_id` |

### Project Role Events

| Событие | Описание | Поля |
|---|---|---|
| `ProjectRoleCreated` | Кастомная роль проекта создана | `project_id`, `role_name` |
| `ProjectRoleUpdated` | Роль проекта обновлена | `project_id`, `role_name` |
| `ProjectRoleDeleted` | Кастомная роль проекта удалена | `project_id`, `role_name` |

### Board Events

| Событие | Описание | Поля |
|---|---|---|
| `BoardColumnAdded` | Колонка добавлена | `project_id`, `column_id`, `name` |
| `BoardColumnRemoved` | Колонка удалена | `project_id`, `column_id` |
| `BoardColumnReordered` | Колонки переупорядочены | `project_id` |
| `WIPLimitChanged` | WIP-лимит изменён | `project_id`, `column_id` |
| `SwimlaneAdded` | Swimlane добавлена | `project_id`, `swimlane_id` |
| `SwimlaneRemoved` | Swimlane удалена | `project_id`, `swimlane_id` |
| `WorkflowStatusAdded` | Статус workflow добавлен | `project_id`, `status_id`, `name`, `category` |
| `WorkflowStatusRemoved` | Статус workflow удалён | `project_id`, `status_id` |
| `WorkflowTransitionAdded` | Переход workflow добавлен | `project_id`, `transition_id` |
| `WorkflowTransitionRemoved` | Переход workflow удалён | `project_id`, `transition_id` |
| `ProjectViewCreated` | Представление создано | `project_id`, `view_id` |
| `ProjectViewUpdated` | Представление обновлено | `project_id`, `view_id` |
| `ProjectViewDeleted` | Представление удалено | `project_id`, `view_id` |
| `AutomationRuleCreated` | Правило автоматизации создано | `project_id`, `rule_id` |
| `AutomationRuleUpdated` | Правило автоматизации обновлено | `project_id`, `rule_id` |
| `AutomationRuleDeleted` | Правило автоматизации удалено | `project_id`, `rule_id` |
| `AutomationRuleTriggered` | Правило автоматизации сработало | `project_id`, `rule_id`, `trigger_data` |

### Sprint Events

| Событие | Описание | Поля |
|---|---|---|
| `SprintCreated` | Спринт создан | `sprint_id`, `project_id`, `name` |
| `SprintStarted` | Спринт запущен | `sprint_id` |
| `SprintCompleted` | Спринт завершён | `sprint_id` |
| `SprintCancelled` | Спринт отменён | `sprint_id` |
| `SprintGoalUpdated` | Цель спринта обновлена | `sprint_id` |
| `SprintRetroCreated` | Ретроспектива создана | `sprint_id`, `template_name` |
| `TasksMovedToNextSprint` | Незавершённые задачи перемещены в следующий спринт | `sprint_id`, `task_ids` |
| `TasksMovedToBacklog` | Незавершённые задачи перемещены в бэклог | `sprint_id`, `task_ids` |

### Epic Events

| Событие | Описание | Поля |
|---|---|---|
| `EpicCreated` | Эпик создан | `project_id`, `epic_id` |
| `EpicUpdated` | Эпик обновлён | `project_id`, `epic_id`, `changed_fields` |
| `EpicStatusChanged` | Статус эпика изменён | `project_id`, `epic_id`, `new_status` |

### Retro Template Events

| Событие | Описание | Поля |
|---|---|---|
| `RetroTemplateCreated` | Шаблон ретроспективы создан | `template_name` |
| `RetroTemplateUpdated` | Шаблон ретроспективы обновлён | `template_name` |
| `RetroTemplateDeleted` | Шаблон ретроспективы удалён | `template_name` |

**Итого: 47 событий**

---

## События, на которые подписывается Project BC

### Внутренние подписки (внутри Project BC)

| Обработчик | Событие | Топик | Описание |
|---|---|---|---|
| `OnAutomationRuleTriggered` | Любое событие с `project_id` | `project.events` | Проверяет, совпадает ли триггер automation rule с событием. Если правило включено и триггер совпадает — логирует срабатывание. |

### Кросс-BC подписки

| Обработчик | Источник (BC) | Событие | Топик | Описание |
|---|---|---|---|---|
| `OnWorkspaceMemberRemoved` | Workspace BC | `WorkspaceMemberRemoved` | `workspace.events` | Удаляет участника из всех проектов workspace при его удалении из workspace. Владельцы проектов пропускаются (не удаляются). |
| `OnWorkspaceArchivedCascade` | Workspace BC | `WorkspaceArchived` | `workspace.events` | Архивирует все проекты workspace при архивации workspace. Уже архивированные проекты пропускаются. |
| `OnWorkspaceDeletionRequestedCascade` | Workspace BC | `WorkspaceDeletionRequested` | `workspace.events` | Мягко удаляет все проекты workspace при запросе удаления workspace. Уже помеченные на удаление пропускаются. |
| `OnWorkspaceMemberRemovedCascade` | Workspace BC | `WorkspaceMemberRemoved` | `workspace.events` | Каскадное удаление участника из всех проектов workspace (dict-based обработчик). Владельцы проектов пропускаются. |
| `OnWorkspaceRestoredCascade` | Workspace BC | `WorkspaceRestored` | `workspace.events` | Восстанавливает все архивированные проекты workspace при восстановлении workspace. Не архивированные проекты пропускаются. |

**Итого: 6 подписок** (1 внутренняя + 5 кросс-BC из Workspace BC)
