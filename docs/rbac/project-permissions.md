# Проверки разрешений в Project Context

## Обзор механизма авторизации

Авторизация в Project Context реализована через два порта:

### 1. `ProjectPermissionCheckerPort` — внутрипроектная авторизация

Порт с двумя методами:
- **`require_permission(user_id, project_id, permission)`** — проверяет разрешение и выбрасывает `InsufficientProjectPermissionsException` при отсутствии.
- **`has_permission(user_id, project_id, permission)`** — возвращает `bool`, используется для фильтрации результатов.

Поддерживаемые wildcard-шаблоны:
- `project.*` — полный доступ в проекте (владелец)
- `<group>.*` — все разрешения в группе (`members.*`, `workflow.*`, `sprints.*`, ...)
- `<group>.<action>` — конкретное разрешение (`members.write`, `epics.read`, ...)

### Каскад ProjectRole → WorkspaceRole → OrgRole

Если у пользователя нет прямой project-роли, или она не покрывает требуемое разрешение, проверяется workspace-разрешение вида `projects.<perm>` (спец-случай: `project.*` → `ws.projects.*`). Workspace-чекер каскадирует дальше в орг-роль `workspaces.<ws-perm>`.

### 2. `WorkspacePermissionCheckerPort` — кросс-BC авторизация

Используется для операций, которые выходят за рамки одного проекта (создание проекта, управление шаблонами ретроспектив). Проверяет разрешения на уровне workspace.

---

## Commands

### Команды с кросс-BC проверкой (Workspace Permission)

| Команда | Handler | REQUIRED_PERMISSION (workspace) | Способ проверки | Дополнительные проверки |
|---|---|---|---|---|
| `CreateProjectCommand` | `CreateProjectHandler` | `projects.create` | `has_permission` (мягкая проверка, выбрасывает `InsufficientProjectPermissionsException` вручную) | Проверка существования workspace через `WorkspacePort`; проверка существования пользователя через `IdentityUserPort` |
| `CreateRetroTemplateCommand` | `CreateRetroTemplateHandler` | `projects.retro_templates.write` | `require_permission` | — |
| `DeleteRetroTemplateCommand` | `DeleteRetroTemplateHandler` | `projects.retro_templates.write` | `require_permission` | — |
| `UpdateRetroTemplateCommand` | `UpdateRetroTemplateHandler` | `projects.retro_templates.write` | `require_permission` | — |

### Команды с проверкой разрешений (Project Permission)

| Команда | Handler | REQUIRED_PERMISSION | Дополнительные проверки |
|---|---|---|---|
| `AddAutomationRuleCommand` | `AddAutomationRuleHandler` | `automations.write` | — |
| `AddBoardColumnCommand` | `AddBoardColumnHandler` | `workflow.write` | — |
| `AddBoardSwimlaneCommand` | `AddBoardSwimlaneHandler` | `workflow.write` | — |
| `AddProjectCustomFieldCommand` | `AddProjectCustomFieldHandler` | `custom_fields.write` | — |
| `AddProjectMemberCommand` | `AddProjectMemberHandler` | `members.write` | Проверка существования пользователя через `IdentityUserPort`; проверка членства в workspace через `WorkspaceMembershipPort`; проверка на дубликат |
| `AddProjectMilestoneCommand` | `AddProjectMilestoneHandler` | `milestones.write` | Проверка `methodology_capabilities.has_milestones` |
| `AddProjectOwnerCommand` | `AddProjectOwnerHandler` | `project.*` | — |
| `AddWorkflowStatusCommand` | `AddWorkflowStatusHandler` | `workflow.write` | — |
| `AddWorkflowTransitionCommand` | `AddWorkflowTransitionHandler` | `workflow.write` | — |
| `ArchiveProjectCommand` | `ArchiveProjectHandler` | `project.*` | Проверка отсутствия активных спринтов |
| `CancelSprintCommand` | `CancelSprintHandler` | `sprints.write` | — |
| `ChangeBoardColumnWipLimitCommand` | `ChangeBoardColumnWipLimitHandler` | `workflow.write` | — |
| `ChangeEpicStatusCommand` | `ChangeEpicStatusHandler` | `epics.write` | — |
| `ChangeProjectMemberRoleCommand` | `ChangeProjectMemberRoleHandler` | `members.write` | — |
| `ChangeProjectMethodologyCommand` | `ChangeProjectMethodologyHandler` | `project.settings.write` | Проверка активных спринтов перед сменой методологии |
| `ChangeProjectMilestoneStatusCommand` | `ChangeProjectMilestoneStatusHandler` | `milestones.write` | — |
| `ChangeProjectVisibilityCommand` | `ChangeProjectVisibilityHandler` | `project.settings.write` | — |
| `CompleteSprintCommand` | `CompleteSprintHandler` | `sprints.write` | — |
| `CreateEpicCommand` | `CreateEpicHandler` | `epics.write` | Проверка `methodology_capabilities.has_epics` |
| `CreateProjectRoleCommand` | `CreateProjectRoleHandler` | `roles.*` | — |
| `CreateProjectViewCommand` | `CreateProjectViewHandler` | `views.write` | — |
| `CreateSprintCommand` | `CreateSprintHandler` | `sprints.write` | Проверка `methodology_capabilities.has_sprints` |
| `CreateSprintRetroCommand` | `CreateSprintRetroHandler` | `sprints.retro.write` | — |
| `DeactivateProjectMemberCommand` | `DeactivateProjectMemberHandler` | `members.write` | Проверяется `is_owner` — влияет на логику деактивации |
| `DeleteProjectRoleCommand` | `DeleteProjectRoleHandler` | `roles.*` | — |
| `DeleteProjectViewCommand` | `DeleteProjectViewHandler` | `views.write` | — |
| `ReactivateProjectCommand` | `ReactivateProjectHandler` | `project.*` | — |
| `ReactivateProjectMemberCommand` | `ReactivateProjectMemberHandler` | `members.write` | — |
| `RemoveAutomationRuleCommand` | `RemoveAutomationRuleHandler` | `automations.write` | — |
| `UpdateAutomationRuleCommand` | `UpdateAutomationRuleHandler` | `automations.write` | — |
| `RemoveBoardColumnCommand` | `RemoveBoardColumnHandler` | `workflow.write` | — |
| `RemoveBoardSwimlaneCommand` | `RemoveBoardSwimlaneHandler` | `workflow.write` | — |
| `RemoveProjectCustomFieldCommand` | `RemoveProjectCustomFieldHandler` | `custom_fields.write` | — |
| `UpdateProjectCustomFieldCommand` | `UpdateProjectCustomFieldHandler` | `custom_fields.write` | — |
| `RemoveProjectMemberCommand` | `RemoveProjectMemberHandler` | `members.write` | Проверяется `is_owner` — влияет на логику удаления |
| `RemoveProjectOwnerCommand` | `RemoveProjectOwnerHandler` | `project.*` | Домен гарантирует, что минимум один владелец останется |
| `RemoveWorkflowStatusCommand` | `RemoveWorkflowStatusHandler` | `workflow.write` | — |
| `RemoveWorkflowTransitionCommand` | `RemoveWorkflowTransitionHandler` | `workflow.write` | — |
| `ReorderBoardColumnsCommand` | `ReorderBoardColumnsHandler` | `workflow.write` | — |
| `RequestProjectDeletionCommand` | `RequestProjectDeletionHandler` | `project.*` | — |
| `RestoreProjectCommand` | `RestoreProjectHandler` | `project.*` | — |
| `StartSprintCommand` | `StartSprintHandler` | `sprints.write` | — |
| `SuspendProjectCommand` | `SuspendProjectHandler` | `project.*` | — |
| `TransferProjectOwnershipCommand` | `TransferProjectOwnershipHandler` | `project.*` | — |
| `UpdateEpicCommand` | `UpdateEpicHandler` | `epics.write` | — |
| `UpdateProjectInfoCommand` | `UpdateProjectInfoHandler` | `project.settings.write` | — |
| `UpdateProjectMilestoneCommand` | `UpdateProjectMilestoneHandler` | `milestones.write` | — |
| `UpdateProjectRoleCommand` | `UpdateProjectRoleHandler` | `roles.*` | — |
| `UpdateProjectViewCommand` | `UpdateProjectViewHandler` | `views.write` | — |
| `UpdateSprintDateRangeCommand` | `UpdateSprintDateRangeHandler` | `sprints.write` | — |
| `UpdateSprintGoalCommand` | `UpdateSprintGoalHandler` | `sprints.write` | — |

---

## Queries

### Запросы без проверки разрешений

| Запрос | Handler | Описание |
|---|---|---|
| `GetRetroTemplatesQuery` | `GetRetroTemplatesHandler` | Получение системных шаблонов ретроспектив. Доступно без авторизации — системные шаблоны общедоступны. |

### Запросы с `require_permission`

| Запрос | Handler | REQUIRED_PERMISSION | Дополнительные проверки |
|---|---|---|---|
| `GetActiveSprintQuery` | `GetActiveSprintHandler` | `sprints.read` | — |
| `GetBoardQuery` | `GetBoardHandler` | `project.read` | — |
| `GetEpicQuery` | `GetEpicHandler` | `epics.read` | — |
| `GetEpicsByProjectQuery` | `GetEpicsByProjectHandler` | `epics.read` | — |
| `GetProjectQuery` | `GetProjectHandler` | `project.read` | — |
| `GetProjectMemberQuery` | `GetProjectMemberHandler` | `members.read` | — |
| `GetProjectMembersQuery` | `GetProjectMembersHandler` | `members.read` | — |
| `GetProjectRoleQuery` | `GetProjectRoleHandler` | `roles.read` | — |
| `GetProjectRolesQuery` | `GetProjectRolesHandler` | `roles.read` | — |
| `GetSprintQuery` | `GetSprintHandler` | `sprints.read` | — |
| `GetSprintsByProjectQuery` | `GetSprintsByProjectHandler` | `sprints.read` | — |

### Запросы с `has_permission` (фильтрация)

| Запрос | Handler | Проверяемое разрешение | Описание |
|---|---|---|---|
| `GetArchivedProjectsQuery` | `GetArchivedProjectsHandler` | `project.read` | Возвращает архивированные проекты workspace, отфильтрованные по наличию `project.read` у `caller_id`. Используется `has_permission`. |
| `GetProjectsByMemberQuery` | `GetProjectsByMemberHandler` | `project.read` | Возвращает проекты участника, отфильтрованные по наличию `project.read` у `caller_id`. Используется `has_permission`. |
| `GetProjectsByMethodologyQuery` | `GetProjectsByMethodologyHandler` | `project.read` | Возвращает проекты по методологии, отфильтрованные по наличию `project.read` у `caller_id`. Используется `has_permission`. |
| `GetProjectsByWorkspaceQuery` | `GetProjectsByWorkspaceHandler` | `project.read` | Возвращает проекты workspace, отфильтрованные по наличию `project.read` у `caller_id`. Используется `has_permission`. |
| `SearchProjectsQuery` | `SearchProjectsHandler` | `project.read` | Глобальный поиск проектов с фильтрацией по наличию `project.read` у `caller_id`. Используется `has_permission`. |

---

## Сводная таблица разрешений

### Project-разрешения

| Разрешение | Commands | Queries |
|---|---|---|
| `project.*` | `AddProjectOwner`, `ArchiveProject`, `ReactivateProject`, `RemoveProjectOwner`, `RequestProjectDeletion`, `RestoreProject`, `SuspendProject`, `TransferProjectOwnership` | — |
| `project.settings.write` | `ChangeProjectMethodology`, `ChangeProjectVisibility`, `UpdateProjectInfo` | — |
| `project.read` | — | `GetProject`, `GetBoard`, `GetArchivedProjects`*, `GetProjectsByMember`*, `GetProjectsByMethodology`*, `GetProjectsByWorkspace`*, `SearchProjects`* |
| `members.write` | `AddProjectMember`, `ChangeProjectMemberRole`, `DeactivateProjectMember`, `ReactivateProjectMember`, `RemoveProjectMember` | — |
| `members.read` | — | `GetProjectMember`, `GetProjectMembers` |
| `roles.*` | `CreateProjectRole`, `DeleteProjectRole`, `UpdateProjectRole` | — |
| `roles.read` | — | `GetProjectRole`, `GetProjectRoles` |
| `workflow.write` | `AddBoardColumn`, `AddBoardSwimlane`, `AddWorkflowStatus`, `AddWorkflowTransition`, `ChangeBoardColumnWipLimit`, `RemoveBoardColumn`, `RemoveBoardSwimlane`, `RemoveWorkflowStatus`, `RemoveWorkflowTransition`, `ReorderBoardColumns` | — |
| `sprints.write` | `CancelSprint`, `CompleteSprint`, `CreateSprint`, `StartSprint`, `UpdateSprintDateRange`, `UpdateSprintGoal` | — |
| `sprints.read` | — | `GetActiveSprint`, `GetSprint`, `GetSprintsByProject` |
| `sprints.retro.write` | `CreateSprintRetro` | — |
| `epics.write` | `ChangeEpicStatus`, `CreateEpic`, `UpdateEpic` | — |
| `epics.read` | — | `GetEpic`, `GetEpicsByProject` |
| `milestones.write` | `AddProjectMilestone`, `ChangeProjectMilestoneStatus`, `UpdateProjectMilestone` | — |
| `views.write` | `CreateProjectView`, `DeleteProjectView`, `UpdateProjectView` | — |
| `automations.write` | `AddAutomationRule`, `RemoveAutomationRule`, `UpdateAutomationRule` | — |
| `custom_fields.write` | `AddProjectCustomField`, `RemoveProjectCustomField`, `UpdateProjectCustomField` | — |
| Без проверки | — | `GetRetroTemplates` |

### Кросс-BC (Workspace) разрешения

| Разрешение | Commands | Queries |
|---|---|---|
| `projects.create` | `CreateProject`‡ | — |
| `projects.retro_templates.write` | `CreateRetroTemplate`, `DeleteRetroTemplate`, `UpdateRetroTemplate` | — |

\* — используют `has_permission` для фильтрации, а не `require_permission`
‡ — проверяется через `WorkspacePermissionCheckerPort.has_permission` + выбрасывает `InsufficientProjectPermissionsException` вручную

---

## Особенности Project BC

### Зависимость от методологии

Некоторые операции зависят от `methodology_capabilities` проекта:
- **`has_sprints`** → `CreateSprint`, `StartSprint`, `CancelSprint`, `CompleteSprint`
- **`has_epics`** → `CreateEpic`, `ChangeEpicStatus`, `UpdateEpic`
- **`has_milestones`** → `AddProjectMilestone`, `ChangeProjectMilestoneStatus`, `UpdateProjectMilestone`
- **`has_retros`** → `CreateSprintRetro`

При отсутствии capability выбрасывается соответствующее исключение (`SprintCapabilityNotAvailableException`, `EpicCapabilityNotAvailableException`).

### Двойная проверка при работе с участниками

Команды `DeactivateProjectMember` и `RemoveProjectMember` проверяют `is_owner` через агрегат `Project`, что влияет на логику удаления/деактивации в `ProjectMembership`.

### Кросс-BC интеграции

- **`IdentityUserPort`** — проверка существования пользователя перед добавлением в проект (`AddProjectMember`, `CreateProject`).
- **`WorkspaceMembershipPort`** — проверка членства в workspace перед добавлением в проект (`AddProjectMember`).
- **`WorkspacePort`** — проверка существования workspace при создании проекта (`CreateProject`).
- **`WorkspacePermissionCheckerPort`** — авторизация на уровне workspace для кросс-BC операций.
