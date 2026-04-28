# 03. Organization — Организации

## Обзор

Организация — верхний уровень мульти-тенантности для бизнес- и enterprise-клиентов. Организация объединяет workspace'ы, участников, SSO-настройки и хранилище. Для Free и Start тарифов организация не используется — пользователи работают напрямую с workspace.

**Доступность:** Business ✅ | Enterprise ✅ | Free ❌ | Start ❌

---

## Принципы расширяемости

1. **OrgRole — entity, не enum** — роли организации как сущности с `is_system` флагом. Предустановленные = `is_system=True`. Кастомные = запись, не правка домена.
2. **Policies — VO group** — `SecurityPolicy`, `MembershipPolicy` как группы настроек. Новые настройки = поле в VO.
3. **OrgPersonalization — VO group** — `logo_url`, `icon`, `primary_color`, `description` вынесены в один VO.
4. **SSOProvider — enum** — вместо `protocol: str`. Новые провайдеры = значение enum.
5. **StorageProvider — enum** — вместо `provider: str`. Новые провайдеры = значение enum.
6. **Credentials — по ссылке** — `encrypted_key_ref` / `encrypted_secret_ref` хранят vault-ссылки, не сами ключи.
7. **Отдельные AR** — `Organization`, `OrgMembership`, `Team` — независимые Aggregate Root'ы для лучшей изоляции.
8. **Department — entity** — организационная структура с иерархией.

---

## 1. Функциональные требования

### 1.1. Управление организацией

| Требование | Business | Enterprise |
|-----------|----------|------------|
| Создание организации | ✅ | ✅ |
| Изменение информации | ✅ | ✅ |
| Передача владения | ✅ | ✅ |
| Удаление организации | ✅ | ✅ |
| Несколько организаций | ⚡ 3 | ∞ |

**Правила:**
- Создатель организации автоматически становится Owner
- Передача владения требует подтверждения от нового владельца
- Удаление организации: soft-delete, данные хранятся 30 дней (Enterprise: настраиваемо)
- При удалении — все workspace'ы организации архивируются

### 1.2. Участники

| Требование | Business | Enterprise |
|-----------|----------|------------|
| Макс. участников | 100–500 | ∞ |
| Приглашение по email (одиночное) | ✅ | ✅ |
| Приглашение по email (массовое) | ✅ (до 50) | ✅ (до 500) |
| Приглашение по ссылке | ✅ | ✅ |
| Настройка срока ссылки | ✅ | ✅ |
| Лимит использований ссылки | ✅ | ✅ |
| Назначение/изменение ролей | ✅ | ✅ |
| Удаление/деактивация | ✅ | ✅ |
| Просмотр профилей | ✅ | ✅ |
| Группы/команды | ✅ | ✅ |

**Правила приглашений:**
- Приглашение по email: действует 7 дней (настраиваемо)
- Приглашение по ссылке: настраиваемый срок (1 час — 30 дней) и лимит (1–1000 или ∞)
- При вступлении через ссылку — назначается роль по умолчанию (Member)
- Массовое приглашение: CSV-файл или список email через запятую
- Деактивация: участник теряет доступ, но данные сохраняются

### 1.3. SSO

| Требование | Business | Enterprise |
|-----------|----------|------------|
| Добавление SSO-провайдера | ✅ (1) | ✅ (∞) |
| SAML 2.0 | ✅ | ✅ |
| Настройка domain mapping | ✅ | ✅ |
| Принудительный SSO | ❌ | ✅ |
| SCIM provisioning | ❌ | ✅ |
| LDAP / AD | ❌ | ✅ |

**Правила:**
- SSO привязывается к email-домену организации
- При принудительном SSO: пользователи с доменом организации не могут входить через пароль
- SCIM: автоматическая синхронизация пользователей из IdP

### 1.4. Персонализация

- Название организации (уникальное в системе, slug)
- Логотип (PNG/SVG, до 5 MB)
- Иконка (PNG/SVG, до 1 MB)
- Основной цвет (HEX)
- Описание (до 500 символов)

### 1.5. Управление хранилищем

| Требование | Business | Enterprise |
|-----------|----------|------------|
| Добавление S3-хранилища | ✅ | ✅ |
| Несколько хранилищ | ❌ | ✅ |
| Настройка (endpoint, bucket, credentials) | ✅ | ✅ |
| Тестирование подключения | ✅ | ✅ |
| Переключение между хранилищами | ❌ | ✅ |
| Миграция данных между хранилищами | ❌ | ✅ |

**Правила:**
- Поддерживаемые S3-совместимые провайдеры: AWS S3, MinIO, Yandex Object Storage, Selectel и т.д.
- Credentials хранятся зашифрованными (AES-256)
- При добавлении — обязательный health check (создание тестового файла)

### 1.6. Роли на уровне организации

| Роль | Описание |
|------|----------|
| **Owner** | Полный контроль, передача владения, удаление организации |
| **Admin** | Управление участниками, workspace, SSO, хранилищем |
| **Moderator** | Управление участниками (приглашение, деактивация), просмотр настроек |
| **Member** | Доступ к workspace'ам, в которые добавлен |

### Матрица прав (Organization)

| Действие | Owner | Admin | Moderator | Member |
|----------|-------|-------|-----------|--------|
| Изменить информацию организации | ✅ | ✅ | ❌ | ❌ |
| Удалить организацию | ✅ | ❌ | ❌ | ❌ |
| Передать владение | ✅ | ❌ | ❌ | ❌ |
| Управлять SSO | ✅ | ✅ | ❌ | ❌ |
| Управлять хранилищем | ✅ | ✅ | ❌ | ❌ |
| Приглашать участников | ✅ | ✅ | ✅ | ❌ |
| Удалять/деактивировать участников | ✅ | ✅ | ✅ | ❌ |
| Назначать роли (ниже своей) | ✅ | ✅ | ❌ | ❌ |
| Создавать workspace | ✅ | ✅ | ✅ | ❌ |
| Просматривать все workspace'ы | ✅ | ✅ | ✅ | ❌ |
| Просматривать участников | ✅ | ✅ | ✅ | ✅ |
| Управлять группами/командами | ✅ | ✅ | ✅ | ❌ |
| Просматривать аналитику | ✅ | ✅ | ⚡ | ❌ |
| Персонализация (лого, цвет) | ✅ | ✅ | ❌ | ❌ |

---

## 2. Доменная модель

### Value Objects

| VO | Тип | Описание |
|---|---|---|
| `OrgStatus` | Enum | `ACTIVE`, `SUSPENDED`, `DELETED` |
| `InvitationType` | Enum | `EMAIL`, `LINK` |
| `InvitationStatus` | Enum | `PENDING`, `ACCEPTED`, `EXPIRED`, `REVOKED` |
| `StorageProvider` | Enum | `AWS_S3`, `MINIO`, `YANDEX_OS`, `SELECTEL`, `CUSTOM_S3` |
| `SSOProvider` | Enum | `SAML2`, `OIDC_GOOGLE`, `OIDC_AZURE`, `OIDC_OKTA`, `OIDC_CUSTOM` |
| `AccentColor` | frozen dataclass | hex: str (validated `#RRGGBB`) |

#### VO Groups

```python
class OrgPersonalization:
    logo_url: Url | None
    icon: str | None
    primary_color: AccentColor | None
    description: str | None  # до 500 символов

class SecurityPolicy:
    require_2fa: bool = False
    enforce_sso: bool = False
    allowed_email_domains: list[str] | None = None
    password_policy_enabled: bool = False

class MembershipPolicy:
    default_role_id: Id | None = None  # → OrgRole
    allow_member_workspace_creation: bool = True
    max_members: int | None = None
    require_approval: bool = False

class StorageConfig:
    provider: StorageProvider
    endpoint: str
    bucket: str
    region: str | None
    encrypted_key_ref: str  # vault reference
    encrypted_secret_ref: str  # vault reference
```

### Entities

| Сущность | Поля | Описание |
|---|---|---|
| `OrgRole` | id, name, permissions: list[str], is_system: bool, description | Роль организации (entity, не enum) |
| `OrgMember` | id, user_id: Id, role_id: Id (→ OrgRole), status: MemberStatus, joined_at, deactivated_at | Участник организации |
| `Department` | id, name, parent_department_id: Id \| None, head_user_id: Id \| None, description | Отдел (иерархическая структура) |
| `SSOIntegration` | id, provider: SSOProvider, entity_id, sso_url, certificate_ref, email_domains: list[str], auto_provision: bool, default_role_id: Id, status: SsoStatus | SSO-интеграция |
| `StorageIntegration` | id, name, config: StorageConfig, is_default, status: StorageStatus, last_health_check_at | Интеграция хранилища |

```python
class MemberStatus(str, Enum):
    ACTIVE = "active"
    DEACTIVATED = "deactivated"

class SsoStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TESTING = "testing"

class StorageStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
```

#### Предустановленные системные роли организации

При создании организации создаются `OrgRole` с `is_system=True`:

| name | permissions | Описание |
|---|---|---|
| `owner` | `["*"]` | Полный контроль, передача владения, удаление |
| `admin` | `["manage_members", "manage_sso", "manage_storage", ...]` | Управление участниками, SSO, хранилищем |
| `moderator` | `["invite_members", "deactivate_members", "view_settings"]` | Приглашение, модерация участников |
| `member` | `["view_members"]` | Доступ к workspace'ам, в которые добавлен |

> Кастомные роли = `OrgRole` с `is_system=False`.

### Aggregates

#### Organization (Aggregate Root)

Поля:
- name: str (3–100 символов)
- slug: str (unique, lowercase, a-z0-9-)
- status: OrgStatus
- personalization: OrgPersonalization
- owner_ids: list[Id] — минимум один
- security_policy: SecurityPolicy
- membership_policy: MembershipPolicy
- roles: list[OrgRole]
- sso_integrations: list[SSOIntegration]
- storage_integrations: list[StorageIntegration]
- departments: list[Department]
- created_at: datetime
- updated_at: datetime
- deleted_at: datetime | None

Методы:
- `create(name, slug, owner_id)` → `Organization` (factory, status=ACTIVE)
- `update_info(name=None, slug=None, personalization=None)`
- `transfer_ownership(from_user_id, to_user_id)`
- `suspend()` / `reactivate()`
- `soft_delete()` / `restore()`
- `update_security_policy(policy: SecurityPolicy)`
- `update_membership_policy(policy: MembershipPolicy)`
- `create_role(name, permissions, description=None)` → `OrgRole`
- `update_role(role_id, permissions=None, description=None)`
- `delete_role(role_id)` — только `is_system=False`
- `add_sso_integration(integration: SSOIntegration)`
- `remove_sso_integration(sso_id)`
- `add_storage_integration(integration: StorageIntegration)`
- `remove_storage_integration(storage_id)` — не дефолтное
- `set_default_storage(storage_id)`
- `create_department(name, parent_id=None, head_user_id=None)`
- `remove_department(department_id)`

Инварианты:
- `slug` уникален в системе
- Минимум один `owner_id`
- Системные роли (`is_system=True`) нельзя удалить/переименовать
- Дефолтное хранилище нельзя удалить
- `SSOIntegration.email_domains` — домен привязан к одной организации
- При `security_policy.enforce_sso=True` — пользователи с доменом обязаны входить через SSO
- Удаление: soft-delete, данные хранятся 30 дней (Enterprise: настраиваемо)
- При удалении — все workspace'ы организации архивируются

#### OrgMembership (Aggregate Root)

Поля:
- organization_id: Id (opaque)
- members: list[OrgMember]
- invitations: list[OrgInvitation]
- created_at: datetime
- updated_at: datetime

Связанная entity:

```
OrgInvitation
├── id: Id
├── email: str | None — для email-приглашений
├── type: InvitationType
├── role_id: Id (→ OrgRole)
├── token: str — unique
├── status: InvitationStatus
├── max_uses: int | None — для ссылок
├── use_count: int
├── expires_at: datetime
├── message: str | None
├── invited_by: Id
├── accepted_by: Id | None
├── accepted_at: datetime | None
├── created_at: datetime
```

Методы:
- `invite_by_email(email, role_id, invited_by, message=None, expires_in_days=7)`
- `invite_by_link(role_id, invited_by, max_uses=None, expires_in_hours=168)`
- `accept_invitation(token, user_id)` → `OrgMember`
- `revoke_invitation(invitation_id)`
- `change_member_role(member_id, new_role_id, changed_by)`
- `deactivate_member(member_id, deactivated_by)`
- `reactivate_member(member_id, reactivated_by)`
- `remove_member(member_id, removed_by)`

Инварианты:
- Нельзя пригласить уже участника
- Одновременно не более одного PENDING приглашения на email
- Ссылка деактивируется при `use_count >= max_uses`
- Деактивированный участник теряет доступ ко всем workspace'ам
- Нельзя назначить роль выше или равную своей (проверка на app-слое)
- Нельзя удалить/деактивировать последнего owner

#### Team (Aggregate Root)

Поля:
- organization_id: Id (opaque)
- name: str (уникально внутри организации)
- description: str | None
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

Методы:
- `create(organization_id, name, created_by, description=None)` → `Team` (factory)
- `update_info(name=None, description=None)`
- `add_member(user_id, role, added_by)`
- `remove_member(user_id)`
- `change_member_role(user_id, new_role)`
- `delete()`

Инварианты:
- Имя команды уникально внутри организации
- `TeamMember` уникален по `user_id` внутри команды

---

## 3. Бизнес-правила

1. **Slug уникальность**: slug организации уникален в системе
2. **Owner**: ровно 1 Owner в организации
3. **Передача владения**: текущий Owner → выбирает нового → новый подтверждает → старый становится Admin
4. **Удаление**: только Owner; soft-delete, 30 дней retention; можно восстановить
5. **Приглашение по email**: нельзя пригласить уже участника; одновременно не более одного активного приглашения на email
6. **Приглашение по ссылке**: при достижении max_uses — автоматически деактивируется
7. **Деактивация участника**: теряет доступ ко всем workspace'ам организации
8. **SSO enforce**: при включении — пользователи с email-доменом организации обязаны входить через SSO
9. **SSO domain exclusivity**: email-домен может быть привязан только к одной организации
10. **Storage**: минимум одно хранилище (дефолтное) для организации; удаление возможно только если не дефолтное
11. **Группы**: название группы уникально внутри организации
12. **Role hierarchy**: Owner > Admin > Moderator > Member; нельзя назначить роль выше или равную своей

---

## 4. API Endpoints

### 4.1. CRUD организации

```
POST /api/v1/organizations
```

**Request:**
```json
{
  "name": "Acme Corp",
  "slug": "acme-corp",
  "description": "Software development company"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "name": "Acme Corp",
  "slug": "acme-corp",
  "description": "Software development company",
  "owner_id": "current_user_uuid",
  "status": "active",
  "created_at": "2025-01-01T00:00:00Z"
}
```

---

```
GET /api/v1/organizations
```
*Список организаций текущего пользователя*

---

```
GET /api/v1/organizations/{org_id}
```

---

```
PATCH /api/v1/organizations/{org_id}
```

**Request:**
```json
{
  "name": "Acme Corporation",
  "description": "Updated description",
  "primary_color": "#FF5733"
}
```

---

```
DELETE /api/v1/organizations/{org_id}
```
*Soft-delete (Owner only)*

---

```
POST /api/v1/organizations/{org_id}/restore
```
*Восстановление удалённой организации (в течение 30 дней)*

---

```
POST /api/v1/organizations/{org_id}/transfer-ownership
```

**Request:**
```json
{
  "new_owner_id": "user_uuid"
}
```

### 4.2. Участники

```
GET /api/v1/organizations/{org_id}/members
```

**Query params:** `page`, `limit`, `search`, `role`, `status`, `group_id`

---

```
POST /api/v1/organizations/{org_id}/invitations
```

**Request (email):**
```json
{
  "type": "email",
  "emails": ["user1@example.com", "user2@example.com"],
  "role": "member",
  "message": "Welcome to Acme Corp!"
}
```

**Request (link):**
```json
{
  "type": "link",
  "role": "member",
  "max_uses": 50,
  "expires_in_hours": 168
}
```

**Response (201, link):**
```json
{
  "id": "uuid",
  "invite_url": "https://app.taskflow.com/invite/org/TOKEN",
  "token": "TOKEN",
  "max_uses": 50,
  "expires_at": "2025-01-08T00:00:00Z"
}
```

---

```
GET /api/v1/organizations/{org_id}/invitations
```

---

```
DELETE /api/v1/organizations/{org_id}/invitations/{invitation_id}
```
*Отзыв приглашения*

---

```
POST /api/v1/organizations/join/{token}
```
*Принятие приглашения*

---

```
PUT /api/v1/organizations/{org_id}/members/{member_id}/role
```

**Request:**
```json
{
  "role": "moderator"
}
```

---

```
POST /api/v1/organizations/{org_id}/members/{member_id}/deactivate
```

---

```
POST /api/v1/organizations/{org_id}/members/{member_id}/reactivate
```

---

```
DELETE /api/v1/organizations/{org_id}/members/{member_id}
```
*Полное удаление участника*

### 4.3. Группы

```
POST /api/v1/organizations/{org_id}/groups
```

**Request:**
```json
{
  "name": "Backend Team",
  "description": "Backend developers"
}
```

---

```
GET /api/v1/organizations/{org_id}/groups
```

---

```
GET /api/v1/organizations/{org_id}/groups/{group_id}
```

---

```
PATCH /api/v1/organizations/{org_id}/groups/{group_id}
```

---

```
DELETE /api/v1/organizations/{org_id}/groups/{group_id}
```

---

```
POST /api/v1/organizations/{org_id}/groups/{group_id}/members
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
DELETE /api/v1/organizations/{org_id}/groups/{group_id}/members/{user_id}
```

### 4.4. SSO

```
POST /api/v1/organizations/{org_id}/sso
```

**Request:**
```json
{
  "provider_name": "Okta",
  "protocol": "saml2",
  "entity_id": "https://idp.okta.com/entity",
  "sso_url": "https://idp.okta.com/saml/login",
  "certificate": "-----BEGIN CERTIFICATE-----\n...",
  "email_domains": ["acme.com", "acme.ru"],
  "enforce_sso": false,
  "auto_provision": true,
  "default_role": "member"
}
```

---

```
GET /api/v1/organizations/{org_id}/sso
```

---

```
PATCH /api/v1/organizations/{org_id}/sso/{sso_id}
```

---

```
POST /api/v1/organizations/{org_id}/sso/{sso_id}/test
```
*Тестирование SSO-конфигурации*

---

```
POST /api/v1/organizations/{org_id}/sso/{sso_id}/deactivate
```

### 4.5. Хранилище

```
POST /api/v1/organizations/{org_id}/storage
```

**Request:**
```json
{
  "name": "Primary S3",
  "provider": "aws_s3",
  "endpoint": "https://s3.amazonaws.com",
  "bucket": "acme-taskflow",
  "region": "eu-west-1",
  "access_key": "AKIA...",
  "secret_key": "secret...",
  "is_default": true
}
```

---

```
GET /api/v1/organizations/{org_id}/storage
```

---

```
PATCH /api/v1/organizations/{org_id}/storage/{storage_id}
```

---

```
POST /api/v1/organizations/{org_id}/storage/{storage_id}/health-check
```

---

```
DELETE /api/v1/organizations/{org_id}/storage/{storage_id}
```

### 4.6. Персонализация

```
PUT /api/v1/organizations/{org_id}/branding
```

**Request (multipart/form-data):**
- `logo` — файл логотипа
- `icon` — файл иконки
- `primary_color` — HEX-цвет
- `name` — название

---

## 5. Схема БД

### Таблица: `organizations`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| name | VARCHAR(100) | NOT NULL | |
| slug | VARCHAR(100) | UNIQUE, NOT NULL | Lowercase, a-z0-9- |
| description | VARCHAR(500) | NULLABLE | |
| logo_url | VARCHAR(500) | NULLABLE | |
| icon | VARCHAR(500) | NULLABLE | |
| primary_color | VARCHAR(7) | NULLABLE | #RRGGBB |
| owner_id | UUID | FK → users.id, NOT NULL | |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'active' | |
| settings | JSONB | NOT NULL, DEFAULT '{}' | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| deleted_at | TIMESTAMPTZ | NULLABLE | Soft-delete |

**Индексы:**
- `idx_org_slug` — UNIQUE на `slug`
- `idx_org_owner` — на `owner_id`
- `idx_org_status` — на `status`

### Таблица: `organization_members`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| organization_id | UUID | FK → organizations.id, NOT NULL | |
| user_id | UUID | FK → users.id, NOT NULL | |
| role | VARCHAR(20) | NOT NULL | |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'active' | |
| invited_by | UUID | FK → users.id, NULLABLE | |
| joined_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| deactivated_at | TIMESTAMPTZ | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_om_org_user` — UNIQUE на `(organization_id, user_id)`
- `idx_om_user` — на `user_id`
- `idx_om_role` — на `(organization_id, role)`

### Таблица: `organization_invitations`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| organization_id | UUID | FK → organizations.id, NOT NULL | |
| email | VARCHAR(255) | NULLABLE | Для email-приглашений |
| type | VARCHAR(10) | NOT NULL | email/link |
| role | VARCHAR(20) | NOT NULL | Роль при вступлении |
| token | VARCHAR(64) | UNIQUE, NOT NULL | |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | |
| max_uses | INTEGER | NULLABLE | Для ссылок |
| use_count | INTEGER | NOT NULL, DEFAULT 0 | |
| expires_at | TIMESTAMPTZ | NOT NULL | |
| message | TEXT | NULLABLE | |
| invited_by | UUID | FK → users.id, NOT NULL | |
| accepted_by | UUID | FK → users.id, NULLABLE | |
| accepted_at | TIMESTAMPTZ | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_oi_token` — UNIQUE на `token`
- `idx_oi_org_email` — на `(organization_id, email)` WHERE `status = 'pending'`
- `idx_oi_expires` — на `expires_at`

### Таблица: `organization_groups`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| organization_id | UUID | FK → organizations.id, NOT NULL | |
| name | VARCHAR(100) | NOT NULL | |
| description | VARCHAR(500) | NULLABLE | |
| created_by | UUID | FK → users.id, NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_og_org_name` — UNIQUE на `(organization_id, name)`

### Таблица: `organization_group_members`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| group_id | UUID | FK → organization_groups.id, NOT NULL | |
| user_id | UUID | FK → users.id, NOT NULL | |
| role | VARCHAR(10) | NOT NULL, DEFAULT 'member' | lead/member |
| added_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| added_by | UUID | FK → users.id, NOT NULL | |

**Индексы:**
- `idx_ogm_group_user` — UNIQUE на `(group_id, user_id)`

### Таблица: `sso_configurations`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| organization_id | UUID | FK → organizations.id, NOT NULL | |
| provider_name | VARCHAR(100) | NOT NULL | |
| protocol | VARCHAR(10) | NOT NULL | saml2 |
| entity_id | VARCHAR(500) | NOT NULL | |
| sso_url | VARCHAR(500) | NOT NULL | |
| certificate | TEXT | NOT NULL | Encrypted |
| email_domains | JSONB | NOT NULL | ["acme.com"] |
| enforce_sso | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| auto_provision | BOOLEAN | NOT NULL, DEFAULT TRUE | |
| default_role | VARCHAR(20) | NOT NULL, DEFAULT 'member' | |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'inactive' | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_sso_org` — на `organization_id`
- `idx_sso_domains` — GIN на `email_domains`

### Таблица: `storage_integrations`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| organization_id | UUID | FK → organizations.id, NOT NULL | |
| name | VARCHAR(100) | NOT NULL | |
| provider | VARCHAR(20) | NOT NULL | |
| endpoint | VARCHAR(500) | NOT NULL | |
| bucket | VARCHAR(100) | NOT NULL | |
| region | VARCHAR(50) | NULLABLE | |
| access_key | TEXT | NOT NULL | Encrypted |
| secret_key | TEXT | NOT NULL | Encrypted |
| is_default | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'active' | |
| last_health_check_at | TIMESTAMPTZ | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Индексы:**
- `idx_si_org` — на `organization_id`
- `idx_si_org_default` — UNIQUE на `(organization_id)` WHERE `is_default = TRUE`

---

## 6. Доменные события

| Событие | Поля | Описание |
|---|---|---|
| `OrganizationCreated` | org_id, name, slug, owner_id | Организация создана |
| `OrganizationUpdated` | org_id, changed_fields: list[str] | Информация обновлена |
| `OrganizationSuspended` | org_id | Организация приостановлена |
| `OrganizationReactivated` | org_id | Организация реактивирована |
| `OrganizationDeleted` | org_id, deleted_by | Soft-delete |
| `OrganizationRestored` | org_id, restored_by | Восстановлена |
| `OwnershipTransferred` | org_id, from_user_id, to_user_id | Владение передано |
| `SecurityPolicyUpdated` | org_id, changed_fields: list[str] | Политика безопасности обновлена |
| `MembershipPolicyUpdated` | org_id, changed_fields: list[str] | Политика участников обновлена |
| `OrgRoleCreated` | org_id, role_id, role_name | Кастомная роль создана |
| `OrgRoleUpdated` | org_id, role_id, changed_fields: list[str] | Роль обновлена |
| `OrgRoleDeleted` | org_id, role_id | Роль удалена |
| `OrgMemberInvited` | org_id, email, role_id, invited_by, type | Приглашение отправлено |
| `OrgInviteLinkCreated` | org_id, invitation_id, max_uses, expires_at | Ссылка-приглашение создана |
| `OrgMemberJoined` | org_id, user_id, role_id, invitation_id | Участник вступил |
| `OrgMemberRoleChanged` | org_id, user_id, old_role_id, new_role_id, changed_by | Роль изменена |
| `OrgMemberDeactivated` | org_id, user_id, deactivated_by | Участник деактивирован |
| `OrgMemberReactivated` | org_id, user_id, reactivated_by | Участник реактивирован |
| `OrgMemberRemoved` | org_id, user_id, removed_by | Участник удалён |
| `OrgInvitationRevoked` | org_id, invitation_id, revoked_by | Приглашение отозвано |
| `TeamCreated` | org_id, team_id, name, created_by | Команда создана |
| `TeamUpdated` | org_id, team_id, changed_fields: list[str] | Команда обновлена |
| `TeamDeleted` | org_id, team_id, deleted_by | Команда удалена |
| `TeamMemberAdded` | org_id, team_id, user_id, role, added_by | Участник добавлен в команду |
| `TeamMemberRemoved` | org_id, team_id, user_id, removed_by | Участник убран из команды |
| `DepartmentCreated` | org_id, department_id, name | Отдел создан |
| `DepartmentDeleted` | org_id, department_id | Отдел удалён |
| `SsoIntegrationCreated` | org_id, sso_id, provider, email_domains | SSO добавлено |
| `SsoIntegrationUpdated` | org_id, sso_id, changed_fields: list[str] | SSO обновлено |
| `SsoIntegrationActivated` | org_id, sso_id | SSO активировано |
| `SsoIntegrationDeactivated` | org_id, sso_id | SSO деактивировано |
| `OrgStorageAdded` | org_id, storage_id, provider, bucket | Хранилище добавлено |
| `OrgStorageUpdated` | org_id, storage_id, changed_fields: list[str] | Хранилище обновлено |
| `OrgStorageRemoved` | org_id, storage_id | Хранилище удалено |
| `OrgStorageSetDefault` | org_id, storage_id, previous_default_id | Хранилище назначено дефолтным |
| `StorageHealthCheckPassed` | org_id, storage_id | Health check пройден |
| `StorageHealthCheckFailed` | org_id, storage_id, error | Health check не пройден |

---

## 7. Exceptions

| Исключение | Описание |
|---|---|
| `OrganizationNotFoundException` | Организация не найдена |
| `DuplicateOrgSlugException` | Slug уже занят |
| `CannotDeleteLastOwnerException` | Нельзя удалить последнего owner |
| `OrgMemberAlreadyExistsException` | Пользователь уже участник |
| `OrgInvitationAlreadyPendingException` | Приглашение уже отправлено |
| `OrgInvitationNotFoundException` | Приглашение не найдено |
| `OrgInvitationExpiredException` | Приглашение истекло |
| `OrgInvitationExhaustedException` | Ссылка-приглашение исчерпана |
| `OrgMemberNotFoundException` | Участник не найден |
| `CannotChangeOwnRoleException` | Нельзя изменить свою роль |
| `InsufficientOrgPermissionException` | Недостаточно прав |
| `CannotDeleteSystemRoleException` | Нельзя удалить системную роль |
| `OrgRoleNotFoundException` | Роль не найдена |
| `DuplicateOrgRoleNameException` | Имя роли уже существует |
| `OrgRoleInUseException` | Роль используется участниками |
| `TeamNotFoundException` | Команда не найдена |
| `DuplicateTeamNameException` | Имя команды уже существует |
| `TeamMemberAlreadyExistsException` | Участник уже в команде |
| `SsoIntegrationNotFoundException` | SSO-интеграция не найдена |
| `DuplicateEmailDomainException` | Домен уже привязан к организации |
| `StorageIntegrationNotFoundException` | Хранилище не найдено |
| `CannotRemoveDefaultStorageException` | Нельзя удалить дефолтное хранилище |
| `StorageHealthCheckFailedException` | Health check хранилища не пройден |
| `DepartmentNotFoundException` | Отдел не найден |
| `OrgMemberLimitExceededException` | Превышен лимит участников |

---

## 8. Repositories

| Репозиторий | Методы |
|---|---|
| `OrganizationRepository` | `get_by_id`, `get_by_slug`, `get_by_owner`, `get_by_user`, `search` |
| `OrgMembershipRepository` | `get_by_org_id`, `get_member`, `get_by_user_id`, `get_by_role`, `count_members`, `search` |
| `OrgInvitationRepository` | `get_by_id`, `get_by_token`, `get_pending_by_email`, `get_by_org`, `get_expired` |
| `TeamRepository` | `get_by_id`, `get_by_org`, `get_by_name`, `get_by_member`, `search` |
| `OrgRoleRepository` | `get_by_id`, `get_by_org`, `get_system_roles`, `get_by_name` |
| `DepartmentRepository` | `get_by_id`, `get_by_org`, `get_children`, `get_by_head` |

## 9. Интеграция с другими BC

| Событие | Целевой BC | Действие |
|---|---|---|
| `OrganizationCreated` | Billing | Создать подписку (FREE) |
| `OrgMemberJoined` | Workspace | Добавить в workspace'ы организации |
| `OrgMemberRemoved` | Workspace | Удалить из workspace'ов организации |
| `OrgStorageAdded` | FileStorage | Создать Storage |
| `OrganizationDeleted` | Workspace | Архивировать все workspace'ы |
