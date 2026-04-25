# Проверки разрешений в Organization Context

## Обзор механизма авторизации

Авторизация в Organization Context реализована через порт `OrgPermissionCheckerPort` с двумя методами:

- **`require_permission(user_id, org_id, permission)`** — проверяет разрешение и выбрасывает `InsufficientOrgPermissionsException` при отсутствии. Используется в большинстве commands и queries.
- **`has_permission(user_id, org_id, permission)`** — возвращает `bool`, используется для фильтрации результатов (когда отсутствие разрешения не является ошибкой).

Поддерживаются wildcard-разрешения:
- `org.*` — полный доступ в организации (владелец)
- `members.*` — все разрешения в группе `members`
- `members.write` — конкретное разрешение

Каждый handler определяет константу `REQUIRED_PERMISSION` — требуемое разрешение для выполнения операции.

---

## Commands

### Команды без проверки разрешений

| Команда | Handler | Описание |
|---|---|---|
| `AcceptInvitationCommand` | `AcceptInvitationHandler` | Принятие приглашения. Доступно любому аутентифицированному пользователю по `invitation_id`. Проверяется только существование пользователя через `IdentityUserPort`. |
| `DeclineInvitationCommand` | `DeclineInvitationHandler` | Отклонение приглашения. Доступно без проверки роли. |
| `CreateOrganizationCommand` | `CreateOrganizationHandler` | Создание организации. Доступно любому аутентифицированному пользователю. Проверяется существование пользователя через `IdentityUserPort`. |

### Команды с проверкой разрешений

| Команда | Handler | REQUIRED_PERMISSION | Дополнительные проверки |
|---|---|---|---|
| `AddDepartmentMemberCommand` | `AddDepartmentMemberHandler` | `departments.write` | Проверяется, что добавляемый пользователь является членом организации |
| `AddOrgMemberCommand` | `AddOrgMemberHandler` | `members.write` | Проверка существования пользователя через `IdentityUserPort`; проверка на дубликат членства; резолв `role_id` из `MembershipPolicy` если не указан |
| `AddOrgOwnerCommand` | `AddOrgOwnerHandler` | `org.*` | — |
| `AddOrgStorageCommand` | `AddOrgStorageHandler` | `org.settings.write` | — |
| `AddSSOIntegrationCommand` | `AddSSOIntegrationHandler` | `org.settings.write` | — |
| `AddTeamMemberCommand` | `AddTeamMemberHandler` | `teams.write` | Проверяется, что добавляемый пользователь является членом организации |
| `ChangeOrgMemberRoleCommand` | `ChangeOrgMemberRoleHandler` | `members.write` | — |
| `CreateDepartmentCommand` | `CreateDepartmentHandler` | `departments.write` | — |
| `CreateOrgRoleCommand` | `CreateOrgRoleHandler` | `roles.write` | — |
| `CreateTeamCommand` | `CreateTeamHandler` | `teams.write` | — |
| `DeactivateOrgMemberCommand` | `DeactivateOrgMemberHandler` | `members.write` | Проверяется, является ли деактивируемый пользователь владельцем (`is_owner`) — влияет на логику деактивации |
| `DeactivateSSOIntegrationCommand` | `DeactivateSSOIntegrationHandler` | `org.settings.write` | — |
| `DeactivateTeamCommand` | `DeactivateTeamHandler` | `teams.write` | — |
| `DeleteDepartmentCommand` | `DeleteDepartmentHandler` | `departments.write` | — |
| `DeleteOrgRoleCommand` | `DeleteOrgRoleHandler` | `roles.write` | Домен гарантирует, что системные роли нельзя удалить |
| `GenerateInvitationLinkCommand` | `GenerateInvitationLinkHandler` | `members.invite` | — |
| `ReactivateOrgMemberCommand` | `ReactivateOrgMemberHandler` | `members.write` | — |
| `ReactivateOrganizationCommand` | `ReactivateOrganizationHandler` | `org.settings.write` | — |
| `ReactivateTeamCommand` | `ReactivateTeamHandler` | `teams.write` | — |
| `RemoveDepartmentMemberCommand` | `RemoveDepartmentMemberHandler` | `departments.write` | — |
| `RemoveOrgMemberCommand` | `RemoveOrgMemberHandler` | `members.write` | Проверяется, является ли удаляемый пользователь владельцем (`is_owner`) — влияет на логику удаления |
| `RemoveOrgOwnerCommand` | `RemoveOrgOwnerHandler` | `org.*` | Домен гарантирует, что минимум один владелец останется |
| `RemoveTeamMemberCommand` | `RemoveTeamMemberHandler` | `teams.write` | — |
| `RequestOrganizationDeletionCommand` | `RequestOrganizationDeletionHandler` | `org.settings.write` | — |
| `RevokeInvitationCommand` | `RevokeInvitationHandler` | `members.invite` | — |
| `SendBulkInvitationsCommand` | `SendBulkInvitationsHandler` | `members.invite` | Пропускаются дубликаты email среди pending-приглашений |
| `SendInvitationCommand` | `SendInvitationHandler` | `members.invite` | Проверка на дубликат pending-приглашения для email |
| `SuspendOrganizationCommand` | `SuspendOrganizationHandler` | `org.settings.write` | — |
| `TransferOwnershipCommand` | `TransferOwnershipHandler` | `org.*` | — |
| `UpdateDepartmentCommand` | `UpdateDepartmentHandler` | `departments.write` | — |
| `UpdateMembershipPolicyCommand` | `UpdateMembershipPolicyHandler` | `org.settings.write` | — |
| `UpdateOrgMemberDisplayNameCommand` | `UpdateOrgMemberDisplayNameHandler` | `members.write` | — |
| `UpdateOrgRoleCommand` | `UpdateOrgRoleHandler` | `roles.write` | — |
| `UpdateOrgStorageCommand` | `UpdateOrgStorageHandler` | `org.settings.write` | — |
| `UpdateOrganizationInfoCommand` | `UpdateOrganizationInfoHandler` | `org.settings.write` | — |
| `UpdateSecurityPolicyCommand` | `UpdateSecurityPolicyHandler` | `org.settings.write` | — |
| `UpdateSSOIntegrationCommand` | `UpdateSSOIntegrationHandler` | `org.settings.write` | — |
| `UpdateTeamCommand` | `UpdateTeamHandler` | `teams.write` | — |

---

## Queries

### Запросы без проверки разрешений

| Запрос | Handler | Описание |
|---|---|---|
| `GetInvitationByTokenQuery` | `GetInvitationByTokenHandler` | Получение приглашения по токену ссылки. Доступно без авторизации — необходимо для работы ссылок-приглашений. |

### Запросы с `require_permission`

| Запрос | Handler | REQUIRED_PERMISSION | Дополнительные проверки |
|---|---|---|---|
| `GetDepartmentQuery` | `GetDepartmentHandler` | `departments.read` | — |
| `GetDepartmentsByOrgQuery` | `GetDepartmentsByOrgHandler` | `departments.read` | — |
| `GetInvitationsByOrgQuery` | `GetInvitationsByOrgHandler` | `invitations.read` | — |
| `GetOrgMemberQuery` | `GetOrgMemberHandler` | `members.read` | — |
| `GetOrgMembersQuery` | `GetOrgMembersHandler` | `members.read` | — |
| `GetOrgRoleQuery` | `GetOrgRoleHandler` | `roles.read` | — |
| `GetOrgRolesQuery` | `GetOrgRolesHandler` | `roles.read` | — |
| `GetOrgStorageQuery` | `GetOrgStorageHandler` | `org.settings.read` | — |
| `GetOrganizationQuery` | `GetOrganizationHandler` | `org.read` | — |
| `GetSSOIntegrationsQuery` | `GetSSOIntegrationsHandler` | `org.settings.read` | — |
| `GetTeamQuery` | `GetTeamHandler` | `teams.read` | — |
| `GetTeamsByOrgQuery` | `GetTeamsByOrgHandler` | `teams.read` | — |

### Запросы с `has_permission` (фильтрация)

| Запрос | Handler | Проверяемое разрешение | Описание |
|---|---|---|---|
| `GetOrganizationsByOwnerQuery` | `GetOrganizationsByOwnerHandler` | `org.read` | Возвращает организации владельца, отфильтрованные по наличию `org.read` у `caller_id`. Используется `has_permission` (не `require_permission`). |
| `SearchOrganizationsQuery` | `SearchOrganizationsHandler` | `org.read` | Поиск организаций с фильтрацией по наличию `org.read` у `caller_id`. Используется `has_permission` (не `require_permission`). |

---

## Сводная таблица разрешений

| Разрешение | Commands | Queries |
|---|---|---|
| `org.*` | `AddOrgOwner`, `RemoveOrgOwner`, `TransferOwnership` | — |
| `org.settings.write` | `AddOrgStorage`, `AddSSOIntegration`, `DeactivateSSOIntegration`, `ReactivateOrganization`, `RequestOrganizationDeletion`, `SuspendOrganization`, `UpdateMembershipPolicy`, `UpdateOrgStorage`, `UpdateOrganizationInfo`, `UpdateSecurityPolicy`, `UpdateSSOIntegration` | — |
| `org.settings.read` | — | `GetOrgStorage`, `GetSSOIntegrations` |
| `org.read` | — | `GetOrganization`, `GetOrganizationsByOwner`*, `SearchOrganizations`* |
| `members.write` | `AddOrgMember`, `ChangeOrgMemberRole`, `DeactivateOrgMember`, `ReactivateOrgMember`, `RemoveOrgMember`, `UpdateOrgMemberDisplayName` | — |
| `members.read` | — | `GetOrgMember`, `GetOrgMembers` |
| `members.invite` | `GenerateInvitationLink`, `RevokeInvitation`, `SendBulkInvitations`, `SendInvitation` | — |
| `invitations.read` | — | `GetInvitationsByOrg` |
| `departments.write` | `AddDepartmentMember`, `CreateDepartment`, `DeleteDepartment`, `RemoveDepartmentMember`, `UpdateDepartment` | — |
| `departments.read` | — | `GetDepartment`, `GetDepartmentsByOrg` |
| `teams.write` | `AddTeamMember`, `CreateTeam`, `DeactivateTeam`, `ReactivateTeam`, `RemoveTeamMember`, `UpdateTeam` | — |
| `teams.read` | — | `GetTeam`, `GetTeamsByOrg` |
| `roles.write` | `CreateOrgRole`, `DeleteOrgRole`, `UpdateOrgRole` | — |
| `roles.read` | — | `GetOrgRole`, `GetOrgRoles` |
| Без проверки | `AcceptInvitation`, `DeclineInvitation`, `CreateOrganization` | `GetInvitationByToken` |

\* — используют `has_permission` для фильтрации, а не `require_permission`
