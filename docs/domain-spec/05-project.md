# Project BC — Спецификация

> Путь: `app/context/project/domain`
> Исходные требования: §5 (Проекты)

## Контекст

Project BC отвечает за проекты, методологии, спринты, доски, workflow, представления, эпики, milestones, автоматизации и роли на уровне проекта.

---

## Принципы расширяемости

1. **Роли — entity, не enum** — `ProjectRole` хранится как запись с permissions. Кастомные роли без изменения домена.
2. **Разделение AR** — Project (ядро) + Board (доска) + Sprint (спринты) + ProjectMembership (члены). Каждый AR развивается независимо.
3. **Методология — enum + capabilities** — `Methodology` определяет доступный функционал через `MethodologyCapabilities`. Новая методология = новое значение enum + capabilities.
4. **Workflow — entity, не захардкоженные статусы** — произвольные статусы и переходы. Новые статусы = новая запись, не правка домена.
5. **Типизация** — `SwimlaneGroupBy`, `ViewType`, `CustomFieldType` enum вместо магических строк и dict.
6. **Events по группам** — `changed_fields` для детализации.

---

## Value Objects

### Общие

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `ProjectStatus` | Enum | `ACTIVE`, `ARCHIVED`, `SUSPENDED`, `PENDING_DELETION` | §5.3 |
| `ProjectVisibility` | Enum | `PRIVATE`, `WORKSPACE`, `ORGANIZATION`, `PUBLIC` | §5.3 |
| `Methodology` | Enum | `KANBAN`, `SCRUM`, `WATERFALL`, `HYBRID`, `SHAPE_UP` | §5.4 |
| `WIPLimit` | frozen dataclass | value: int (≥1) | §5.4.2 |
| `SprintStatus` | Enum | `PLANNING`, `ACTIVE`, `COMPLETED`, `CANCELLED` | §5.4.1 |
| `SprintGoal` | frozen dataclass | value: str | §5.4.1 |
| `MilestoneStatus` | Enum | `NOT_STARTED`, `IN_PROGRESS`, `COMPLETED`, `OVERDUE` | §5.4 |
| `ViewType` | Enum | `BOARD`, `LIST`, `TIMELINE`, `CALENDAR`, `TABLE`, `ACTIVITY` | §5.5 |
| `SwimlaneGroupBy` | Enum | `ASSIGNEE`, `PRIORITY`, `LABEL`, `EPIC`, `CUSTOM_FIELD` | §5.4.2 |
| `CustomFieldType` | Enum | `TEXT`, `NUMBER`, `DATE`, `SELECT`, `MULTI_SELECT`, `URL`, `USER`, `CHECKBOX` | — |
| `AutomationTrigger` | Enum | `STATUS_CHANGED`, `ASSIGNEE_CHANGED`, `DUE_DATE_APPROACHING`, `PRIORITY_CHANGED`, `LABEL_ADDED`, `COMMENT_ADDED` | — |
| `AutomationAction` | Enum | `ASSIGN_USER`, `CHANGE_STATUS`, `ADD_LABEL`, `SET_DUE_DATE`, `SEND_NOTIFICATION`, `MOVE_TO_SPRINT` | — |
| `AccentColor` | frozen dataclass | hex: str (validated #RRGGBB) | §5.3 |
| `RichText` | frozen dataclass | content: str, format: RichTextFormat | §5.3, §6.2 |
| `RichTextFormat` | Enum | `MARKDOWN`, `WYSIWYG` | §5.3 |
| `DateRange` | frozen dataclass | start: date, end: date (start ≤ end) | §5.4.1 |
| `Category` | frozen dataclass | name: str, color: AccentColor \| None | §5.3 |

> **`Methodology`** — добавление новой методологии (SAFe, Lean, OKR-driven) = новое значение enum + определение `MethodologyCapabilities`. Не ломает существующие проекты.
>
> **`ProjectVisibility`** — `WORKSPACE` = видно участникам workspace, `ORGANIZATION` = видно участникам организации, `PUBLIC` = видно всем. Расширяемо.
>
> **`SwimlaneGroupBy`** — `CUSTOM_FIELD` позволяет группировать по любому кастомному полю. Новые способы группировки = новое значение enum.
>
> **`AutomationTrigger`/`AutomationAction`** — будут расти. Новые триггеры/действия = новое значение enum + обработчик на app-слое.

### MethodologyCapabilities (VO group)

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `MethodologyCapabilities` | frozen dataclass | has_sprints: bool, has_backlog: bool, has_milestones: bool, has_epics: bool, has_wip_limits: bool, has_velocity: bool, has_retros: bool, has_burndown: bool | §5.4 |

> Предустановленные capabilities:

| Methodology | has_sprints | has_backlog | has_milestones | has_epics | has_wip_limits | has_velocity | has_retros | has_burndown |
|---|---|---|---|---|---|---|---|---|
| `KANBAN` | No | No | Yes | Yes | Yes | No | No | No |
| `SCRUM` | Yes | Yes | No | Yes | No | Yes | Yes | Yes |
| `WATERFALL` | No | No | Yes | Yes | No | No | No | No |
| `HYBRID` | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| `SHAPE_UP` | No | Yes | Yes | Yes | No | No | Yes | No |

> **Новая методология** — добавить значение в `Methodology` + определить capabilities. UI проверяет capabilities для отображения/скрытия функций.

### CardAppearance (VO group)

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `CardAppearance` | frozen dataclass | visible_fields: list[str], compact_mode: bool, show_cover_image: bool | §5.4.2 |

> **`visible_fields`** — список имён полей для отображения на карточке. Новое поле = добавить в список, без правки VO-структуры. Предустановленные наборы: minimal, standard, detailed.

### ProjectViewConfig (VO group)

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `ProjectViewConfig` | frozen dataclass | view_type: ViewType, filters: list[ViewFilter], sorting: list[SortRule], grouping: str \| None, card_appearance: CardAppearance \| None, column_settings: dict[str, str] \| None | §5.5 |
| `ViewFilter` | frozen dataclass | field: str, operator: FilterOperator, value: str | §5.5 |
| `SortRule` | frozen dataclass | field: str, direction: SortDirection | §5.5 |
| `FilterOperator` | Enum | `EQ`, `NEQ`, `IN`, `NOT_IN`, `CONTAINS`, `GT`, `LT`, `GTE`, `LTE`, `IS_EMPTY`, `IS_NOT_EMPTY` | §5.5 |
| `SortDirection` | Enum | `ASC`, `DESC` | §5.5 |

> **`ProjectViewConfig`** — типизированная замена `config: dict`. Новые параметры отображения = поля в VO, не нетипизированный dict.

### CustomFieldDefinition (VO group)

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `CustomFieldDefinition` | frozen dataclass | name: str, field_type: CustomFieldType, is_required: bool, options: list[str] \| None (для SELECT/MULTI_SELECT), default_value: str \| None, description: str \| None | — |

> **Кастомные поля** — определяются на уровне проекта. Значения хранятся на задачах (Task BC) как `dict[str, str]`. Новые типы полей = значение в `CustomFieldType`.

## Entities

| Сущность | Поля | Описание | Исходное требование |
|---|---|---|---|
| `ProjectMember` | user_id: Id, role: ProjectRole (entity ref), joined_at: datetime, is_active: bool | Участник проекта | §5.2 |
| `ProjectRole` | name: str, permissions: list[str], is_system: bool, description: str \| None | Роль проекта (системная или кастомная) | §5.7 |
| `BoardColumn` | name: str, order: int, color: AccentColor \| None, wip_limit: WIPLimit \| None, status_mapping: Id \| None (связь с WorkflowStatus) | Колонка доски | §5.4, §5.4.2 |
| `Swimlane` | name: str, order: int, group_by: SwimlaneGroupBy, group_value: str \| None | Swimlane на доске | §5.4.2 |
| `WorkflowStatus` | name: str, color: AccentColor \| None, icon: str \| None, order: int, is_default: bool, category: WorkflowStatusCategory | Кастомный статус задачи | §5.5 |
| `WorkflowTransition` | from_status_id: Id, to_status_id: Id, name: str, trigger: AutomationTrigger \| None, required_permission: str \| None | Переход между статусами | §5.5 |
| `ProjectView` | name: str, config: ProjectViewConfig, is_default: bool, is_shared: bool, owner_id: Id \| None | Представление проекта | §5.5 |
| `Epic` | name: str, description: RichText \| None, status: EpicStatus, start_date: date \| None, due_date: date \| None, owner_id: Id \| None, color: AccentColor \| None | Эпик/фича проекта | §5.4 |
| `Milestone` | name: str, description: RichText \| None, status: MilestoneStatus, due_date: date, completed_at: datetime \| None | Milestone проекта | §5.4 |
| `AutomationRule` | name: str, trigger: AutomationTrigger, action: AutomationAction, action_params: dict[str, str], is_enabled: bool | Правило автоматизации | — |
| `RetroTemplate` | name: str, sections: list[RetroSection] | Шаблон ретроспективы | §5.4.1 |
| `RetroSection` | title: str, prompt: str \| None, item_type: RetroItemType | Секция ретроспективы | §5.4.1 |
| `RetroItemType` | Enum | `POSITIVE`, `NEGATIVE`, `NEUTRAL`, `ACTION_ITEM` | §5.4.1 |

> **`WorkflowStatusCategory`** — enum: `TODO`, `IN_PROGRESS`, `DONE`, `CANCELLED`. Группирует произвольные статусы в агрегированные категории для аналитики и фильтрации. Новые категории (например, `BLOCKED`, `REVIEW`) = значение enum.

> **`BoardColumn.status_mapping`** — связь колонки доски с workflow status. Колонка — визуальное представление, status — логическое состояние. Одна колонка может отображать несколько статусов (фильтр по category).

> **`Epic`** — группировка задач выше уровня спринта. Доступен когда `MethodologyCapabilities.has_epics=True`.

> **`AutomationRule`** — "при переходе в статус X → назначить пользователя Y". Расширяемо через новые `AutomationTrigger` и `AutomationAction`.

> **`RetroTemplate`** — гибкие шаблоны ретроспектив. Предустановленные: "What went well / Improve / Actions", "4Ls (Liked/Learned/Lacked/Longed for)", "Start/Stop/Continue". Новые шаблоны = новая запись.

### EpicStatus Enum

| Значение | Описание |
|---|---|
| `OPEN` | Эпик открыт |
| `IN_PROGRESS` | В работе |
| `DONE` | Завершён |
| `CANCELLED` | Отменён |

### WorkflowStatusCategory Enum

| Значение | Описание |
|---|---|
| `TODO` | К выполнению |
| `IN_PROGRESS` | В работе |
| `DONE` | Выполнено |
| `CANCELLED` | Отменено |
| `BLOCKED` | Заблокировано |
| `REVIEW` | На ревью |

## Domain Events

| Событие | Поля | Описание | Исходное требование |
|---|---|---|---|
| `ProjectCreated` | project_id, workspace_id, name, methodology | Проект создан | §5.1 |
| `ProjectInfoChanged` | project_id, changed_fields: list[str] | Информация обновлена | §5.1 |
| `ProjectArchived` | project_id | Проект архивирован | §5.1 |
| `ProjectRestored` | project_id | Проект восстановлен | §5.1 |
| `ProjectSuspended` | project_id, reason | Проект приостановлен | §5.1 |
| `ProjectReactivated` | project_id | Проект реактивирован | §5.1 |
| `ProjectDeletionRequested` | project_id | Запрос удаления проекта | §5.1 |
| `MethodologyChanged` | project_id, old_methodology, new_methodology | Методология изменена | §5.4 |
| `ProjectVisibilityChanged` | project_id, new_visibility | Видимость изменена | §5.3 |
| `ProjectMemberJoined` | project_id, user_id, role | Участник добавлен | §5.2 |
| `ProjectMemberRemoved` | project_id, user_id | Участник удалён | §5.2 |
| `ProjectMemberRoleChanged` | project_id, user_id, new_role | Роль изменена | §5.2 |
| `ProjectRoleCreated` | project_id, role_name | Кастомная роль создана | §5.7 |
| `ProjectRoleUpdated` | project_id, role_name | Роль обновлена | §5.7 |
| `ProjectRoleDeleted` | project_id, role_name | Кастомная роль удалена | §5.7 |
| `BoardColumnAdded` | project_id, column_id, name | Колонка добавлена | §5.4 |
| `BoardColumnRemoved` | project_id, column_id | Колонка удалена | §5.4 |
| `BoardColumnReordered` | project_id | Колонки переупорядочены | §5.4 |
| `WIPLimitChanged` | project_id, column_id | WIP-лимит изменён | §5.4.2 |
| `SwimlaneAdded` | project_id, swimlane_id | Swimlane добавлена | §5.4.2 |
| `SwimlaneRemoved` | project_id, swimlane_id | Swimlane удалена | §5.4.2 |
| `WorkflowStatusAdded` | project_id, status_id, name, category | Статус добавлен | §5.5 |
| `WorkflowStatusRemoved` | project_id, status_id | Статус удалён | §5.5 |
| `WorkflowTransitionAdded` | project_id, transition_id | Переход добавлен | §5.5 |
| `WorkflowTransitionRemoved` | project_id, transition_id | Переход удалён | §5.5 |
| `ProjectViewCreated` | project_id, view_id | Представление создано | §5.5 |
| `ProjectViewUpdated` | project_id, view_id | Представление обновлено | §5.5 |
| `ProjectViewDeleted` | project_id, view_id | Представление удалено | §5.5 |
| `EpicCreated` | project_id, epic_id | Эпик создан | §5.4 |
| `EpicUpdated` | project_id, epic_id, changed_fields: list[str] | Эпик обновлён | §5.4 |
| `EpicStatusChanged` | project_id, epic_id, new_status | Статус эпика изменён | §5.4 |
| `MilestoneCreated` | project_id, milestone_id | Milestone создан | §5.4 |
| `MilestoneUpdated` | project_id, milestone_id, changed_fields: list[str] | Milestone обновлён | §5.4 |
| `MilestoneStatusChanged` | project_id, milestone_id, new_status | Статус milestone изменён | §5.4 |
| `CustomFieldDefinitionAdded` | project_id, field_name, field_type | Кастомное поле добавлено | — |
| `CustomFieldDefinitionUpdated` | project_id, field_name | Кастомное поле обновлено | — |
| `CustomFieldDefinitionRemoved` | project_id, field_name | Кастомное поле удалено | — |
| `AutomationRuleCreated` | project_id, rule_id | Правило автоматизации создано | — |
| `AutomationRuleUpdated` | project_id, rule_id | Правило обновлено | — |
| `AutomationRuleDeleted` | project_id, rule_id | Правило удалено | — |
| `AutomationRuleTriggered` | project_id, rule_id, trigger_data: dict | Правило сработало | — |
| `SprintCreated` | sprint_id, project_id, name | Спринт создан | §5.4.1 |
| `SprintStarted` | sprint_id | Спринт запущен | §5.4.1 |
| `SprintCompleted` | sprint_id | Спринт завершён | §5.4.1 |
| `SprintCancelled` | sprint_id | Спринт отменён | §5.4.1 |
| `SprintGoalUpdated` | sprint_id | Цель спринта обновлена | §5.4.1 |
| `SprintRetroCreated` | sprint_id, template_name | Ретроспектива создана | §5.4.1 |
| `TasksMovedToNextSprint` | sprint_id, task_ids | Незавершённые задачи → следующий спринт | §5.4.1 |
| `TasksMovedToBacklog` | sprint_id, task_ids | Незавершённые задачи → бэклог | §5.4.1 |

## Exceptions

| Исключение | Описание |
|---|---|
| `ProjectNotFoundException` | Проект не найден |
| `ProjectSuspendedException` | Проект приостановлен |
| `ProjectArchivedException` | Проект архивирован, действие невозможно |
| `ProjectMemberNotFoundException` | Участник проекта не найден |
| `ProjectRoleNotFoundException` | Роль не найдена |
| `ProjectRoleInUseException` | Роль используется, нельзя удалить |
| `CannotRemoveOwnerException` | Нельзя удалить владельца |
| `CannotRemoveLastOwnerException` | Нельзя удалить последнего владельца |
| `BoardColumnNotFoundException` | Колонка не найдена |
| `SwimlaneNotFoundException` | Swimlane не найдена |
| `WorkflowStatusNotFoundException` | Статус не найден |
| `WorkflowTransitionNotAllowedException` | Переход не разрешён |
| `CircularTransitionException` | Циклический переход |
| `WIPLimitExceededException` | WIP-лимит превышен |
| `SprintNotFoundException` | Спринт не найден |
| `SprintAlreadyStartedException` | Спринт уже запущен |
| `SprintNotStartedException` | Спринт не запущен |
| `CannotCompleteSprintWithOpenTasksException` | Нельзя завершить спринт с открытыми задачами |
| `EpicNotFoundException` | Эпик не найден |
| `MilestoneNotFoundException` | Milestone не найден |
| `MilestoneOverdueException` | Milestone просрочен |
| `CustomFieldDefinitionNotFoundException` | Определение кастомного поля не найдено |
| `DuplicateCustomFieldException` | Кастомное поле с таким именем уже существует |
| `AutomationRuleNotFoundException` | Правило автоматизации не найдено |
| `MethodologyCapabilityNotAvailableException` | Функция не доступна для текущей методологии |
| `CannotChangeMethodologyWithActiveSprintsException` | Нельзя сменить методологию с активными спринтами |

## Aggregates

### Project (Aggregate Root)

Ядро проекта — идентичность, статус, методология, владельцы, политики. Не содержит доски/спринты (это отдельные AR).

Поля:
- workspace_id: Id (opaque, из Workspace BC)
- name: str
- description: RichText | None
- icon: str | None
- color: AccentColor | None
- category: Category | None
- methodology: Methodology
- methodology_capabilities: MethodologyCapabilities
- visibility: ProjectVisibility
- status: ProjectStatus
- owner_ids: list[Id] — один или несколько владельцев
- start_date: date | None
- deadline: date | None
- custom_field_definitions: list[CustomFieldDefinition]
- created_at: datetime
- updated_at: datetime

Методы:
- `create(name, workspace_id, owner_id, methodology)` → `Project` (factory, capabilities = предустановленные для методологии)
- `update_info(name=None, description=None, icon=None, color=None, category=None, start_date=None, deadline=None)`
- `archive()` — только если нет активных спринтов
- `restore()`
- `suspend(reason)`
- `reactivate()`
- `request_deletion()`
- `change_methodology(new_methodology)` — только если нет активных спринтов
- `change_visibility(visibility)`
- `transfer_ownership(from_id, to_id)`
- `add_owner(user_id)` — со-владелец
- `remove_owner(user_id)` — минимум один владелец
- `add_custom_field(definition: CustomFieldDefinition)`
- `update_custom_field(name, definition)`
- `remove_custom_field(name)`
- `create_role(name, permissions, description=None)` — кастомная роль
- `update_role(name, permissions=None, description=None)`
- `delete_role(name)` — только кастомные

Инварианты:
- Минимум один владелец
- `ProjectStatus.ARCHIVED` блокирует все действия кроме `restore`
- `ProjectStatus.SUSPENDED` блокирует все действия кроме `reactivate`
- Нельзя удалить системную роль (`is_system=True`)
- Нельзя удалить роль если она используется участниками
- При смене методологии — capabilities обновляются на предустановленные
- Имена кастомных полей уникальны в рамках проекта
- Нельзя сменить методологию если есть активные спринты

### ProjectMembership (Aggregate Root)

Управление участниками проекта. Отдельный AR для масштабируемости.

Поля:
- project_id: Id (opaque)
- members: list[ProjectMember]

Методы:
- `create(project_id, owner_id)` → `ProjectMembership` (factory)
- `add_member(user_id, role, invited_by=None)`
- `remove_member(user_id)`
- `deactivate_member(user_id)`
- `reactivate_member(user_id)`
- `change_member_role(user_id, new_role)`

Инварианты:
- Владелец не может быть удалён — сначала снять роль
- Участник должен быть членом workspace (проверка на app-слое через ACL)
- Для `ProjectVisibility.PRIVATE` — только участники видят проект
- Для `ProjectVisibility.WORKSPACE` — все члены workspace видят, но редактируют только участники

### Board (Aggregate Root)

Доска проекта — колонки, swimlanes, workflow, views, автоматизации. Отдельный AR.

Поля:
- project_id: Id (opaque)
- columns: list[BoardColumn]
- swimlanes: list[Swimlane]
- workflow_statuses: list[WorkflowStatus]
- workflow_transitions: list[WorkflowTransition]
- views: list[ProjectView]
- automation_rules: list[AutomationRule]
- created_at: datetime
- updated_at: datetime

Методы:
- `create(project_id, methodology)` → `Board` (factory, default columns/statuses based on methodology)
- `add_column(name, color=None, wip_limit=None, status_mapping=None)`
- `remove_column(column_id)`
- `reorder_columns(column_ids)`
- `change_wip_limit(column_id, wip_limit)`
- `add_swimlane(name, group_by, group_value=None)`
- `remove_swimlane(swimlane_id)`
- `add_workflow_status(name, color=None, icon=None, category, is_default=False)`
- `remove_workflow_status(status_id)` — нельзя если есть задачи в этом статусе (проверка на app-слое)
- `add_workflow_transition(from_status_id, to_status_id, name, required_permission=None)`
- `remove_workflow_transition(transition_id)`
- `create_view(name, config: ProjectViewConfig, is_shared=True)`
- `update_view(view_id, config=None, name=None)`
- `delete_view(view_id)`
- `add_automation_rule(name, trigger, action, action_params)`
- `update_automation_rule(rule_id, is_enabled=None, action_params=None)`
- `remove_automation_rule(rule_id)`

Инварианты:
- WIP-лимит ≥ 1
- Workflow transition: from_status_id ≠ to_status_id
- Хотя бы один `is_default=True` workflow status
- Хотя бы одна колонка
- `MethodologyCapabilities.has_wip_limits=False` → WIP-лимиты игнорируются (но не запрещаются)
- `AutomationRule` срабатывает на app-слое при соответствующем event

### Sprint (Aggregate Root)

Спринт — самостоятельный AR. Связан с проектом через `project_id`.

Поля:
- project_id: Id (opaque)
- name: str
- goal: SprintGoal | None
- status: SprintStatus
- date_range: DateRange | None
- retro: SprintRetro | None
- created_at: datetime
- updated_at: datetime

Методы:
- `create(name, project_id, goal=None, date_range=None)` → `Sprint` (factory)
- `start()`
- `complete(incomplete_task_ids, next_sprint_id=None)` — незавершённые задачи перемещаются
- `cancel()`
- `update_goal(goal)`
- `update_date_range(date_range)`
- `create_retro(template: RetroTemplate)` → SprintRetro

Инварианты:
- Спринт можно запустить только из PLANNING
- Завершить можно только из ACTIVE
- Незавершённые задачи → следующий спринт или бэклог (определяется на app-слое)
- `MethodologyCapabilities.has_sprints` должен быть True (проверка на app-слое)

### SprintRetro (Entity внутри Sprint)

Поля:
- id: Id
- template_name: str
- sections: list[RetroSection]
- items: list[RetroItem]
- created_at: datetime

### RetroItem (Entity)

Поля:
- id: Id
- section_id: Id
- content: str
- author_id: Id
- votes: int
- created_at: datetime

> **Гибкая ретро** — вместо захардкоженных 3 списков — шаблон с произвольными секциями. Предустановленные шаблоны создаются при инициализации. Новые форматы ретро = новый `RetroTemplate`, без правки домена.

### Epic (Aggregate Root)

Эпик — самостоятельный AR. Связан с проектом через `project_id`.

Поля:
- project_id: Id (opaque)
- name: str
- description: RichText | None
- status: EpicStatus
- start_date: date | None
- due_date: date | None
- owner_id: Id | None
- color: AccentColor | None
- created_at: datetime
- updated_at: datetime

Методы:
- `create(project_id, name, owner_id=None)` → `Epic` (factory)
- `update(name=None, description=None, owner_id=None, color=None, start_date=None, due_date=None)`
- `change_status(new_status)`

Инварианты:
- `MethodologyCapabilities.has_epics` должен быть True (проверка на app-слое)

### Milestone (Entity внутри Project)

Milestone — ключевая точка проекта. Доступен когда `MethodologyCapabilities.has_milestones=True`.

Поля:
- id: Id
- name: str
- description: RichText | None
- status: MilestoneStatus
- due_date: date
- completed_at: datetime | None

> Milestone — entity на Project AR (не отдельный AR), т.к. немногочисленны и принадлежат проекту.

## Repositories

| Репозиторий | Методы |
|---|---|
| `ProjectRepository` | `get_by_id`, `get_by_workspace`, `get_by_member`, `get_by_methodology`, `get_archived_by_workspace`, `search` |
| `ProjectMembershipRepository` | `get_by_project_id`, `get_member_by_project_and_user`, `get_members_by_project` |
| `BoardRepository` | `get_by_project_id`, `get_by_id` |
| `SprintRepository` | `get_by_id`, `get_by_project`, `get_active_by_project`, `get_backlog_by_project`, `get_by_date_range` |
| `EpicRepository` | `get_by_id`, `get_by_project`, `get_by_status`, `get_by_owner` |
| `ProjectRoleRepository` | `get_by_id`, `get_by_name`, `get_system_roles`, `get_by_project`, `search` |
| `RetroTemplateRepository` | `get_by_id`, `get_system_templates`, `get_by_project`, `get_by_name` |

## Предустановленные системные роли

При создании проекта создаются 5 записей `ProjectRole` с `is_system=True`:

| name | permissions | Описание |
|---|---|---|
| `owner` | `project.*` | Полный доступ, управление владельцами |
| `admin` | `project.settings.*`, `members.*`, `workflow.*`, `views.*`, `automations.*` | Управление проектом |
| `manager` | `members.read`, `workflow.*`, `sprints.*`, `epics.*`, `milestones.*`, `content.*` | Управление процессами |
| `member` | `content.*`, `sprints.read`, `views.read` | Работа с задачами |
| `guest` | `content.read`, `views.read` | Только просмотр |

> Кастомные роли создаются админами/владельцами проекта с `is_system=False`.

## Предустановленные retro-шаблоны

| name | sections |
|---|---|
| `classic` | What went well (POSITIVE), What to improve (NEGATIVE), Action items (ACTION_ITEM) |
| `4ls` | Liked (POSITIVE), Learned (NEUTRAL), Lacked (NEGATIVE), Longed for (NEUTRAL) |
| `start_stop_continue` | Start (ACTION_ITEM), Stop (NEGATIVE), Continue (POSITIVE) |
| `mad_sad_glad` | Mad (NEGATIVE), Sad (NEGATIVE), Glad (POSITIVE) |

> Новые шаблоны ретро = новая запись `RetroTemplate`. Без правки домена.
