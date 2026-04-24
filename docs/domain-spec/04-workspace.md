# Workspace BC — Спецификация

> Путь: `app/context/workspace/domain`
> Исходные требования: §4 (Workspace)

## Контекст

Workspace BC отвечает за рабочие пространства: создание, участники, безопасность, персонализацию, роли, иерархию. Workspace может принадлежать организации или быть независимым. Поддерживает иерархию: дочерние workspace наследуют политики от родительского.

---

## Принципы расширяемости

1. **Роли — entity, не enum** — `WorkspaceRole` хранится как запись с permissions. Кастомные роли без изменения домена.
2. **Разделение AR** — Workspace (ядро) + WorkspaceMembership (члены) + WorkspaceTeam (команды). Каждый AR развивается независимо.
3. **Иерархия через parent_id** — opaque ID, без загрузки дерева в агрегат. Проверки на app-слое (циклы, наследование политик).
4. **Политики — VO-группы** — `SecurityPolicy`, `MembershipPolicy`, `WorkspaceLimits` как расширяемые группы. Новое правило = поле в VO.
5. **Тип workspace — enum с расширяемыми возможностями** — `WorkspaceType` определяет доступный функционал. Новые типы = новое значение enum.
6. **Events по группам** — `changed_fields` для детализации.

---

## Value Objects

### Общие

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `WorkspaceStatus` | Enum | `ACTIVE`, `ARCHIVED`, `SUSPENDED`, `PENDING_DELETION` | §4.1 |
| `WorkspaceType` | Enum | `PERSONAL`, `TEAM`, `ENTERPRISE` | §4.1 |
| `MemberSource` | Enum | `DIRECT`, `ORGANIZATION`, `PARENT_WORKSPACE`, `INVITATION_LINK` | §4.2 |
| `InvitationStatus` | Enum | `PENDING`, `ACCEPTED`, `DECLINED`, `EXPIRED`, `REVOKED` | §4.2 |
| `SSOMode` | Enum | `NONE`, `OPTIONAL`, `REQUIRED` | §4.3 |
| `AccentColor` | frozen dataclass | hex: str (validated #RRGGBB) | §4.4 |
| `InvitationToken` | frozen dataclass | value: str, expires_at: datetime \| None, max_uses: int \| None, used_count: int | §4.2 |

> **`WorkspaceType`** — определяет доступный функционал. `PERSONAL` — один пользователь, ограниченные функции. `TEAM` — стандартный набор. `ENTERPRISE` — полный набор + SSO + аудит. Новые типы (например, `EDUCATION`, `OPEN_SOURCE`) добавляются как значения enum.

> **`MemberSource`** — от куда участник пришёл. `PARENT_WORKSPACE` — унаследован из родительского workspace (для иерархии).

### WorkspacePersonalization (VO group)

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `WorkspacePersonalization` | frozen dataclass | color: AccentColor, icon_url: Url \| None, display_name: str \| None, description: str \| None, branding: WorkspaceBranding \| None | §4.4 |
| `WorkspaceBranding` | frozen dataclass | logo_url: Url \| None, cover_image_url: Url \| None, custom_css: str \| None | §4.4 |

### SecurityPolicy (VO group)

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `SecurityPolicy` | frozen dataclass | pin_code_enabled: bool, password_enabled: bool, ip_allowlist: list[str], sso_mode: SSOMode, require_2fa: bool, session_timeout_minutes: int \| None, inherit_from_parent: bool | §4.3 |

> **`inherit_from_parent`** — если True, дочерний workspace наследует SecurityPolicy от родителя. При изменении политики родителя — каскадное обновление через events на app-слое.
>
> **Расширение политик** — новые правила (watermark_enabled, download_restricted, copy_paste_restricted) = поле в `SecurityPolicy`.

### MembershipPolicy (VO group)

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `MembershipPolicy` | frozen dataclass | allow_invitation_links: bool, default_role: str, require_approval: bool, max_members: int \| None, allowed_email_domains: list[str], auto_add_from_org: bool, inherit_from_parent: bool | §4.2 |

> **`auto_add_from_org`** — если True и workspace привязан к организации, новые члены организации автоматически добавляются в workspace.
>
> **`inherit_from_parent`** — аналогично SecurityPolicy, наследование от родительского workspace.

### WorkspaceLimits (VO group)

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `WorkspaceLimits` | frozen dataclass | max_projects: int \| None, max_members: int \| None, max_storage_bytes: int \| None, max_file_size_bytes: int \| None, max_teams: int \| None | — |

> **Лимиты** — могут задаваться планом подписки (Billing BC) или вручную админом. Новые лимиты (max_automations, max_integrations) = поле в `WorkspaceLimits`. Проверка на app-слое перед действием.

## Entities

| Сущность | Поля | Описание | Исходное требование |
|---|---|---|---|
| `WorkspaceMember` | user_id: Id, display_name: str \| None, role: WorkspaceRole (entity ref), joined_at: datetime, is_active: bool, source: MemberSource, invited_by: Id \| None | Участник workspace | §4.2 |
| `WorkspaceRole` | name: str, permissions: list[str], is_system: bool, description: str \| None | Роль workspace (системная или кастомная) | §4.5 |
| `WorkspaceInvitation` | id: Id, email: Email \| None, link: InvitationToken \| None, role: WorkspaceRole (entity ref), invited_by: Id, invited_at: datetime, status: InvitationStatus | Приглашение в workspace | §4.2 |

> **`WorkspaceRole` — entity, не enum** — системные роли (owner, admin, moderator, member) — предустановленные записи с `is_system=True`. Кастомные роли создаются админами workspace.

## Domain Events

| Событие | Поля | Описание | Исходное требование |
|---|---|---|---|
| `WorkspaceCreated` | workspace_id, owner_id, name, organization_id \| None, parent_workspace_id \| None, workspace_type | Workspace создан | §4.1 |
| `WorkspaceInfoChanged` | workspace_id, changed_fields: list[str] | Информация обновлена | §4.1 |
| `WorkspaceArchived` | workspace_id | Workspace архивирован | §4.1 |
| `WorkspaceRestored` | workspace_id | Workspace восстановлен | §4.1 |
| `WorkspaceSuspended` | workspace_id, reason | Workspace приостановлен | §4.1 |
| `WorkspaceReactivated` | workspace_id | Workspace реактивирован | §4.1 |
| `WorkspaceDeletionRequested` | workspace_id | Запрос удаления workspace | §4.1 |
| `OwnershipTransferred` | workspace_id, old_owner_id, new_owner_id | Владение передано | §4.1 |
| `WorkspaceMemberJoined` | workspace_id, user_id, role, source | Участник присоединился | §4.2 |
| `WorkspaceMemberDisplayNameChanged` | workspace_id, user_id, display_name | Отображаемое имя участника изменено | §4.2 |
| `WorkspaceMemberRoleChanged` | workspace_id, user_id, new_role | Роль изменена | §4.2 |
| `WorkspaceMemberRemoved` | workspace_id, user_id | Участник удалён | §4.2 |
| `WorkspaceMemberDeactivated` | workspace_id, user_id | Участник деактивирован | §4.2 |
| `WorkspaceMemberReactivated` | workspace_id, user_id | Участник реактивирован | §4.2 |
| `MemberAddedFromOrganization` | workspace_id, user_id | Участник добавлен из организации (ACL) | §4.2 |
| `MemberInheritedFromParent` | workspace_id, user_id, parent_workspace_id | Участник унаследован из родительского workspace | §4.2 |
| `WorkspaceRoleCreated` | workspace_id, role_name | Кастомная роль создана | §4.5 |
| `WorkspaceRoleUpdated` | workspace_id, role_name | Роль обновлена | §4.5 |
| `WorkspaceRoleDeleted` | workspace_id, role_name | Кастомная роль удалена | §4.5 |
| `InvitationSent` | workspace_id, email \| None, role | Приглашение отправлено | §4.2 |
| `InvitationAccepted` | workspace_id, user_id | Приглашение принято | §4.2 |
| `InvitationDeclined` | workspace_id, email \| None | Приглашение отклонено | §4.2 |
| `InvitationRevoked` | workspace_id, invitation_id | Приглашение отозвано | §4.2 |
| `InvitationLinkGenerated` | workspace_id, token | Ссылка-приглашение | §4.2 |
| `SecurityPolicyChanged` | workspace_id, changed_fields: list[str] | Политика безопасности изменена | §4.3 |
| `MembershipPolicyChanged` | workspace_id, changed_fields: list[str] | Политика членства изменена | §4.2 |
| `WorkspaceLimitsChanged` | workspace_id, changed_fields: list[str] | Лимиты изменены | — |
| `WorkspacePersonalizationChanged` | workspace_id, changed_fields: list[str] | Персонализация изменена | §4.4 |
| `ChildWorkspaceCreated` | parent_workspace_id, child_workspace_id | Дочерний workspace создан | — |
| `WorkspaceTeamCreated` | workspace_id, team_id | Команда создана | §4.2 |
| `WorkspaceTeamUpdated` | workspace_id, team_id, changed_fields: list[str] | Команда обновлена | §4.2 |
| `WorkspaceTeamDeleted` | workspace_id, team_id | Команда удалена | §4.2 |
| `WorkspaceTeamMemberAdded` | workspace_id, team_id, user_id | Участник добавлен в команду | §4.2 |
| `WorkspaceTeamMemberRemoved` | workspace_id, team_id, user_id | Участник удалён из команды | §4.2 |

## Exceptions

| Исключение | Описание |
|---|---|
| `WorkspaceNotFoundException` | Workspace не найден |
| `WorkspaceSuspendedException` | Workspace приостановлен |
| `WorkspaceArchivedException` | Workspace архивирован, действие невозможно |
| `WorkspaceMemberNotFoundException` | Участник не найден |
| `WorkspaceRoleNotFoundException` | Роль не найдена |
| `WorkspaceRoleInUseException` | Роль используется, нельзя удалить |
| `CannotRemoveOwnerException` | Нельзя удалить владельца |
| `CannotRemoveLastOwnerException` | Нельзя удалить последнего владельца |
| `CannotTransferOwnershipException` | Нельзя передать владение |
| `WorkspaceTeamNotFoundException` | Команда не найдена |
| `InvitationNotFoundException` | Приглашение не найдено |
| `InvitationExpiredException` | Приглашение истекло |
| `InvitationLinkExpiredException` | Ссылка истекла |
| `InvitationLinkMaxUsesExceededException` | Лимит использований ссылки исчерпан |
| `DuplicateInvitationException` | Приглашение уже отправлено |
| `MembershipLimitExceededException` | Лимит участников превышен |
| `WorkspaceLimitExceededException` | Лимит workspace превышен (projects/members/storage) |
| `SecurityPolicyViolationException` | Нарушение политики безопасности |
| `IPAllowlistViolationException` | IP не в allowlist |
| `SSORequiredException` | Требуется SSO аутентификация |
| `CircularWorkspaceHierarchyException` | Циклическая ссылка в иерархии workspace |
| `ParentWorkspaceNotFoundException` | Родительский workspace не найден |
| `CannotArchiveWithChildrenException` | Нельзя архивировать workspace с активными дочерними |

## Aggregates

### Workspace (Aggregate Root)

Ядро workspace — идентичность, статус, владельцы, политики, иерархия. Не содержит списки членов/команд (это отдельные AR). Связь через `workspace_id` (opaque ID).

Поля:
- name: str
- status: WorkspaceStatus
- workspace_type: WorkspaceType
- organization_id: Id | None (opaque, из Organization BC)
- parent_workspace_id: Id | None (opaque, для иерархии)
- personalization: WorkspacePersonalization
- owner_ids: list[Id] — один или несколько владельцев
- security_policy: SecurityPolicy
- membership_policy: MembershipPolicy
- limits: WorkspaceLimits
- created_at: datetime
- updated_at: datetime

Методы:
- `create(name, owner_id, workspace_type, organization_id=None, parent_workspace_id=None)` → `Workspace` (factory)
- `update_info(name=None, personalization=None)`
- `archive()` — только если нет активных дочерних workspace
- `restore()`
- `suspend(reason)`
- `reactivate()`
- `request_deletion()`
- `transfer_ownership(from_id, to_id)`
- `add_owner(user_id)` — со-владелец
- `remove_owner(user_id)` — минимум один владелец
- `update_security_policy(policy: SecurityPolicy)`
- `update_membership_policy(policy: MembershipPolicy)`
- `update_limits(limits: WorkspaceLimits)`
- `create_role(name, permissions, description=None)` — кастомная роль
- `update_role(name, permissions=None, description=None)`
- `delete_role(name)` — только кастомные
- `move_under_parent(parent_workspace_id)` — переместить в иерархию
- `detach_from_parent()` — сделать корневым workspace

Инварианты:
- Минимум один владелец
- `WorkspaceStatus.ARCHIVED` блокирует все действия кроме `restore`
- `WorkspaceStatus.SUSPENDED` блокирует все действия кроме `reactivate`
- `WorkspaceStatus.PENDING_DELETION` блокирует все действия
- Нельзя удалить системную роль (`is_system=True`)
- Нельзя удалить роль если она используется участниками
- Иерархия: циклы проверяются на app-слое (обход дерева по `parent_workspace_id`)
- Нельзя архивировать workspace с активными дочерними
- `SecurityPolicy.inherit_from_parent=True` — политика наследуется от родителя (проверка на app-слое)
- `MembershipPolicy.inherit_from_parent=True` — политика наследуется от родителя
- `WorkspaceType.PERSONAL` — ограничение: max_members=1, нет команд

### WorkspaceMembership (Aggregate Root)

Управление участниками workspace. Отдельный AR для масштабируемости.

Поля:
- workspace_id: Id (opaque)
- members: list[WorkspaceMember]
- invitations: list[WorkspaceInvitation]

Методы:
- `create(workspace_id, owner_id)` → `WorkspaceMembership` (factory)
- `add_member(user_id, role, source, invited_by=None, display_name=None)` — прямое добавление
- `add_member_from_org(user_id, role)` — из организации (ACL)
- `inherit_member_from_parent(user_id, role, parent_workspace_id)` — из родительского workspace
- `remove_member(user_id)`
- `deactivate_member(user_id)`
- `reactivate_member(user_id)`
- `change_member_role(user_id, new_role)`
- `update_member_display_name(user_id, display_name)` — установить никнейм/ФИО в рамках workspace
- `invite_member(email, role)` — email-приглашение
- `invite_members_bulk(emails, role)` — массовое
- `generate_invitation_link(role, expires_at=None, max_uses=None)`
- `accept_invitation(token, user_id)`
- `decline_invitation(token)`
- `revoke_invitation(invitation_id)`

Инварианты:
- Владелец не может быть удалён/деактивирован — сначала снять роль
- Приглашение уникально по email в рамках workspace
- Invitation link: опциональные expires_at и max_uses
- `MembershipPolicy.max_members` проверяется при добавлении
- `MembershipPolicy.allowed_email_domains` проверяется при приглашении
- `MembershipPolicy.require_approval` — приглашения в статусе PENDING до подтверждения
- `MembershipPolicy.auto_add_from_org` — автоматическое добавление при событии `OrgMemberJoined` из Organization BC

### WorkspaceTeam (Aggregate Root)

Команда — самостоятельный AR. Связан с workspace через `workspace_id`.

Поля:
- workspace_id: Id (opaque)
- name: str
- description: str | None
- lead_id: Id | None
- member_ids: list[Id]
- icon_url: Url | None
- is_active: bool
- created_at: datetime
- updated_at: datetime

Методы:
- `create(workspace_id, name, lead_id=None)` → `WorkspaceTeam` (factory)
- `update(name=None, description=None, lead_id=None, icon_url=None)`
- `add_member(user_id)`
- `remove_member(user_id)`
- `deactivate()`
- `reactivate()`

Инварианты:
- Участник команды должен быть членом workspace (проверка на app-слое через ACL)
- lead_id должен быть членом команды
- Неактивная команда не может принимать участников

## Иерархия workspace

```
Organization
├── Workspace A (root, enterprise)
│   ├── Workspace A1 (child, team)
│   └── Workspace A2 (child, team)
├── Workspace B (root, team)
└── Workspace C (root, personal)
```

**Правила иерархии:**

1. `parent_workspace_id` — opaque ID, хранится на дочернем workspace. Родитель не содержит список детей — запрос через repository.
2. **Наследование политик** — если `inherit_from_parent=True`, дочерний workspace получает политику от родителя. При изменении политики родителя — app-layer handler обновляет детей (через events).
3. **Наследование членов** — `MemberSource.PARENT_WORKSPACE`. При добавлении члена в родительский — можно автоматически добавить в дочерние (настраивается через `MembershipPolicy`).
4. **Циклы** — проверяются на app-слое перед `move_under_parent()`. Обход дерева по `parent_workspace_id` через repository.
5. **Архивирование** — нельзя архивировать workspace с активными дочерними. Сначала архивируются дети (снизу вверх).
6. **Глубина** — ограничение на app-слое (например, макс. 3 уровня). Проверяется при `move_under_parent()`.
7. **WorkspaceType** — дочерний workspace может иметь другой тип (родитель enterprise → ребёнок team).

> **Расширение иерархии**: В будущем можно добавить: веса/приоритеты между siblings, автоматическое распределение задач по дочерним workspace, агрегацию аналитики снизу вверх. Все эти функции — на app-слое, доменная модель уже поддерживает.

## Repositories

| Репозиторий | Методы |
|---|---|
| `WorkspaceRepository` | `get_by_id`, `get_by_owner`, `get_by_organization`, `get_by_parent`, `get_children`, `get_root_workspaces`, `search`, `count_by_organization` |
| `WorkspaceMembershipRepository` | `get_by_workspace_id`, `get_member_by_workspace_and_user`, `get_members_by_workspace`, `get_invitations_by_workspace`, `get_invitation_by_token` |
| `WorkspaceTeamRepository` | `get_by_id`, `get_by_workspace`, `get_by_member`, `get_by_lead` |
| `WorkspaceRoleRepository` | `get_by_id`, `get_by_name`, `get_system_roles`, `get_by_workspace`, `search` |

## Предустановленные системные роли

При создании workspace создаются 4 записи `WorkspaceRole` с `is_system=True`:

| name | permissions | Описание |
|---|---|---|
| `owner` | `workspace.*` | Полный доступ, управление владельцами |
| `admin` | `workspace.settings.*`, `members.*`, `teams.*`, `projects.*`, `content.*` | Управление workspace |
| `moderator` | `members.read`, `members.invite`, `content.*`, `teams.*` | Ограниченное управление |
| `member` | `self.*`, `content.read`, `projects.read`, `teams.read` | Базовый доступ |

> Кастомные роли создаются админами/владельцами workspace с `is_system=False`. Примеры: `guest` (только чтение), `contractor` (ограниченный доступ), `viewer` (просмотр без редактирования).

## WorkspaceType — доступный функционал

| Тип | Макс. участники | Команды | SSO | Иерархия | Лимиты |
|---|---|---|---|---|---|
| `PERSONAL` | 1 | Нет | Нет | Только корень | Ограниченные |
| `TEAM` | ∞ (по лимиту) | Да | Нет | Корень или ребёнок | Стандартные |
| `ENTERPRISE` | ∞ (по лимиту) | Да | Да | Корень или ребёнок | Расширенные |

> **Новый тип workspace** — добавить значение в `WorkspaceType` + определить доступный функционал. Например, `EDUCATION` — с ограничениями для учебных заведений.
