# 04. Workspace — Рабочие пространства

## Обзор

Workspace — основная единица работы. Может существовать автономно (для Free/Start) или в составе организации (Business/Enterprise). Внутри workspace создаются проекты, задачи, и вся рабочая деятельность.

**Доступность:** Free ✅ (1) | Start ✅ (5) | Business ✅ (25) | Enterprise ✅ (∞)

---

## 1. Функциональные требования

### 1.1. Управление пространством

| Требование | Free | Start | Business | Enterprise |
|-----------|------|-------|----------|------------|
| Создание workspace | ✅ (1) | ✅ (5) | ✅ (25) | ✅ (∞) |
| Изменение информации | ✅ | ✅ | ✅ | ✅ |
| Удаление/архивация | ✅ | ✅ | ✅ | ✅ |
| Восстановление | ⚡ 7 дней | ✅ 30 дней | ✅ 90 дней | ✅ ∞ |
| Передача владения | ✅ | ✅ | ✅ | ✅ |
| Переключение между workspace | — | ✅ | ✅ | ✅ |

**Правила:**
- Standalone workspace (Free/Start): не привязан к организации
- Organizational workspace (Business/Enterprise): привязан к организации
- Создатель автоматически становится Owner
- Удаление: soft-delete, workspace и все проекты архивируются
- Архивированный workspace: read-only доступ к данным
- При восстановлении — все проекты тоже восстанавливаются

### 1.2. Участники

| Требование | Free | Start | Business | Enterprise |
|-----------|------|-------|----------|------------|
| Макс. участников | 10 | 25–50 | 100–500 | ∞ |
| Приглашение по email (одиночное) | ✅ | ✅ | ✅ | ✅ |
| Приглашение по email (массовое) | ❌ | ✅ (до 20) | ✅ (до 50) | ✅ (до 500) |
| Приглашение по ссылке | ❌ | ✅ | ✅ | ✅ |
| Настройка срока ссылки | — | ✅ | ✅ | ✅ |
| Лимит использований ссылки | — | ✅ | ✅ | ✅ |
| Назначение/изменение ролей | ✅ | ✅ | ✅ | ✅ |
| Удаление/деактивация | ✅ | ✅ | ✅ | ✅ |
| Просмотр профилей | ✅ | ✅ | ✅ | ✅ |
| Группы/команды | ❌ | ✅ | ✅ | ✅ |
| Добавление из организации | — | — | ✅ | ✅ |

**Правила:**
- Для organizational workspace: участник должен быть членом организации
- «Добавление из организации»: быстрое добавление без повторного приглашения
- Группы workspace: могут наследоваться из организации или создаваться локально

### 1.3. Безопасность workspace

| Требование | Free | Start | Business | Enterprise |
|-----------|------|-------|----------|------------|
| Пин-код | ❌ | ❌ | ✅ | ✅ |
| Пароль | ❌ | ❌ | ✅ | ✅ |
| IP-whitelist | ❌ | ❌ | ❌ | ✅ |
| Единоразовый вход через корп. аккаунт | — | — | ✅ | ✅ |
| Каждый раз вход через корп. аккаунт | — | — | ❌ | ✅ |

**Режимы доступа:**
- **Открытый**: без дополнительной аутентификации (после входа в систему)
- **PIN**: 4-6 цифр, запрашивается при входе в workspace
- **Пароль**: отдельный пароль workspace, запрашивается при входе
- **Корпоративный**: повторная SSO-аутентификация при входе в workspace
- **IP-whitelist**: доступ только с разрешённых IP (для Enterprise)

### 1.4. Персонализация

- Название (3–100 символов)
- Slug (unique внутри организации или глобально для standalone)
- Логотип (PNG/SVG, до 5 MB)
- Иконка (PNG/SVG, до 1 MB)
- Основной цвет (HEX)
- Описание (до 500 символов)

### 1.5. Роли на уровне workspace

| Роль | Описание |
|------|----------|
| **Owner** | Полный контроль, удаление workspace, передача владения |
| **Admin** | Управление участниками, проектами, настройками |
| **Moderator** | Управление участниками, создание проектов |
| **Member** | Работа с проектами и задачами (в рамках назначенных проектов) |

### Матрица прав (Workspace)

| Действие | Owner | Admin | Moderator | Member |
|----------|-------|-------|-----------|--------|
| Изменить информацию workspace | ✅ | ✅ | ❌ | ❌ |
| Удалить/архивировать workspace | ✅ | ❌ | ❌ | ❌ |
| Восстановить workspace | ✅ | ❌ | ❌ | ❌ |
| Передать владение | ✅ | ❌ | ❌ | ❌ |
| Настроить безопасность | ✅ | ✅ | ❌ | ❌ |
| Приглашать участников | ✅ | ✅ | ✅ | ❌ |
| Удалять/деактивировать участников | ✅ | ✅ | ✅ | ❌ |
| Назначать роли (ниже своей) | ✅ | ✅ | ❌ | ❌ |
| Создавать проекты | ✅ | ✅ | ✅ | ❌ |
| Просматривать все проекты | ✅ | ✅ | ✅ | ❌ |
| Работать с задачами | ✅ | ✅ | ✅ | ✅ |
| Управлять группами | ✅ | ✅ | ✅ | ❌ |
| Персонализация | ✅ | ✅ | ❌ | ❌ |

---

## Принципы расширяемости

1. **WorkspaceRole — entity, не enum** — роли как сущности с `is_system` флагом. Кастомные роли = запись.
2. **Policies — VO group** — `SecurityPolicy`, `MembershipPolicy` как группы настроек. Новые настройки = поле в VO.
3. **WorkspacePersonalization — VO group** — `logo_url`, `icon_url`, `primary_color`, `description` в одном VO.
4. **WorkspaceType — enum** — `STANDALONE`, `ORGANIZATIONAL`. Определяет привязку к организации.
5. **WorkspaceLimits — VO** — лимиты (участники, проекты) для тарификации.
6. **Иерархия** — `parent_workspace_id` для вложенных workspace'ов.
7. **SSOMode — enum** — вместо `AccessMode` для SSO. `ONCE`, `EVERY_TIME`.
8. **Отдельные AR** — `Workspace`, `WorkspaceMembership`, `WorkspaceTeam`.

---

## 2. Доменная модель

### Value Objects

| VO | Тип | Описание |
|---|---|---|
| `WorkspaceStatus` | Enum | `ACTIVE`, `ARCHIVED`, `DELETED` |
| `WorkspaceType` | Enum | `STANDALONE`, `ORGANIZATIONAL` |
| `MemberSource` | Enum | `INVITATION`, `ORGANIZATION`, `DIRECT` |
| `InvitationStatus` | Enum | `PENDING`, `ACCEPTED`, `EXPIRED`, `REVOKED` |
| `SSOMode` | Enum | `ONCE`, `EVERY_TIME` |
| `AccentColor` | frozen dataclass | hex: str (validated `#RRGGBB`) |

#### VO Groups

```python
class WorkspacePersonalization:
    logo_url: Url | None
    icon_url: Url | None
    primary_color: AccentColor | None
    description: str | None  # до 500 символов

class SecurityPolicy:
    access_mode: AccessMode  # OPEN, PIN, PASSWORD, CORPORATE
    pin_hash: str | None = None  # hashed PIN (4-6 digits)
    password_hash: str | None = None
    ip_whitelist: list[str] = []  # CIDR notation
    corporate_sso_id: Id | None = None
    sso_mode: SSOMode | None = None

class MembershipPolicy:
    default_role_id: Id | None = None  # → WorkspaceRole
    allow_self_join: bool = False
    require_org_membership: bool = False  # для ORGANIZATIONAL

class WorkspaceLimits:
    max_members: int | None = None
    max_projects: int | None = None
```

```python
class AccessMode(str, Enum):
    OPEN = "open"
    PIN = "pin"
    PASSWORD = "password"
    CORPORATE = "corporate"
```

### Entities

| Сущность | Поля | Описание |
|---|---|---|
| `WorkspaceRole` | id, name, permissions: list[str], is_system: bool, description | Роль workspace (entity, не enum) |
| `WorkspaceMember` | id, user_id: Id, role_id: Id (→ WorkspaceRole), status: MemberStatus, source: MemberSource, joined_at, deactivated_at | Участник workspace |
| `WorkspaceInvitation` | id, email: str \| None, type: InvitationType, role_id: Id, token, status: InvitationStatus, max_uses, use_count, expires_at, message, invited_by, accepted_by, accepted_at | Приглашение |

```python
class MemberStatus(str, Enum):
    ACTIVE = "active"
    DEACTIVATED = "deactivated"

class InvitationType(str, Enum):
    EMAIL = "email"
    LINK = "link"
```

#### Предустановленные системные роли workspace

При создании workspace создаются `WorkspaceRole` с `is_system=True`:

| name | permissions | Описание |
|---|---|---|
| `owner` | `["*"]` | Полный контроль, удаление, передача владения |
| `admin` | `["manage_members", "manage_projects", "manage_settings"]` | Управление участниками, проектами, настройками |
| `moderator` | `["invite_members", "deactivate_members", "create_projects"]` | Приглашение, модерация, создание проектов |
| `member` | `["view_projects", "work_tasks"]` | Работа с задачами в назначенных проектах |

> Кастомные роли = `WorkspaceRole` с `is_system=False`.

### Aggregates

#### Workspace (Aggregate Root)

Поля:
- name: str (3–100 символов)
- slug: str (unique)
- status: WorkspaceStatus
- workspace_type: WorkspaceType
- organization_id: Id | None (opaque, из Organization BC)
- parent_workspace_id: Id | None (для иерархии)
- personalization: WorkspacePersonalization
- owner_id: Id
- security_policy: SecurityPolicy
- membership_policy: MembershipPolicy
- limits: WorkspaceLimits
- roles: list[WorkspaceRole]
- created_at: datetime
- updated_at: datetime
- archived_at: datetime | None
- deleted_at: datetime | None

Методы:
- `create(name, slug, owner_id, workspace_type, organization_id=None)` → `Workspace` (factory)
- `update_info(name=None, slug=None, personalization=None)`
- `archive()` / `restore()`
- `soft_delete()`
- `transfer_ownership(from_user_id, to_user_id)`
- `move_under_parent(parent_workspace_id)` / `detach_from_parent()`
- `update_security_policy(policy: SecurityPolicy)`
- `update_membership_policy(policy: MembershipPolicy)`
- `update_limits(limits: WorkspaceLimits)`
- `create_role(name, permissions, description=None)` → `WorkspaceRole`
- `update_role(role_id, permissions=None, description=None)`
- `delete_role(role_id)` — только `is_system=False`

Инварианты:
- Slug: для ORGANIZATIONAL — уникально в рамках организации; для STANDALONE — глобально
- Ровно 1 owner
- Системные роли нельзя удалить/переименовать
- ORGANIZATIONAL workspace: `organization_id` обязателен
- Иерархия: parent не может быть собственным потомком (no cycles)
- Архивация: workspace → read-only, все проекты архивируются
- Удаление: soft-delete, retention зависит от тарифа

#### WorkspaceMembership (Aggregate Root)

Поля:
- workspace_id: Id (opaque)
- members: list[WorkspaceMember]
- invitations: list[WorkspaceInvitation]
- created_at: datetime
- updated_at: datetime

Методы:
- `invite_by_email(email, role_id, invited_by, message=None, expires_in_days=7)`
- `invite_by_link(role_id, invited_by, max_uses=None, expires_in_hours=72)`
- `accept_invitation(token, user_id)` → `WorkspaceMember`
- `revoke_invitation(invitation_id)`
- `add_from_organization(user_ids, role_id, added_by)` — для ORGANIZATIONAL
- `change_member_role(member_id, new_role_id, changed_by)`
- `deactivate_member(member_id, deactivated_by)`
- `reactivate_member(member_id, reactivated_by)`
- `remove_member(member_id, removed_by)`

Инварианты:
- Нельзя пригласить уже участника
- Одновременно не более одного PENDING приглашения на email
- Для ORGANIZATIONAL: участник должен быть членом организации
- Нельзя назначить роль выше или равную своей (app-слой)
- Нельзя удалить/деактивировать последнего owner

#### WorkspaceTeam (Aggregate Root)

Поля:
- workspace_id: Id (opaque)
- name: str (уникально внутри workspace)
- description: str | None
- source: GroupSource (LOCAL | ORGANIZATION)
- source_group_id: Id | None
- members: list[TeamMember]
- created_by: Id
- created_at: datetime
- updated_at: datetime

Связанная entity:

```
TeamMember
├── id: Id
├── user_id: Id
├── role: TeamMemberRole (LEAD | MEMBER)
├── added_at: datetime
├── added_by: Id
```

```python
class GroupSource(str, Enum):
    LOCAL = "local"
    ORGANIZATION = "organization"
```

Методы:
- `create(workspace_id, name, created_by, description=None, source=LOCAL)` → `WorkspaceTeam`
- `import_from_organization(source_group_id)` — snapshot
- `update_info(name=None, description=None)`
- `add_member(user_id, role, added_by)`
- `remove_member(user_id)`
- `change_member_role(user_id, new_role)`
- `delete()`

Инварианты:
- Имя уникально внутри workspace
- Группы из организации = snapshot, не auto-sync

---

## 3. Бизнес-правила

1. **Slug уникальность**: для organizational — уникально в рамках организации; для standalone — глобально уникально
2. **Owner**: ровно 1 Owner в workspace
3. **Передача владения**: аналогично организации (подтверждение новым владельцем)
4. **Архивация**: workspace → read-only, все проекты архивируются; можно восстановить
5. **Удаление**: soft-delete; данные хранятся: Free 7 дней, Start 30 дней, Business 90 дней, Enterprise настраиваемо
6. **Участники organizational workspace**: должны быть членами организации
7. **Лимиты участников**: при достижении лимита — приглашения блокируются
8. **PIN/пароль**: хранятся в hashed виде; при 3 неверных попытках — блокировка на 5 минут
9. **IP-whitelist**: при несоответствии — доступ запрещён, логирование в audit
10. **Corporate access**: при корпоративном режиме — инициируется SSO-флоу организации
11. **Группы из организации**: sync = false (snapshot на момент копирования), можно обновить вручную
12. **Role hierarchy**: Owner > Admin > Moderator > Member
13. **Standalone workspace**: может быть привязан к организации позже (upgrade path)

---

## 4. API Endpoints

### 4.1. CRUD workspace

```
POST /api/v1/workspaces
```

**Request:**
```json
{
  "name": "Development Team",
  "slug": "dev-team",
  "description": "Main development workspace",
  "organization_id": "org_uuid_or_null"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "name": "Development Team",
  "slug": "dev-team",
  "description": "Main development workspace",
  "organization_id": "org_uuid_or_null",
  "owner_id": "current_user_uuid",
  "status": "active",
  "access_mode": "open",
  "created_at": "2025-01-01T00:00:00Z"
}
```

---

```
GET /api/v1/workspaces
```
*Список workspace текущего пользователя*

**Query params:** `page`, `limit`, `search`, `status`, `organization_id`

---

```
GET /api/v1/workspaces/{ws_id}
```

---

```
PATCH /api/v1/workspaces/{ws_id}
```

---

```
POST /api/v1/workspaces/{ws_id}/archive
```

---

```
POST /api/v1/workspaces/{ws_id}/restore
```

---

```
DELETE /api/v1/workspaces/{ws_id}
```

---

```
POST /api/v1/workspaces/{ws_id}/transfer-ownership
```

**Request:**
```json
{
  "new_owner_id": "user_uuid"
}
```

### 4.2. Безопасность

```
PUT /api/v1/workspaces/{ws_id}/security
```

**Request:**
```json
{
  "access_mode": "pin",
  "pin": "1234"
}
```

или

```json
{
  "access_mode": "corporate",
  "sso_configuration_id": "sso_uuid"
}
```

или

```json
{
  "access_mode": "open",
  "ip_whitelist": ["192.168.1.0/24", "10.0.0.0/8"]
}
```

---

```
POST /api/v1/workspaces/{ws_id}/verify-access
```
*Проверка PIN/пароля при входе в workspace*

**Request:**
```json
{
  "pin": "1234"
}
```

**Response (200):**
```json
{
  "workspace_access_token": "short_lived_token",
  "expires_in": 3600
}
```

### 4.3. Участники

```
GET /api/v1/workspaces/{ws_id}/members
```

**Query params:** `page`, `limit`, `search`, `role`, `status`, `group_id`

---

```
POST /api/v1/workspaces/{ws_id}/invitations
```

**Request (email):**
```json
{
  "type": "email",
  "emails": ["user@example.com"],
  "role": "member",
  "message": "Join our workspace!"
}
```

**Request (link):**
```json
{
  "type": "link",
  "role": "member",
  "max_uses": 20,
  "expires_in_hours": 72
}
```

---

```
GET /api/v1/workspaces/{ws_id}/invitations
```

---

```
DELETE /api/v1/workspaces/{ws_id}/invitations/{invitation_id}
```

---

```
POST /api/v1/workspaces/join/{token}
```

---

```
POST /api/v1/workspaces/{ws_id}/members/add-from-organization
```
*Быстрое добавление из организации (Business/Enterprise)*

**Request:**
```json
{
  "user_ids": ["uuid1", "uuid2"],
  "role": "member"
}
```

---

```
PUT /api/v1/workspaces/{ws_id}/members/{member_id}/role
```

---

```
POST /api/v1/workspaces/{ws_id}/members/{member_id}/deactivate
```

---

```
POST /api/v1/workspaces/{ws_id}/members/{member_id}/reactivate
```

---

```
DELETE /api/v1/workspaces/{ws_id}/members/{member_id}
```

### 4.4. Группы

```
POST /api/v1/workspaces/{ws_id}/groups
```

---

```
GET /api/v1/workspaces/{ws_id}/groups
```

---

```
POST /api/v1/workspaces/{ws_id}/groups/import-from-organization
```
*Импорт группы из организации*

**Request:**
```json
{
  "organization_group_id": "group_uuid"
}
```

---

```
PATCH /api/v1/workspaces/{ws_id}/groups/{group_id}
```

---

```
DELETE /api/v1/workspaces/{ws_id}/groups/{group_id}
```

---

```
POST /api/v1/workspaces/{ws_id}/groups/{group_id}/members
```

---

```
DELETE /api/v1/workspaces/{ws_id}/groups/{group_id}/members/{user_id}
```

### 4.5. Персонализация

```
PUT /api/v1/workspaces/{ws_id}/branding
```

**Request (multipart/form-data):**
- `logo` — файл логотипа
- `icon` — файл иконки
- `primary_color` — HEX-цвет

---

## 5. Схема БД

### Таблица: `workspaces`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| organization_id | UUID | FK → organizations.id, NULLABLE | NULL для standalone |
| name | VARCHAR(100) | NOT NULL | |
| slug | VARCHAR(100) | NOT NULL | |
| description | VARCHAR(500) | NULLABLE | |
| logo_url | VARCHAR(500) | NULLABLE | |
| icon_url | VARCHAR(500) | NULLABLE | |
| primary_color | VARCHAR(7) | NULLABLE | |
| owner_id | UUID | FK → users.id, NOT NULL | |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'active' | |
| access_mode | VARCHAR(30) | NOT NULL, DEFAULT 'open' | |
| security_settings | JSONB | NOT NULL, DEFAULT '{}' | PIN hash, password hash, IP whitelist, SSO ref |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| archived_at | TIMESTAMPTZ | NULLABLE | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

**Индексы:**
- `idx_ws_org_slug` — UNIQUE на `(organization_id, slug)` WHERE `organization_id IS NOT NULL`
- `idx_ws_slug_standalone` — UNIQUE на `slug` WHERE `organization_id IS NULL`
- `idx_ws_owner` — на `owner_id`
- `idx_ws_org` — на `organization_id`
- `idx_ws_status` — на `status`

### Таблица: `workspace_members`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| workspace_id | UUID | FK → workspaces.id, NOT NULL | |
| user_id | UUID | FK → users.id, NOT NULL | |
| role | VARCHAR(20) | NOT NULL | |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'active' | |
| added_from | VARCHAR(20) | NOT NULL, DEFAULT 'invitation' | |
| invited_by | UUID | FK → users.id, NULLABLE | |
| joined_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| deactivated_at | TIMESTAMPTZ | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_wm_ws_user` — UNIQUE на `(workspace_id, user_id)`
- `idx_wm_user` — на `user_id`

### Таблица: `workspace_invitations`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| workspace_id | UUID | FK → workspaces.id, NOT NULL | |
| email | VARCHAR(255) | NULLABLE | |
| type | VARCHAR(10) | NOT NULL | |
| role | VARCHAR(20) | NOT NULL | |
| token | VARCHAR(64) | UNIQUE, NOT NULL | |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | |
| max_uses | INTEGER | NULLABLE | |
| use_count | INTEGER | NOT NULL, DEFAULT 0 | |
| expires_at | TIMESTAMPTZ | NOT NULL | |
| message | TEXT | NULLABLE | |
| invited_by | UUID | FK → users.id, NOT NULL | |
| accepted_by | UUID | FK → users.id, NULLABLE | |
| accepted_at | TIMESTAMPTZ | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_wi_token` — UNIQUE на `token`
- `idx_wi_ws_email` — на `(workspace_id, email)` WHERE `status = 'pending'`

### Таблица: `workspace_groups`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| workspace_id | UUID | FK → workspaces.id, NOT NULL | |
| name | VARCHAR(100) | NOT NULL | |
| description | VARCHAR(500) | NULLABLE | |
| source | VARCHAR(20) | NOT NULL, DEFAULT 'local' | local/organization |
| source_group_id | UUID | NULLABLE | FK → organization_groups.id |
| created_by | UUID | FK → users.id, NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_wg_ws_name` — UNIQUE на `(workspace_id, name)`

### Таблица: `workspace_group_members`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| group_id | UUID | FK → workspace_groups.id, NOT NULL | |
| user_id | UUID | FK → users.id, NOT NULL | |
| role | VARCHAR(10) | NOT NULL, DEFAULT 'member' | |
| added_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| added_by | UUID | FK → users.id, NOT NULL | |

**Индексы:**
- `idx_wgm_group_user` — UNIQUE на `(group_id, user_id)`

---

## 6. Доменные события

| Событие | Поля | Описание |
|---|---|---|
| `WorkspaceCreated` | ws_id, name, slug, owner_id, workspace_type, organization_id | Workspace создан |
| `WorkspaceUpdated` | ws_id, changed_fields: list[str] | Информация обновлена |
| `WorkspaceArchived` | ws_id, archived_by | Архивирован |
| `WorkspaceRestored` | ws_id, restored_by | Восстановлен |
| `WorkspaceDeleted` | ws_id, deleted_by | Soft-delete |
| `WorkspaceOwnershipTransferred` | ws_id, from_user_id, to_user_id | Владение передано |
| `WorkspaceMovedUnderParent` | ws_id, parent_workspace_id | Перемещён в иерархии |
| `WorkspaceDetachedFromParent` | ws_id, old_parent_id | Отвязан от родителя |
| `SecurityPolicyUpdated` | ws_id, changed_fields: list[str] | Политика безопасности обновлена |
| `WorkspaceAccessVerified` | ws_id, user_id, method | Доступ подтверждён |
| `WorkspaceAccessDenied` | ws_id, user_id, reason, ip | Доступ отклонён |
| `WorkspaceRoleCreated` | ws_id, role_id, role_name | Кастомная роль создана |
| `WorkspaceRoleUpdated` | ws_id, role_id, changed_fields: list[str] | Роль обновлена |
| `WorkspaceRoleDeleted` | ws_id, role_id | Роль удалена |
| `WorkspaceMemberInvited` | ws_id, email, role_id, invited_by, type | Приглашение |
| `WorkspaceInviteLinkCreated` | ws_id, invitation_id, max_uses, expires_at | Ссылка-приглашение |
| `WorkspaceMemberJoined` | ws_id, user_id, role_id, source | Участник вступил |
| `WorkspaceMemberRoleChanged` | ws_id, user_id, old_role_id, new_role_id, changed_by | Роль изменена |
| `WorkspaceMemberDeactivated` | ws_id, user_id, deactivated_by | Деактивирован |
| `WorkspaceMemberReactivated` | ws_id, user_id, reactivated_by | Реактивирован |
| `WorkspaceMemberRemoved` | ws_id, user_id, removed_by | Удалён |
| `WorkspaceInvitationRevoked` | ws_id, invitation_id, revoked_by | Приглашение отозвано |
| `MembersAddedFromOrganization` | ws_id, user_ids, role_id, added_by | Добавлены из организации |
| `WorkspaceTeamCreated` | ws_id, team_id, name, source | Команда создана |
| `WorkspaceTeamUpdated` | ws_id, team_id, changed_fields: list[str] | Команда обновлена |
| `WorkspaceTeamDeleted` | ws_id, team_id | Команда удалена |
| `WorkspaceTeamMemberAdded` | ws_id, team_id, user_id, role | Участник добавлен |
| `WorkspaceTeamMemberRemoved` | ws_id, team_id, user_id | Участник убран |

---

## 7. Exceptions

| Исключение | Описание |
|---|---|
| `WorkspaceNotFoundException` | Workspace не найден |
| `DuplicateWorkspaceSlugException` | Slug уже занят |
| `WorkspaceMemberAlreadyExistsException` | Пользователь уже участник |
| `WorkspaceInvitationAlreadyPendingException` | Приглашение уже отправлено |
| `WorkspaceInvitationNotFoundException` | Приглашение не найдено |
| `WorkspaceInvitationExpiredException` | Приглашение истекло |
| `WorkspaceInvitationExhaustedException` | Ссылка исчерпана |
| `WorkspaceMemberNotFoundException` | Участник не найден |
| `CannotDeleteLastOwnerException` | Нельзя удалить последнего owner |
| `CannotChangeOwnRoleException` | Нельзя изменить свою роль |
| `InsufficientWorkspacePermissionException` | Недостаточно прав |
| `CannotDeleteSystemRoleException` | Нельзя удалить системную роль |
| `WorkspaceRoleNotFoundException` | Роль не найдена |
| `DuplicateWorkspaceRoleNameException` | Имя роли уже существует |
| `WorkspaceRoleInUseException` | Роль используется |
| `WorkspaceTeamNotFoundException` | Команда не найдена |
| `DuplicateTeamNameException` | Имя команды уже существует |
| `TeamMemberAlreadyExistsException` | Участник уже в команде |
| `WorkspaceMemberLimitExceededException` | Превышен лимит участников |
| `WorkspaceProjectLimitExceededException` | Превышен лимит проектов |
| `RequiresOrgMembershipException` | Участник должен быть членом организации |
| `WorkspaceAccessDeniedException` | Доступ к workspace запрещён |
| `InvalidPinException` | Неверный PIN |
| `InvalidPasswordException` | Неверный пароль workspace |
| `IpNotWhitelistedException` | IP не в whitelist |
| `WorkspaceHierarchyCycleException` | Циклическая зависимость в иерархии |

---

## 8. Repositories

| Репозиторий | Методы |
|---|---|
| `WorkspaceRepository` | `get_by_id`, `get_by_slug`, `get_by_owner`, `get_by_user`, `get_by_organization`, `get_children`, `search` |
| `WorkspaceMembershipRepository` | `get_by_ws_id`, `get_member`, `get_by_user_id`, `get_by_role`, `count_members`, `search` |
| `WorkspaceInvitationRepository` | `get_by_id`, `get_by_token`, `get_pending_by_email`, `get_by_ws`, `get_expired` |
| `WorkspaceTeamRepository` | `get_by_id`, `get_by_ws`, `get_by_name`, `get_by_member`, `search` |
| `WorkspaceRoleRepository` | `get_by_id`, `get_by_ws`, `get_system_roles`, `get_by_name` |

---

## 9. Интеграция с другими BC

| Событие | Целевой BC | Действие |
|---|---|---|
| `WorkspaceCreated` | FileStorage | Создать Storage для workspace |
| `WorkspaceDeleted` | Project | Архивировать все проекты |
| `OrgMemberJoined` (из Org BC) | Workspace | Добавить в workspace'ы организации |
| `OrgMemberRemoved` (из Org BC) | Workspace | Удалить из workspace'ов организации |
