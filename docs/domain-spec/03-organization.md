# Organization BC — Спецификация

> Путь: `app/context/organization/domain`
> Исходные требования: §3 (Организации)

## Контекст

Organization BC отвечает за создание и управление организациями: участники, команды, департаменты, приглашения, SSO, хранилище, персонализацию, орг-политики и роли на уровне организации.

---

## Принципы расширяемости

1. **Роли — entity, не enum** — `OrgRole` хранится как запись с permissions. Кастомные роли без изменения домена.
2. **Разделение AR** — Organization (ядро) + OrgMembership (члены) + Team (команды) + Invitation (приглашения). Каждый AR развивается независимо.
3. **Политики — VO-группы** — `SecurityPolicy`, `MembershipPolicy` как расширяемые группы. Новое правило = поле в VO.
4. **Events по группам** — `changed_fields` для детализации, как в Profile BC.
5. **Магические строки → enum или валидированные типы** — `InvitationStatus`, `StorageProvider`, `SSOProvider`.

---

## Value Objects

### Общие

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `OrgStatus` | Enum | `ACTIVE`, `SUSPENDED`, `PENDING_DELETION` | §3.1 |
| `InvitationStatus` | Enum | `PENDING`, `ACCEPTED`, `DECLINED`, `EXPIRED`, `REVOKED` | §3.2 |
| `StorageProvider` | Enum | `AWS_S3`, `MINIO`, `LOCAL`, `AZURE_BLOB`, `GCS` | §3.5 |
| `SSOProvider` | Enum | `SAML`, `OIDC`, `LDAP` | §3.3 |
| `AccentColor` | frozen dataclass | hex: str (validated #RRGGBB) | §3.4 |
| `InvitationToken` | frozen dataclass | value: str, expires_at: datetime \| None, max_uses: int \| None, used_count: int | §3.2 |

### OrgPersonalization (VO group)

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `OrgPersonalization` | frozen dataclass | color: AccentColor, icon_url: Url \| None, display_name: str \| None, custom_domain: str \| None, branding: OrgBranding \| None | §3.4 |
| `OrgBranding` | frozen dataclass | logo_url: Url \| None, favicon_url: Url \| None, custom_css: str \| None, login_message: str \| None | §3.4 |

> **Расширение персонализации** — добавление новых полей (custom_js, watermark, email_templates) = поле в `OrgBranding` или `OrgPersonalization`, без нового event.

### SecurityPolicy (VO group)

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `SecurityPolicy` | frozen dataclass | require_2fa: bool, password_min_length: int, session_timeout_minutes: int \| None, ip_allowlist: list[str], domain_restrictions: list[str], require_email_verification: bool | §3.3 |

> **Расширение политик** — новые правила (max_session_count, require_sso_for_admins, password_rotation_days) = поле в `SecurityPolicy`. Групповой event покрывает.

### MembershipPolicy (VO group)

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `MembershipPolicy` | frozen dataclass | allow_invitation_links: bool, default_role: str, require_approval: bool, max_members: int \| None, allowed_email_domains: list[str] | §3.2 |

> **`require_approval`** — если True, приглашения требуют подтверждения владельцем/админом. **`allowed_email_domains`** — ограничение доменов для приглашений (например, только @company.com).

### StorageConfig (VO group)

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `StorageConfig` | frozen dataclass | provider: StorageProvider, endpoint: Url, bucket: str, region: str, access_key: str (encrypted) | §3.5 |
| `StorageQuota` | frozen dataclass | max_bytes: int, used_bytes: int, max_file_size_bytes: int \| None, allowed_extensions: list[str] \| None | §3.5 |

### SSOConfig (VO group)

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `SSOConfig` | frozen dataclass | provider: SSOProvider, entity_id: str, sso_url: Url, certificate: str (encrypted), is_active: bool, group_mapping: dict[str, str] \| None, attribute_mapping: dict[str, str] \| None | §3.3 |

> **`group_mapping`** — маппинг групп IdP на орг-роли (например, "admins" → "admin"). **`attribute_mapping`** — маппинг атрибутов SSO на поля профиля. Оба расширяемы без изменения структуры.

## Entities

| Сущность | Поля | Описание | Исходное требование |
|---|---|---|---|
| `OrgMember` | user_id: Id, display_name: str \| None, role: OrgRole (entity ref), joined_at: datetime, is_active: bool, invited_by: Id \| None | Участник организации | §3.2 |
| `OrgRole` | name: str, permissions: list[str], is_system: bool, description: str \| None, scope: OrgRoleScope | Роль организации (системная или кастомная) | §3.6 |
| `Department` | name: str, parent_id: Id \| None, lead_id: Id \| None, member_ids: list[Id], is_active: bool | Подразделение / департамент | §3.2 |
| `SSOIntegration` | config: SSOConfig, added_at: datetime, added_by: Id | SSO-интеграция организации | §3.3 |
| `StorageIntegration` | config: StorageConfig, quota: StorageQuota | Хранилище организации | §3.5 |

> **`OrgRole` — entity, не enum** — системные роли (owner, admin, moderator, member) — предустановленные записи с `is_system=True`. Кастомные роли создаются админами организации с `is_system=False`. Это открывает RBAC на уровне организации.

### OrgRoleScope Enum

| Значение | Описание |
|---|---|
| `ORG` | Роль действует на всю организацию |
| `DEPARTMENT` | Роль действует на подразделение |
| `TEAM` | Роль действует на команду |

> **`OrgRoleScope`** — позволяет назначать роли на разных уровнях: админ департамента, модератор команды. Новые scope добавляются по мере роста модели.

## Domain Events

| Событие | Поля | Описание | Исходное требование |
|---|---|---|---|
| `OrganizationCreated` | org_id, owner_id, name | Организация создана | §3.1 |
| `OrganizationInfoChanged` | org_id, changed_fields: list[str] | Информация обновлена | §3.1 |
| `OrganizationSuspended` | org_id, reason | Организация приостановлена | §3.1 |
| `OrganizationReactivated` | org_id | Организация реактивирована | §3.1 |
| `OrganizationDeletionRequested` | org_id | Запрос удаления организации | §3.1 |
| `OwnershipTransferred` | org_id, old_owner_id, new_owner_id | Владение передано | §3.1 |
| `OrgMemberJoined` | org_id, user_id, role | Участник присоединился | §3.2 |
| `OrgMemberDisplayNameChanged` | org_id, user_id, display_name | Отображаемое имя участника изменено | §3.2 |
| `OrgMemberRoleChanged` | org_id, user_id, new_role | Роль участника изменена | §3.2 |
| `OrgMemberRemoved` | org_id, user_id | Участник удалён | §3.2 |
| `OrgMemberDeactivated` | org_id, user_id | Участник деактивирован | §3.2 |
| `OrgMemberReactivated` | org_id, user_id | Участник реактивирован | §3.2 |
| `OrgRoleCreated` | org_id, role_name | Кастомная роль создана | §3.6 |
| `OrgRoleUpdated` | org_id, role_name | Роль обновлена | §3.6 |
| `OrgRoleDeleted` | org_id, role_name | Кастомная роль удалена | §3.6 |
| `InvitationSent` | org_id, email, role | Приглашение отправлено | §3.2 |
| `InvitationAccepted` | org_id, user_id | Приглашение принято | §3.2 |
| `InvitationDeclined` | org_id, email | Приглашение отклонено | §3.2 |
| `InvitationRevoked` | org_id, invitation_id | Приглашение отозвано | §3.2 |
| `InvitationLinkGenerated` | org_id, token | Ссылка-приглашение сгенерирована | §3.2 |
| `SSOIntegrationAdded` | org_id, provider | SSO добавлен | §3.3 |
| `SSOIntegrationUpdated` | org_id, provider | SSO обновлён | §3.3 |
| `SSOIntegrationDeactivated` | org_id, provider | SSO деактивирован | §3.3 |
| `OrgPersonalizationChanged` | org_id, changed_fields: list[str] | Персонализация изменена | §3.4 |
| `SecurityPolicyChanged` | org_id, changed_fields: list[str] | Политика безопасности изменена | §3.3 |
| `MembershipPolicyChanged` | org_id, changed_fields: list[str] | Политика членства изменена | §3.2 |
| `OrgStorageAdded` | org_id, storage_id | Хранилище добавлено | §3.5 |
| `OrgStorageUpdated` | org_id, changed_fields: list[str] | Хранилище обновлено | §3.5 |
| `OrgStorageQuotaExceeded` | org_id | Квота хранилища превышена | §3.5 |
| `TeamCreated` | org_id, team_id | Команда создана | §3.2 |
| `TeamUpdated` | org_id, team_id, changed_fields: list[str] | Команда обновлена | §3.2 |
| `TeamDeleted` | org_id, team_id | Команда удалена | §3.2 |
| `TeamMemberAdded` | org_id, team_id, user_id | Участник добавлен в команду | §3.2 |
| `TeamMemberRemoved` | org_id, team_id, user_id | Участник удалён из команды | §3.2 |
| `DepartmentCreated` | org_id, department_id | Подразделение создано | §3.2 |
| `DepartmentUpdated` | org_id, department_id, changed_fields: list[str] | Подразделение обновлено | §3.2 |
| `DepartmentDeleted` | org_id, department_id | Подразделение удалено | §3.2 |
| `DepartmentMemberAdded` | org_id, department_id, user_id | Участник добавлен в подразделение | §3.2 |
| `DepartmentMemberRemoved` | org_id, department_id, user_id | Участник удалён из подразделения | §3.2 |

## Exceptions

| Исключение | Описание |
|---|---|
| `OrganizationNotFoundException` | Организация не найдена |
| `OrganizationSuspendedException` | Организация приостановлена |
| `OrgMemberNotFoundException` | Участник организации не найден |
| `OrgRoleNotFoundException` | Роль не найдена |
| `OrgRoleInUseException` | Роль используется, нельзя удалить |
| `CannotRemoveOwnerException` | Нельзя удалить владельца |
| `CannotRemoveLastOwnerException` | Нельзя удалить последнего владельца |
| `CannotTransferOwnershipException` | Нельзя передать владение |
| `TeamNotFoundException` | Команда не найдена |
| `DepartmentNotFoundException` | Подразделение не найдена |
| `CircularDepartmentException` | Циклическая ссылка в иерархии подразделений |
| `InvitationNotFoundException` | Приглашение не найдено |
| `InvitationExpiredException` | Приглашение истекло |
| `InvitationLinkExpiredException` | Ссылка-приглашение истекла |
| `InvitationLinkMaxUsesExceededException` | Лимит использований ссылки исчерпан |
| `DuplicateInvitationException` | Приглашение уже отправлено |
| `MembershipLimitExceededException` | Лимит участников превышен |
| `EmailDomainNotAllowedException` | Домен email не разрешён политикой |
| `SSOProviderAlreadyExistsException` | SSO-провайдер уже настроен |
| `StorageQuotaExceededException` | Квота хранилища превышена |
| `SecurityPolicyViolationException` | Нарушение политики безопасности |

## Aggregates

### Organization (Aggregate Root)

Ядро организации — идентичность, статус, владельцы, политики. Не содержит списки членов/команд (это отдельные AR). Связь через `org_id` (opaque ID).

Поля:
- name: str
- status: OrgStatus
- personalization: OrgPersonalization
- owner_ids: list[Id]  — один или несколько владельцев
- security_policy: SecurityPolicy
- membership_policy: MembershipPolicy
- storage: StorageIntegration | None
- sso_integrations: list[SSOIntegration]
- created_at: datetime
- updated_at: datetime

Методы:
- `create(name, owner_id)` → `Organization` (factory)
- `update_info(name=None, personalization=None)`
- `transfer_ownership(from_id, to_id)`
- `add_owner(user_id)` — со-владелец
- `remove_owner(user_id)` — минимум один владелец
- `suspend(reason)`
- `reactivate()`
- `request_deletion()`
- `update_security_policy(policy: SecurityPolicy)`
- `update_membership_policy(policy: MembershipPolicy)`
- `add_sso_integration(config: SSOConfig)`
- `update_sso_integration(provider: SSOProvider, config: SSOConfig)`
- `deactivate_sso_integration(provider: SSOProvider)`
- `add_storage(config: StorageConfig, quota: StorageQuota)`
- `update_storage(config=None, quota=None)`
- `create_role(name, permissions, scope, description=None)` — кастомная роль
- `update_role(name, permissions=None, description=None)`
- `delete_role(name)` — только кастомные

Инварианты:
- Минимум один владелец
- `OrgStatus.SUSPENDED` блокирует все действия кроме `reactivate`
- `OrgStatus.PENDING_DELETION` блокирует все действия
- Нельзя удалить системную роль (`is_system=True`)
- Нельзя удалить роль если она используется участниками
- SSO-интеграции уникальны по provider
- Security policy: `require_2fa` проверяется при входе (через event → Identity BC)

### OrgMembership (Aggregate Root)

Управление участниками организации. Отдельный AR для масштабируемости — тысячи членов не загружаются в Organization.

Поля:
- org_id: Id (opaque)
- members: list[OrgMember]
- departments: list[Department]
- invitations: list[Invitation]

Методы:
- `create(org_id, owner_id)` → `OrgMembership` (factory)
- `add_member(user_id, role, invited_by=None, display_name=None)` — прямой добавление
- `remove_member(user_id)`
- `deactivate_member(user_id)`
- `reactivate_member(user_id)`
- `change_member_role(user_id, new_role)`
- `update_member_display_name(user_id, display_name)` — установить никнейм/ФИО в рамках организации
- `invite_member(email, role)` — email-приглашение
- `invite_members_bulk(emails, role)` — массовое
- `generate_invitation_link(role, expires_at=None, max_uses=None)`
- `accept_invitation(token, user_id)`
- `decline_invitation(token)`
- `revoke_invitation(invitation_id)`
- `create_department(name, parent_id=None, lead_id=None)`
- `update_department(department_id, name=None, lead_id=None)`
- `delete_department(department_id)`
- `add_department_member(department_id, user_id)`
- `remove_department_member(department_id, user_id)`

Инварианты:
- Владелец не может быть удалён/деактивирован — сначала снять роль
- Приглашение уникально по email в рамках организации
- Invitation link: опциональные expires_at и max_uses
- Департамент не может быть своим предком (нет циклов)
- Участник должен быть членом организации для добавления в департамент
- `MembershipPolicy.max_members` проверяется при добавлении
- `MembershipPolicy.allowed_email_domains` проверяется при приглашении
- `MembershipPolicy.require_approval` — приглашения в статусе PENDING до подтверждения

### Team (Aggregate Root)

Команда — самостоятельный AR. Связан с организацией через `org_id`.

Поля:
- org_id: Id (opaque)
- name: str
- description: str | None
- lead_id: Id | None
- member_ids: list[Id]
- icon_url: Url | None
- is_active: bool
- created_at: datetime
- updated_at: datetime

Методы:
- `create(org_id, name, lead_id=None)` → `Team` (factory)
- `update(name=None, description=None, lead_id=None, icon_url=None)`
- `add_member(user_id)`
- `remove_member(user_id)`
- `deactivate()`
- `reactivate()`

Инварианты:
- Участник команды должен быть членом организации (проверка на app-слое через ACL)
- lead_id должен быть членом команды
- Неактивная команда не может принимать участников

### Invitation (Entity внутри OrgMembership)

Поля:
- id: Id
- email: Email | None — для email-приглашений
- link: InvitationToken | None — для link-приглашений
- role: OrgRole (entity ref)
- invited_by: Id
- invited_at: datetime
- status: InvitationStatus
- approved_by: Id | None — для require_approval

> **Два типа приглашений**: Email-приглашение (`email` заполнен, `link=None`) и link-приглашение (`link` заполнен, `email=None`). Единая сущность, но разные workflow.

## Repositories

| Репозиторий | Методы |
|---|---|
| `OrganizationRepository` | `get_by_id`, `get_by_owner`, `get_by_sso_domain`, `search` |
| `OrgMembershipRepository` | `get_by_org_id`, `get_member_by_org_and_user`, `get_members_by_org`, `get_departments_by_org`, `get_invitations_by_org`, `get_invitation_by_token` |
| `TeamRepository` | `get_by_id`, `get_by_org`, `get_by_member`, `get_by_lead` |
| `OrgRoleRepository` | `get_by_id`, `get_by_name`, `get_system_roles`, `get_by_org`, `search` |

## Предустановленные системные роли

При создании организации создаются 4 записи `OrgRole` с `is_system=True`:

| name | permissions | scope | Описание |
|---|---|---|---|
| `owner` | `org.*` | ORG | Полный доступ, управление владельцами |
| `admin` | `org.settings.*`, `members.*`, `teams.*`, `departments.*`, `content.*` | ORG | Управление организацией |
| `moderator` | `members.read`, `members.invite`, `content.*`, `teams.*` | ORG | Ограниченное управление |
| `member` | `self.*`, `content.read`, `teams.read` | ORG | Базовый доступ |

> Кастомные роли создаются админами/владельцами организации с `is_system=False`. Примеры: `guest` (только чтение), `contractor` (ограниченный доступ с сроком), `auditor` (только просмотр логов).
