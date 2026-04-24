# 05. Project — Проекты

## Обзор

Проект — контейнер для задач внутри workspace. Проект определяет методологию работы (Kanban, Scrum, Waterfall, гибридный), workflow (набор статусов и переходов), представления (Board, List, Timeline, Calendar) и участников с ролями.

---

## Принципы расширяемости

1. **ProjectRole — entity, не enum** — `ProjectRole` хранится как запись с permissions. Кастомные роли без изменения домена.
2. **Разделение AR** — `Project` (ядро) + `Board` (доска/workflow/views/automations) + `Sprint` (спринты) + `Epic` (эпики) + `ProjectMembership` (участники). Каждый AR развивается независимо.
3. **Methodology — enum + capabilities** — `Methodology` определяет доступный функционал через `MethodologyCapabilities`. Новая методология = значение enum + capabilities.
4. **Workflow — entity, не захардкоженные статусы** — произвольные статусы и переходы. Новые статусы = запись, не правка домена.
5. **Типизация** — `SwimlaneGroupBy`, `ViewType`, `CustomFieldType` enum вместо магических строк/dict.
6. **AutomationTrigger/AutomationAction** — enum'ы для правил автоматизации. Новые триггеры/действия = значение enum + обработчик на app-слое.
7. **Events с `changed_fields`** — для детализации изменений.
8. **RetroTemplate** — гибкие шаблоны ретроспектив с произвольными секциями.

---

## 1. Функциональные требования

### 1.1. Управление проектами

| Требование | Free | Start | Business | Enterprise |
|-----------|------|-------|----------|------------|
| Количество проектов на workspace | 5 | 50 | 500 | ∞ |
| Создание проекта | ✅ | ✅ | ✅ | ✅ |
| Изменение проекта | ✅ | ✅ | ✅ | ✅ |
| Удаление/архивация | ✅ | ✅ | ✅ | ✅ |
| Восстановление | ⚡ 7 дней | ✅ 30 дней | ✅ 90 дней | ✅ ∞ |
| Шаблоны проектов | ❌ | ⚡ 3 | ✅ | ✅ |

### 1.2. Участники

- Назначение ответственного (project lead)
- Добавление участников из workspace
- Назначение/изменение ролей участников проекта
- Приватный проект: видим только участникам проекта
- Публичный проект: видим всем участникам workspace

### 1.3. Персонализация проекта

| Поле | Описание |
|------|----------|
| Название | 3–200 символов |
| Описание | Rich text (Markdown / WYSIWYG), до 50 000 символов |
| Иконка | Emoji или загруженное изображение |
| Цвет | HEX-цвет |
| Категория/теги | Множество тегов для группировки |
| Дата начала | optional |
| Дедлайн | optional |
| Статус проекта | Active, On Hold, Completed, Cancelled |
| Видимость | Private / Public (в рамках workspace) |
| Prefix | Короткий код для ID задач (e.g., "PRJ") |

### 1.4. Методологии

| Методология | Free | Start | Business | Enterprise |
|------------|------|-------|----------|------------|
| Kanban | ✅ | ✅ | ✅ | ✅ |
| Scrum | ❌ | ✅ | ✅ | ✅ |
| Waterfall | ❌ | ❌ | ✅ | ✅ |
| Гибридный | ❌ | ❌ | ✅ | ✅ |
| Переключение методологии | — | ✅ | ✅ | ✅ |

#### Kanban
- Настраиваемые колонки (статусы)
- WIP-лимиты (ограничение задач в колонке)
- Swimlanes (по исполнителю, приоритету, epic, тегу)
- Quick filters на доске
- Card appearance (настройка отображения карточек)

#### Scrum
- Спринты (создание, запуск, завершение)
- Product Backlog
- Sprint Backlog
- Sprint Goal
- Перемещение задач в спринт (drag-n-drop)
- Незавершённые задачи → следующий спринт или backlog
- Ретроспектива спринта (встроенный шаблон заметок)

#### Waterfall
- Фазы (phases) с последовательным выполнением
- Gates (точки принятия решений между фазами)
- Milestones (ключевые вехи)

#### Гибридный
- Комбинация элементов из разных методологий
- Спринты + Kanban board
- Фазы + свободные задачи

### 1.5. Спринты (Scrum)

| Требование | Start | Business | Enterprise |
|-----------|-------|----------|------------|
| Макс. активных спринтов | 1 | 3 | ∞ |
| Длительность спринта | 1–6 недель | настраиваемая | настраиваемая |
| Burndown/Burnup charts | ⚡ базовый | ✅ | ✅ |
| Velocity chart | ❌ | ✅ | ✅ |
| Sprint report | ⚡ базовый | ✅ | ✅ |

**Жизненный цикл спринта:**
1. **Planning**: создание спринта, определение цели, перемещение задач из backlog
2. **Active**: спринт запущен, работа над задачами
3. **Review**: обзор выполненной работы
4. **Completed**: спринт завершён, незавершённые задачи → backlog или новый спринт

### 1.6. Agile-метрики

| Метрика | Start | Business | Enterprise |
|---------|-------|----------|------------|
| Burndown Chart | ✅ | ✅ | ✅ |
| Burnup Chart | ❌ | ✅ | ✅ |
| Velocity Chart | ❌ | ✅ | ✅ |
| Cumulative Flow Diagram | ❌ | ✅ | ✅ |
| Cycle Time | ❌ | ✅ | ✅ |
| Lead Time | ❌ | ✅ | ✅ |
| Throughput | ❌ | ✅ | ✅ |
| Sprint Report | ✅ | ✅ | ✅ |

### 1.7. Представления (Views)

| Представление | Free | Start | Business | Enterprise |
|--------------|------|-------|----------|------------|
| Board (Kanban) | ✅ | ✅ | ✅ | ✅ |
| List | ✅ | ✅ | ✅ | ✅ |
| Timeline / Gantt | ❌ | ✅ | ✅ | ✅ |
| Calendar | ❌ | ✅ | ✅ | ✅ |
| Сохранённые views | ❌ | ⚡ 5 | ⚡ 50 | ∞ |

### 1.8. Workflow (Custom Statuses)

| Требование | Free | Start | Business | Enterprise |
|-----------|------|-------|----------|------------|
| Кастомные статусы | ⚡ 5 | ⚡ 15 | ⚡ 50 | ∞ |
| Переходы между статусами | ❌ (любой→любой) | ✅ | ✅ | ✅ |
| Кастомные workflow | ❌ | ⚡ 3 | ⚡ 25 | ∞ |

**Workflow:**
- Набор статусов с цветами и иконками
- Правила переходов (state machine): из какого статуса в какой можно перейти
- Категории статусов: To Do, In Progress, Done, Cancelled
- Начальный статус (default при создании задачи)
- Финальные статусы (задача считается завершённой)

### 1.9. Портфолио проектов (IDEA)

| Требование | Business | Enterprise |
|-----------|----------|------------|
| Группировка по папкам/категориям | ✅ | ✅ |
| Портфолио (обзор проектов) | ✅ | ✅ |
| Зависимости между проектами | ❌ | ✅ |
| Кросс-проектная аналитика | ⚡ | ✅ |
| Roadmap нескольких проектов | ❌ | ✅ |
| RAG status reports | ✅ | ✅ |

### 1.10. Роли на уровне проекта

| Роль | Описание |
|------|----------|
| **Owner** | Создатель проекта, полный контроль |
| **Lead** | Ответственный за проект, управляет задачами и участниками |
| **Admin** | Управление настройками проекта и участниками |
| **Moderator** | Управление задачами, модерация комментариев |
| **Member** | Работа с задачами (создание, изменение назначенных) |
| **Guest** | Только просмотр (read-only) |

### Матрица прав (Project)

| Действие | Owner | Lead | Admin | Moderator | Member | Guest |
|----------|-------|------|-------|-----------|--------|-------|
| Изменить настройки проекта | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Удалить/архивировать проект | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Управлять workflow | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Управлять спринтами | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Добавлять участников | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Назначать роли | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Создавать задачи | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Изменять любые задачи | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Изменять свои задачи | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Удалять задачи | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Комментировать | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Просматривать | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 2. Доменная модель

### Value Objects

| VO | Тип | Описание |
|---|---|---|
| `ProjectStatus` | Enum | `ACTIVE`, `ARCHIVED`, `SUSPENDED`, `PENDING_DELETION` |
| `ProjectVisibility` | Enum | `PRIVATE`, `WORKSPACE`, `ORGANIZATION`, `PUBLIC` |
| `Methodology` | Enum | `KANBAN`, `SCRUM`, `WATERFALL`, `HYBRID`, `SHAPE_UP` |
| `SprintStatus` | Enum | `PLANNING`, `ACTIVE`, `COMPLETED`, `CANCELLED` |
| `MilestoneStatus` | Enum | `NOT_STARTED`, `IN_PROGRESS`, `COMPLETED`, `OVERDUE` |
| `EpicStatus` | Enum | `OPEN`, `IN_PROGRESS`, `DONE`, `CANCELLED` |
| `ViewType` | Enum | `BOARD`, `LIST`, `TIMELINE`, `CALENDAR`, `TABLE`, `ACTIVITY` |
| `SwimlaneGroupBy` | Enum | `ASSIGNEE`, `PRIORITY`, `LABEL`, `EPIC`, `CUSTOM_FIELD` |
| `CustomFieldType` | Enum | `TEXT`, `NUMBER`, `DATE`, `SELECT`, `MULTI_SELECT`, `URL`, `USER`, `CHECKBOX` |
| `AutomationTrigger` | Enum | `STATUS_CHANGED`, `ASSIGNEE_CHANGED`, `DUE_DATE_APPROACHING`, `PRIORITY_CHANGED`, `LABEL_ADDED`, `COMMENT_ADDED` |
| `AutomationAction` | Enum | `ASSIGN_USER`, `CHANGE_STATUS`, `ADD_LABEL`, `SET_DUE_DATE`, `SEND_NOTIFICATION`, `MOVE_TO_SPRINT` |
| `WorkflowStatusCategory` | Enum | `TODO`, `IN_PROGRESS`, `DONE`, `CANCELLED`, `BLOCKED`, `REVIEW` |
| `WIPLimit` | frozen dataclass | value: int (≥1) |
| `SprintGoal` | frozen dataclass | value: str |
| `AccentColor` | frozen dataclass | hex: str (validated `#RRGGBB`) |
| `RichText` | frozen dataclass | content: str, format: RichTextFormat (`MARKDOWN` \| `WYSIWYG`) |
| `DateRange` | frozen dataclass | start: date, end: date (start ≤ end) |
| `Category` | frozen dataclass | name: str, color: AccentColor \| None |
| `FilterOperator` | Enum | `EQ`, `NEQ`, `IN`, `NOT_IN`, `CONTAINS`, `GT`, `LT`, `GTE`, `LTE`, `IS_EMPTY`, `IS_NOT_EMPTY` |
| `SortDirection` | Enum | `ASC`, `DESC` |
| `RetroItemType` | Enum | `POSITIVE`, `NEGATIVE`, `NEUTRAL`, `ACTION_ITEM` |

#### VO Groups

```python
class MethodologyCapabilities:
    has_sprints: bool
    has_backlog: bool
    has_milestones: bool
    has_epics: bool
    has_wip_limits: bool
    has_velocity: bool
    has_retros: bool
    has_burndown: bool
```

Предустановленные capabilities:

| Methodology | sprints | backlog | milestones | epics | wip_limits | velocity | retros | burndown |
|---|---|---|---|---|---|---|---|---|
| `KANBAN` | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `SCRUM` | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ |
| `WATERFALL` | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `HYBRID` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `SHAPE_UP` | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ |

> Новая методология = значение в `Methodology` + определить capabilities. UI проверяет capabilities.

```python
class CardAppearance:
    visible_fields: list[str]
    compact_mode: bool
    show_cover_image: bool

class ProjectViewConfig:
    view_type: ViewType
    filters: list[ViewFilter]
    sorting: list[SortRule]
    grouping: str | None
    card_appearance: CardAppearance | None
    column_settings: dict[str, str] | None

class ViewFilter:
    field: str
    operator: FilterOperator
    value: str

class SortRule:
    field: str
    direction: SortDirection

class CustomFieldDefinition:
    name: str
    field_type: CustomFieldType
    is_required: bool
    options: list[str] | None  # для SELECT/MULTI_SELECT
    default_value: str | None
    description: str | None
```

### Entities

| Сущность | Поля | Описание |
|---|---|---|
| `ProjectRole` | name, permissions: list[str], is_system: bool, description | Роль проекта (entity, не enum) |
| `ProjectMember` | user_id: Id, role: ProjectRole (entity ref), joined_at, is_active | Участник проекта |
| `BoardColumn` | name, order, color: AccentColor \| None, wip_limit: WIPLimit \| None, status_mapping: Id \| None | Колонка доски |
| `Swimlane` | name, order, group_by: SwimlaneGroupBy, group_value: str \| None | Swimlane на доске |
| `WorkflowStatus` | name, color: AccentColor \| None, icon, order, is_default: bool, category: WorkflowStatusCategory | Кастомный статус |
| `WorkflowTransition` | from_status_id, to_status_id, name, trigger: AutomationTrigger \| None, required_permission: str \| None | Переход между статусами |
| `ProjectView` | name, config: ProjectViewConfig, is_default, is_shared, owner_id: Id \| None | Сохранённое представление |
| `AutomationRule` | name, trigger: AutomationTrigger, action: AutomationAction, action_params: dict, is_enabled | Правило автоматизации |
| `RetroTemplate` | name, sections: list[RetroSection] | Шаблон ретроспективы |
| `RetroSection` | title, prompt: str \| None, item_type: RetroItemType | Секция ретро |
| `SprintRetro` | template_name, sections, items: list[RetroItem] | Ретроспектива спринта |
| `RetroItem` | section_id, content, author_id, votes | Элемент ретро |

#### Предустановленные системные роли проекта

При создании проекта создаются `ProjectRole` с `is_system=True`:

| name | permissions | Описание |
|---|---|---|
| `owner` | `["project.*"]` | Полный доступ, управление владельцами |
| `admin` | `["project.settings.*", "members.*", "workflow.*", "views.*", "automations.*"]` | Управление проектом |
| `manager` | `["members.read", "workflow.*", "sprints.*", "epics.*", "milestones.*", "content.*"]` | Управление процессами |
| `member` | `["content.*", "sprints.read", "views.read"]` | Работа с задачами |
| `guest` | `["content.read", "views.read"]` | Только просмотр |

> Кастомные роли = `ProjectRole` с `is_system=False`.

#### Предустановленные retro-шаблоны

| name | sections |
|---|---|
| `classic` | What went well (POSITIVE), What to improve (NEGATIVE), Action items (ACTION_ITEM) |
| `4ls` | Liked (POSITIVE), Learned (NEUTRAL), Lacked (NEGATIVE), Longed for (NEUTRAL) |
| `start_stop_continue` | Start (ACTION_ITEM), Stop (NEGATIVE), Continue (POSITIVE) |
| `mad_sad_glad` | Mad (NEGATIVE), Sad (NEGATIVE), Glad (POSITIVE) |

### Aggregates

#### Project (Aggregate Root)

Ядро проекта — идентичность, статус, методология, владельцы, политики. Не содержит доски/спринты (отдельные AR).

Поля:
- workspace_id: Id (opaque, из Workspace BC)
- name: str (3–200)
- description: RichText | None
- prefix: str (2–6, uppercase, unique in workspace)
- icon: str | None (emoji или URL)
- color: AccentColor | None
- category: Category | None
- tags: list[str]
- methodology: Methodology
- methodology_capabilities: MethodologyCapabilities
- visibility: ProjectVisibility
- status: ProjectStatus
- owner_ids: list[Id] — один или несколько владельцев
- lead_id: Id | None
- start_date: date | None
- deadline: date | None
- custom_field_definitions: list[CustomFieldDefinition]
- task_counter: int — автоинкремент для номеров задач
- roles: list[ProjectRole]
- milestones: list[Milestone]
- created_at: datetime
- updated_at: datetime

Методы:
- `create(name, workspace_id, owner_id, methodology, prefix)` → `Project` (factory)
- `update_info(name=None, description=None, icon=None, color=None, category=None, tags=None, start_date=None, deadline=None)`
- `archive()` — только если нет активных спринтов
- `restore()`
- `suspend(reason)`
- `reactivate()`
- `request_deletion()`
- `change_methodology(new_methodology)` — только если нет активных спринтов
- `change_visibility(visibility)`
- `transfer_ownership(from_id, to_id)`
- `add_owner(user_id)` — со-владелец
- `remove_owner(user_id)` — минимум один
- `assign_lead(user_id)` / `unassign_lead()`
- `add_custom_field(definition)` / `update_custom_field(name, definition)` / `remove_custom_field(name)`
- `create_role(name, permissions, description=None)` / `update_role(name, permissions)` / `delete_role(name)`
- `add_milestone(name, due_date, description=None)` / `update_milestone(id, ...)` / `remove_milestone(id)`

Инварианты:
- Минимум один владелец
- Prefix уникален внутри workspace
- `ARCHIVED` / `SUSPENDED` блокируют все действия кроме restore/reactivate
- Нельзя удалить системную роль / роль в использовании
- При смене методологии — capabilities обновляются
- Имена кастомных полей уникальны в проекте
- Нельзя сменить методологию с активными спринтами
- Task counter монотонно возрастает, не сбрасывается

#### ProjectMembership (Aggregate Root)

Управление участниками проекта. Отдельный AR для масштабируемости.

Поля:
- project_id: Id (opaque)
- members: list[ProjectMember]

Методы:
- `create(project_id, owner_id)` → `ProjectMembership` (factory)
- `add_member(user_id, role, invited_by=None)`
- `remove_member(user_id)`
- `deactivate_member(user_id)` / `reactivate_member(user_id)`
- `change_member_role(user_id, new_role)`

Инварианты:
- Владелец не может быть удалён — сначала снять роль
- Участник должен быть членом workspace (проверка на app-слое)
- `PRIVATE` — только участники видят проект
- `WORKSPACE` — все члены workspace видят, редактируют только участники

#### Board (Aggregate Root)

Доска проекта — колонки, swimlanes, workflow, views, автоматизации.

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
- `create(project_id, methodology)` → `Board` (factory, default columns/statuses)
- `add_column(name, color, wip_limit, status_mapping)` / `remove_column(id)` / `reorder_columns(ids)`
- `change_wip_limit(column_id, wip_limit)`
- `add_swimlane(name, group_by, group_value)` / `remove_swimlane(id)`
- `add_workflow_status(name, color, icon, category, is_default)` / `remove_workflow_status(id)`
- `add_workflow_transition(from_id, to_id, name, required_permission)` / `remove_workflow_transition(id)`
- `create_view(name, config, is_shared)` / `update_view(id, config, name)` / `delete_view(id)`
- `add_automation_rule(name, trigger, action, params)` / `update_automation_rule(id, ...)` / `remove_automation_rule(id)`

Инварианты:
- WIP-лимит ≥ 1
- Transition: from ≠ to
- Хотя бы один `is_default` workflow status
- Хотя бы одна колонка
- AutomationRule срабатывает на app-слое при event

#### Sprint (Aggregate Root)

Спринт — самостоятельный AR. Доступен когда `MethodologyCapabilities.has_sprints=True`.

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
- `start()` — только из PLANNING
- `complete(incomplete_task_ids, next_sprint_id=None)` — незавершённые → backlog или след. спринт
- `cancel()`
- `update_goal(goal)` / `update_date_range(date_range)`
- `create_retro(template: RetroTemplate)`

Инварианты:
- Start: только из PLANNING
- Complete: только из ACTIVE
- Лимит активных спринтов зависит от тарифа (проверка на app-слое)

#### Epic (Aggregate Root)

Эпик — группировка задач выше спринта. Доступен когда `MethodologyCapabilities.has_epics=True`.

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
- `has_epics` capability проверяется на app-слое

---

## 3. Бизнес-правила

1. **Prefix уникальность**: prefix уникален внутри workspace (e.g., "PRJ" → задачи PRJ-1, PRJ-2)
2. **Task counter**: monotonically increasing per project, never resets
3. **Workflow**: каждый проект привязан к одному workflow; workflow может быть расшарен между проектами в workspace
4. **Начальный статус**: ровно один статус в workflow помечен как `is_initial = true`
5. **Финальные статусы**: хотя бы один статус помечен как `is_final = true`
6. **WIP-лимит**: при попытке переместить задачу в колонку с WIP-лимитом — предупреждение (soft) или блокировка (configurable)
7. **Спринт**: только один активный спринт одновременно (Start), до 3 (Business), ∞ (Enterprise)
8. **Завершение спринта**: незавершённые задачи перемещаются в backlog или следующий спринт (настраиваемо)
9. **Переключение методологии**: сохраняет все задачи, адаптирует представления
10. **Архивация проекта**: все задачи становятся read-only; можно восстановить
11. **Visibility**: Private — виден только участникам проекта; Public — виден всем участникам workspace
12. **Owner**: ровно 1 Owner; при удалении/выходе Owner — передать владение
13. **Lead**: может быть не назначен; максимум 1 Lead
14. **Guest**: только read-only доступ; не может быть повышен через project role (только через workspace)
15. **Waterfall phases**: строго последовательные; нельзя начать следующую фазу до завершения текущей (configurable)
16. **Milestone**: может быть привязан к фазе или существовать отдельно
17. **Saved views**: персональные (видны только создателю) или shared (видны всем участникам)

---

## 4. API Endpoints

### 4.1. CRUD проекта

```
POST /api/v1/workspaces/{ws_id}/projects
```

**Request:**
```json
{
  "name": "Backend API",
  "prefix": "API",
  "description": "Backend service development",
  "methodology": "scrum",
  "visibility": "public",
  "color": "#3498DB",
  "tags": ["backend", "api"],
  "start_date": "2025-02-01",
  "due_date": "2025-06-01"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "workspace_id": "ws_uuid",
  "name": "Backend API",
  "prefix": "API",
  "methodology": "scrum",
  "visibility": "public",
  "status": "active",
  "owner_id": "current_user_uuid",
  "workflow_id": "default_workflow_uuid",
  "task_counter": 0,
  "created_at": "2025-01-01T00:00:00Z"
}
```

---

```
GET /api/v1/workspaces/{ws_id}/projects
```

**Query params:** `page`, `limit`, `search`, `status`, `methodology`, `visibility`, `tag`, `sort_by`, `order`

---

```
GET /api/v1/workspaces/{ws_id}/projects/{project_id}
```

---

```
PATCH /api/v1/workspaces/{ws_id}/projects/{project_id}
```

---

```
POST /api/v1/workspaces/{ws_id}/projects/{project_id}/archive
```

---

```
POST /api/v1/workspaces/{ws_id}/projects/{project_id}/restore
```

---

```
DELETE /api/v1/workspaces/{ws_id}/projects/{project_id}
```

---

```
POST /api/v1/workspaces/{ws_id}/projects/{project_id}/transfer-ownership
```

### 4.2. Участники проекта

```
GET /api/v1/workspaces/{ws_id}/projects/{project_id}/members
```

---

```
POST /api/v1/workspaces/{ws_id}/projects/{project_id}/members
```

**Request:**
```json
{
  "user_ids": ["uuid1", "uuid2"],
  "role": "member"
}
```

---

```
PUT /api/v1/workspaces/{ws_id}/projects/{project_id}/members/{member_id}/role
```

---

```
DELETE /api/v1/workspaces/{ws_id}/projects/{project_id}/members/{member_id}
```

---

```
PUT /api/v1/workspaces/{ws_id}/projects/{project_id}/lead
```

**Request:**
```json
{
  "user_id": "uuid"
}
```

### 4.3. Workflow

```
GET /api/v1/workspaces/{ws_id}/workflows
```
*Список workflow workspace*

---

```
POST /api/v1/workspaces/{ws_id}/workflows
```

**Request:**
```json
{
  "name": "Software Development",
  "statuses": [
    {"name": "Backlog", "category": "todo", "color": "#95A5A6", "is_initial": true, "position": 0},
    {"name": "To Do", "category": "todo", "color": "#3498DB", "position": 1},
    {"name": "In Progress", "category": "in_progress", "color": "#F39C12", "position": 2, "wip_limit": 5},
    {"name": "In Review", "category": "in_progress", "color": "#9B59B6", "position": 3, "wip_limit": 3},
    {"name": "Done", "category": "done", "color": "#27AE60", "is_final": true, "position": 4},
    {"name": "Cancelled", "category": "cancelled", "color": "#E74C3C", "is_final": true, "position": 5}
  ],
  "transitions": [
    {"from": "Backlog", "to": "To Do"},
    {"from": "To Do", "to": "In Progress"},
    {"from": "In Progress", "to": "In Review"},
    {"from": "In Review", "to": "Done"},
    {"from": "In Review", "to": "In Progress"},
    {"from": "To Do", "to": "Cancelled"},
    {"from": "In Progress", "to": "Cancelled"}
  ]
}
```

---

```
GET /api/v1/workspaces/{ws_id}/workflows/{workflow_id}
```

---

```
PATCH /api/v1/workspaces/{ws_id}/workflows/{workflow_id}
```

---

```
DELETE /api/v1/workspaces/{ws_id}/workflows/{workflow_id}
```

---

```
PUT /api/v1/workspaces/{ws_id}/projects/{project_id}/workflow
```

**Request:**
```json
{
  "workflow_id": "workflow_uuid"
}
```

### 4.4. Спринты

```
GET /api/v1/workspaces/{ws_id}/projects/{project_id}/sprints
```

**Query params:** `status`, `page`, `limit`

---

```
POST /api/v1/workspaces/{ws_id}/projects/{project_id}/sprints
```

**Request:**
```json
{
  "name": "Sprint 1",
  "goal": "Complete user authentication",
  "start_date": "2025-02-01",
  "end_date": "2025-02-14"
}
```

---

```
PATCH /api/v1/workspaces/{ws_id}/projects/{project_id}/sprints/{sprint_id}
```

---

```
POST /api/v1/workspaces/{ws_id}/projects/{project_id}/sprints/{sprint_id}/start
```

---

```
POST /api/v1/workspaces/{ws_id}/projects/{project_id}/sprints/{sprint_id}/complete
```

**Request:**
```json
{
  "move_incomplete_to": "backlog"
}
```

---

```
DELETE /api/v1/workspaces/{ws_id}/projects/{project_id}/sprints/{sprint_id}
```
*Только для sprints в статусе PLANNING*

---

```
GET /api/v1/workspaces/{ws_id}/projects/{project_id}/sprints/{sprint_id}/report
```

**Response (200):**
```json
{
  "sprint_id": "uuid",
  "name": "Sprint 1",
  "goal": "Complete user authentication",
  "total_tasks": 20,
  "completed_tasks": 15,
  "incomplete_tasks": 5,
  "total_story_points": 40,
  "completed_story_points": 30,
  "burndown_data": [...],
  "velocity": 30
}
```

### 4.5. Waterfall

```
GET /api/v1/workspaces/{ws_id}/projects/{project_id}/phases
```

---

```
POST /api/v1/workspaces/{ws_id}/projects/{project_id}/phases
```

---

```
PATCH /api/v1/workspaces/{ws_id}/projects/{project_id}/phases/{phase_id}
```

---

```
POST /api/v1/workspaces/{ws_id}/projects/{project_id}/phases/{phase_id}/complete
```

---

```
DELETE /api/v1/workspaces/{ws_id}/projects/{project_id}/phases/{phase_id}
```

### 4.6. Milestones

```
GET /api/v1/workspaces/{ws_id}/projects/{project_id}/milestones
```

---

```
POST /api/v1/workspaces/{ws_id}/projects/{project_id}/milestones
```

---

```
PATCH /api/v1/workspaces/{ws_id}/projects/{project_id}/milestones/{milestone_id}
```

---

```
DELETE /api/v1/workspaces/{ws_id}/projects/{project_id}/milestones/{milestone_id}
```

### 4.7. Saved Views

```
GET /api/v1/workspaces/{ws_id}/projects/{project_id}/views
```

---

```
POST /api/v1/workspaces/{ws_id}/projects/{project_id}/views
```

**Request:**
```json
{
  "name": "My Sprint View",
  "type": "board",
  "filters": {
    "sprint_id": "current",
    "assignee_id": "me"
  },
  "sort": {"field": "priority", "order": "desc"},
  "group_by": "status",
  "is_default": false
}
```

---

```
PATCH /api/v1/workspaces/{ws_id}/projects/{project_id}/views/{view_id}
```

---

```
DELETE /api/v1/workspaces/{ws_id}/projects/{project_id}/views/{view_id}
```

### 4.8. Metrics

```
GET /api/v1/workspaces/{ws_id}/projects/{project_id}/metrics/burndown
```

**Query params:** `sprint_id`

---

```
GET /api/v1/workspaces/{ws_id}/projects/{project_id}/metrics/burnup
```

---

```
GET /api/v1/workspaces/{ws_id}/projects/{project_id}/metrics/velocity
```

**Query params:** `last_n_sprints` (default 5)

---

```
GET /api/v1/workspaces/{ws_id}/projects/{project_id}/metrics/cfd
```
*Cumulative Flow Diagram*

---

```
GET /api/v1/workspaces/{ws_id}/projects/{project_id}/metrics/cycle-time
```

---

```
GET /api/v1/workspaces/{ws_id}/projects/{project_id}/metrics/lead-time
```

---

```
GET /api/v1/workspaces/{ws_id}/projects/{project_id}/metrics/throughput
```

---

## 5. Схема БД

### Таблица: `projects`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| workspace_id | UUID | FK → workspaces.id, NOT NULL | |
| name | VARCHAR(200) | NOT NULL | |
| prefix | VARCHAR(6) | NOT NULL | Uppercase, unique per workspace |
| description | TEXT | NULLABLE | Rich text |
| icon | VARCHAR(500) | NULLABLE | Emoji or URL |
| color | VARCHAR(7) | NULLABLE | |
| tags | JSONB | NOT NULL, DEFAULT '[]' | |
| start_date | DATE | NULLABLE | |
| due_date | DATE | NULLABLE | |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'active' | |
| visibility | VARCHAR(10) | NOT NULL, DEFAULT 'public' | |
| methodology | VARCHAR(20) | NOT NULL, DEFAULT 'kanban' | |
| owner_id | UUID | FK → users.id, NOT NULL | |
| lead_id | UUID | FK → users.id, NULLABLE | |
| workflow_id | UUID | FK → workflows.id, NOT NULL | |
| settings | JSONB | NOT NULL, DEFAULT '{}' | |
| task_counter | INTEGER | NOT NULL, DEFAULT 0 | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| archived_at | TIMESTAMPTZ | NULLABLE | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

**Индексы:**
- `idx_proj_ws_prefix` — UNIQUE на `(workspace_id, prefix)`
- `idx_proj_ws` — на `workspace_id`
- `idx_proj_owner` — на `owner_id`
- `idx_proj_status` — на `status`

### Таблица: `project_members`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| project_id | UUID | FK → projects.id, NOT NULL | |
| user_id | UUID | FK → users.id, NOT NULL | |
| role | VARCHAR(20) | NOT NULL | |
| added_by | UUID | FK → users.id, NOT NULL | |
| joined_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_pm_proj_user` — UNIQUE на `(project_id, user_id)`
- `idx_pm_user` — на `user_id`

### Таблица: `workflows`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| workspace_id | UUID | FK → workspaces.id, NOT NULL | |
| project_id | UUID | FK → projects.id, NULLABLE | NULL = шаблон |
| name | VARCHAR(100) | NOT NULL | |
| is_default | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_wf_ws` — на `workspace_id`
- `idx_wf_ws_default` — UNIQUE на `(workspace_id)` WHERE `is_default = TRUE`

### Таблица: `workflow_statuses`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| workflow_id | UUID | FK → workflows.id, NOT NULL | |
| name | VARCHAR(50) | NOT NULL | |
| slug | VARCHAR(50) | NOT NULL | |
| color | VARCHAR(7) | NOT NULL | |
| icon | VARCHAR(100) | NULLABLE | |
| category | VARCHAR(20) | NOT NULL | todo/in_progress/done/cancelled |
| is_initial | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| is_final | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| position | INTEGER | NOT NULL | |
| wip_limit | INTEGER | NULLABLE | |

**Индексы:**
- `idx_wfs_workflow` — на `workflow_id`
- `idx_wfs_workflow_slug` — UNIQUE на `(workflow_id, slug)`
- `idx_wfs_workflow_pos` — на `(workflow_id, position)`

### Таблица: `workflow_transitions`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| workflow_id | UUID | FK → workflows.id, NOT NULL | |
| from_status_id | UUID | FK → workflow_statuses.id, NOT NULL | |
| to_status_id | UUID | FK → workflow_statuses.id, NOT NULL | |
| name | VARCHAR(100) | NULLABLE | |

**Индексы:**
- `idx_wft_workflow` — на `workflow_id`
- `idx_wft_from_to` — UNIQUE на `(workflow_id, from_status_id, to_status_id)`

### Таблица: `sprints`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| project_id | UUID | FK → projects.id, NOT NULL | |
| name | VARCHAR(100) | NOT NULL | |
| goal | TEXT | NULLABLE | |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'planning' | |
| start_date | DATE | NOT NULL | |
| end_date | DATE | NOT NULL | |
| started_at | TIMESTAMPTZ | NULLABLE | |
| completed_at | TIMESTAMPTZ | NULLABLE | |
| retrospective_notes | TEXT | NULLABLE | Rich text |
| created_by | UUID | FK → users.id, NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_sprint_project` — на `project_id`
- `idx_sprint_status` — на `(project_id, status)`

### Таблица: `waterfall_phases`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| project_id | UUID | FK → projects.id, NOT NULL | |
| name | VARCHAR(100) | NOT NULL | |
| description | TEXT | NULLABLE | |
| position | INTEGER | NOT NULL | |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'not_started' | |
| start_date | DATE | NULLABLE | |
| end_date | DATE | NULLABLE | |
| gate_criteria | TEXT | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_wfp_project` — на `project_id`
- `idx_wfp_position` — на `(project_id, position)`

### Таблица: `milestones`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| project_id | UUID | FK → projects.id, NOT NULL | |
| name | VARCHAR(200) | NOT NULL | |
| description | TEXT | NULLABLE | |
| due_date | DATE | NULLABLE | |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'open' | |
| phase_id | UUID | FK → waterfall_phases.id, NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_ms_project` — на `project_id`

### Таблица: `saved_views`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| project_id | UUID | FK → projects.id, NOT NULL | |
| name | VARCHAR(100) | NOT NULL | |
| type | VARCHAR(20) | NOT NULL | board/list/timeline/calendar |
| filters | JSONB | NOT NULL, DEFAULT '{}' | |
| sort | JSONB | NOT NULL, DEFAULT '{}' | |
| group_by | VARCHAR(50) | NULLABLE | |
| columns | JSONB | NULLABLE | |
| is_default | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| is_shared | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| created_by | UUID | FK → users.id, NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_sv_project` — на `project_id`
- `idx_sv_creator` — на `(project_id, created_by)`

---

## 6. Доменные события

| Событие | Поля | Описание |
|---|---|---|
| `ProjectCreated` | project_id, workspace_id, name, methodology | Проект создан |
| `ProjectInfoChanged` | project_id, changed_fields: list[str] | Информация обновлена |
| `ProjectArchived` | project_id | Архивирован |
| `ProjectRestored` | project_id | Восстановлен |
| `ProjectSuspended` | project_id, reason | Приостановлен |
| `ProjectReactivated` | project_id | Реактивирован |
| `ProjectDeletionRequested` | project_id | Запрос удаления |
| `MethodologyChanged` | project_id, old_methodology, new_methodology | Методология изменена |
| `ProjectVisibilityChanged` | project_id, new_visibility | Видимость изменена |
| `ProjectMemberJoined` | project_id, user_id, role | Участник добавлен |
| `ProjectMemberRemoved` | project_id, user_id | Участник удалён |
| `ProjectMemberRoleChanged` | project_id, user_id, new_role | Роль изменена |
| `ProjectRoleCreated` | project_id, role_name | Кастомная роль создана |
| `ProjectRoleUpdated` | project_id, role_name | Роль обновлена |
| `ProjectRoleDeleted` | project_id, role_name | Роль удалена |
| `BoardColumnAdded` | project_id, column_id, name | Колонка добавлена |
| `BoardColumnRemoved` | project_id, column_id | Колонка удалена |
| `BoardColumnReordered` | project_id | Колонки переупорядочены |
| `WIPLimitChanged` | project_id, column_id | WIP-лимит изменён |
| `SwimlaneAdded` | project_id, swimlane_id | Swimlane добавлена |
| `SwimlaneRemoved` | project_id, swimlane_id | Swimlane удалена |
| `WorkflowStatusAdded` | project_id, status_id, name, category | Статус добавлен |
| `WorkflowStatusRemoved` | project_id, status_id | Статус удалён |
| `WorkflowTransitionAdded` | project_id, transition_id | Переход добавлен |
| `WorkflowTransitionRemoved` | project_id, transition_id | Переход удалён |
| `ProjectViewCreated` | project_id, view_id | Представление создано |
| `ProjectViewUpdated` | project_id, view_id | Представление обновлено |
| `ProjectViewDeleted` | project_id, view_id | Представление удалено |
| `EpicCreated` | project_id, epic_id | Эпик создан |
| `EpicUpdated` | project_id, epic_id, changed_fields: list[str] | Эпик обновлён |
| `EpicStatusChanged` | project_id, epic_id, new_status | Статус эпика |
| `MilestoneCreated` | project_id, milestone_id | Milestone создан |
| `MilestoneUpdated` | project_id, milestone_id, changed_fields: list[str] | Milestone обновлён |
| `MilestoneStatusChanged` | project_id, milestone_id, new_status | Статус milestone |
| `CustomFieldDefinitionAdded` | project_id, field_name, field_type | Кастомное поле добавлено |
| `CustomFieldDefinitionUpdated` | project_id, field_name | Поле обновлено |
| `CustomFieldDefinitionRemoved` | project_id, field_name | Поле удалено |
| `AutomationRuleCreated` | project_id, rule_id | Правило создано |
| `AutomationRuleUpdated` | project_id, rule_id | Правило обновлено |
| `AutomationRuleDeleted` | project_id, rule_id | Правило удалено |
| `AutomationRuleTriggered` | project_id, rule_id, trigger_data: dict | Правило сработало |
| `SprintCreated` | sprint_id, project_id, name | Спринт создан |
| `SprintStarted` | sprint_id | Спринт запущен |
| `SprintCompleted` | sprint_id | Спринт завершён |
| `SprintCancelled` | sprint_id | Спринт отменён |
| `SprintGoalUpdated` | sprint_id | Цель обновлена |
| `SprintRetroCreated` | sprint_id, template_name | Ретро создана |
| `TasksMovedToNextSprint` | sprint_id, task_ids | Задачи → след. спринт |
| `TasksMovedToBacklog` | sprint_id, task_ids | Задачи → бэклог |

---

## 7. Exceptions

| Исключение | Описание |
|---|---|
| `ProjectNotFoundException` | Проект не найден |
| `ProjectSuspendedException` | Проект приостановлен |
| `ProjectArchivedException` | Проект архивирован, действие невозможно |
| `DuplicateProjectPrefixException` | Prefix уже используется в workspace |
| `ProjectMemberNotFoundException` | Участник не найден |
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
| `CannotCompleteSprintWithOpenTasksException` | Нельзя завершить без обработки открытых задач |
| `EpicNotFoundException` | Эпик не найден |
| `MilestoneNotFoundException` | Milestone не найден |
| `MilestoneOverdueException` | Milestone просрочен |
| `CustomFieldDefinitionNotFoundException` | Кастомное поле не найдено |
| `DuplicateCustomFieldException` | Поле с таким именем уже существует |
| `AutomationRuleNotFoundException` | Правило не найдено |
| `MethodologyCapabilityNotAvailableException` | Функция недоступна для методологии |
| `CannotChangeMethodologyWithActiveSprintsException` | Нельзя сменить методологию с активными спринтами |
| `CannotDeleteSystemRoleException` | Нельзя удалить системную роль |

---

## 8. Repositories

| Репозиторий | Методы |
|---|---|
| `ProjectRepository` | `get_by_id`, `get_by_workspace`, `get_by_member`, `get_by_methodology`, `get_archived_by_workspace`, `search` |
| `ProjectMembershipRepository` | `get_by_project_id`, `get_member_by_project_and_user`, `get_members_by_project` |
| `BoardRepository` | `get_by_project_id`, `get_by_id` |
| `SprintRepository` | `get_by_id`, `get_by_project`, `get_active_by_project`, `get_backlog_by_project`, `get_by_date_range` |
| `EpicRepository` | `get_by_id`, `get_by_project`, `get_by_status`, `get_by_owner` |
| `ProjectRoleRepository` | `get_by_id`, `get_by_name`, `get_system_roles`, `get_by_project`, `search` |
| `RetroTemplateRepository` | `get_by_id`, `get_system_templates`, `get_by_project`, `get_by_name` |

---

## 9. Интеграция с другими BC

| Событие | Целевой BC | Действие |
|---|---|---|
| `ProjectCreated` | Board | Создать Board для проекта |
| `ProjectCreated` | ProjectMembership | Создать ProjectMembership |
| `ProjectArchived` | Task | Все задачи → read-only |
| `SprintCompleted` | Task | Переместить незавершённые задачи |
| `WorkspaceDeleted` (из Workspace BC) | Project | Архивировать все проекты |
| `AutomationRuleTriggered` | Task / Notification | Выполнить действие автоматизации |
