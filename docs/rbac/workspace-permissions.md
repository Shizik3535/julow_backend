# Проверки разрешений в Workspace Context

## Обзор механизма авторизации

Авторизация в Workspace Context реализована через порт `WorkspacePermissionCheckerPort` с двумя методами:

- **`require_permission(user_id, workspace_id, permission)`** — проверяет разрешение и выбрасывает `InsufficientWorkspacePermissionsException` при отсутствии. Используется в большинстве commands и queries.
- **`has_permission(user_id, workspace_id, permission)`** — возвращает `bool`, используется для фильтрации результатов (когда отсутствие разрешения не является ошибкой).

Поддерживаются wildcard-разрешения:
- `ws.*` — полный доступ в workspace (владелец)
- `members.*` / `roles.*` / `teams.*` / `ws.settings.*` — групповые разрешения
- `members.write` — конкретное разрешение

### Каскад OrgRole → Workspace

Если workspace принадлежит организации, орг-разрешения вида `workspaces.<group>.<action>` дают те же права, что и соответствующие workspace-разрешения. Например, орг-роль с `workspaces.members.read` покрывает `members.read` в workspace.

### Кросс-BC авторизация

Некоторые операции в Workspace BC требуют проверки разрешений в Organization BC через порт `OrganizationPermissionCheckerPort`. Такие случаи отмечены отдельно.

Каждый handler определяет константу `REQUIRED_PERMISSION` (или `REQUIRED_ORG_PERMISSION` для кросс-BC проверок) — требуемое разрешение для выполнения операции.

---

## Commands

### Команды без проверки разрешений

| Команда | Handler | Описание |
|---|---|---|
| `AcceptWorkspaceInvitationCommand` | `AcceptWorkspaceInvitationHandler` | Принятие приглашения. Доступно любому аутентифицированному пользователю по `invitation_id`. Проверяется существование пользователя через `IdentityUserPort`. |

### Команды с кросс-BC проверкой (Organization Permission)

| Команда | Handler | REQUIRED_ORG_PERMISSION | Способ проверки | Дополнительные проверки |
|---|---|---|---|---|
| `CreateWorkspaceCommand` | `CreateWorkspaceHandler` | `workspaces.create` | `has_permission` (мягкая проверка, выбрасывает `InsufficientWorkspacePermissionsException` вручную) | Проверяется только если указан `organization_id`; для независимого workspace проверка не требуется. Проверка существования пользователя через `IdentityUserPort`. |

### Команды с проверкой разрешений (Workspace Permission)

| Команда | Handler | REQUIRED_PERMISSION | Дополнительные проверки |
|---|---|---|---|
| `AddWorkspaceMemberCommand` | `AddWorkspaceMemberHandler` | `members.write` | Проверка существования пользователя через `IdentityUserPort`; проверка на дубликат членства |
| `AddWorkspaceOwnerCommand` | `AddWorkspaceOwnerHandler` | `ws.*` | — |
| `AddWorkspaceTeamMemberCommand` | `AddWorkspaceTeamMemberHandler` | `teams.write` | Проверяется, что добавляемый пользователь является участником workspace |
| `ArchiveWorkspaceCommand` | `ArchiveWorkspaceHandler` | `ws.settings.write` | Проверяется отсутствие активных дочерних workspace |
| `ChangeWorkspaceMemberRoleCommand` | `ChangeWorkspaceMemberRoleHandler` | `members.write` | — |
| `CreateWorkspaceRoleCommand` | `CreateWorkspaceRoleHandler` | `roles.write` | — |
| `CreateWorkspaceTeamCommand` | `CreateWorkspaceTeamHandler` | `teams.write` | — |
| `DeactivateWorkspaceMemberCommand` | `DeactivateWorkspaceMemberHandler` | `members.write` | Проверяется, является ли деактивируемый пользователь владельцем (`is_owner`) — влияет на логику деактивации |
| `DeclineWorkspaceInvitationCommand` | `DeclineWorkspaceInvitationHandler` | `members.invite`¶ | Адресат приглашения (email совпадает) может отклонить без разрешения; иначе требуется `members.invite` |
| `DeactivateWorkspaceTeamCommand` | `DeactivateWorkspaceTeamHandler` | `teams.write` | — |
| `DeleteWorkspaceRoleCommand` | `DeleteWorkspaceRoleHandler` | `roles.write` | Системные роли (`workspace_id=None`) недоступны для удаления — выбрасывается `InsufficientWorkspacePermissionsException` |
| `GenerateWorkspaceInvitationLinkCommand` | `GenerateWorkspaceInvitationLinkHandler` | `members.invite` | — |
| `MoveWorkspaceUnderParentCommand` | `MoveWorkspaceUnderParentHandler` | `ws.settings.write` | Проверка циклических ссылок в иерархии; максимальная глубина иерархии (`MAX_HIERARCHY_DEPTH=3`) |
| `ReactivateWorkspaceCommand` | `ReactivateWorkspaceHandler` | `ws.settings.write` | — |
| `ReactivateWorkspaceMemberCommand` | `ReactivateWorkspaceMemberHandler` | `members.write` | — |
| `ReactivateWorkspaceTeamCommand` | `ReactivateWorkspaceTeamHandler` | `teams.write` | — |
| `RemoveWorkspaceMemberCommand` | `RemoveWorkspaceMemberHandler` | `members.write` | Проверяется, является ли удаляемый пользователь владельцем (`is_owner`) — влияет на логику удаления |
| `RemoveWorkspaceOwnerCommand` | `RemoveWorkspaceOwnerHandler` | `ws.*` | Домен гарантирует, что минимум один владелец останется |
| `RemoveWorkspaceTeamMemberCommand` | `RemoveWorkspaceTeamMemberHandler` | `teams.write` | — |
| `RequestWorkspaceDeletionCommand` | `RequestWorkspaceDeletionHandler` | `ws.*` | — |
| `RestoreWorkspaceCommand` | `RestoreWorkspaceHandler` | `ws.settings.write` | — |
| `RevokeWorkspaceInvitationCommand` | `RevokeWorkspaceInvitationHandler` | `members.invite` | — |
| `SendBulkWorkspaceInvitationsCommand` | `SendBulkWorkspaceInvitationsHandler` | `members.invite` | Пропускаются дубликаты email среди pending-приглашений |
| `SendWorkspaceInvitationCommand` | `SendWorkspaceInvitationHandler` | `members.invite` | Проверка на дубликат pending-приглашения для email |
| `SuspendWorkspaceCommand` | `SuspendWorkspaceHandler` | `ws.settings.write` | — |
| `TransferWorkspaceOwnershipCommand` | `TransferWorkspaceOwnershipHandler` | `ws.*` | — |
| `UpdateWorkspaceInfoCommand` | `UpdateWorkspaceInfoHandler` | `ws.settings.write` | — |
| `UpdateWorkspaceLimitsCommand` | `UpdateWorkspaceLimitsHandler` | `ws.settings.write` | — |
| `UpdateWorkspaceMemberDisplayNameCommand` | `UpdateWorkspaceMemberDisplayNameHandler` | `members.write` | — |
| `UpdateWorkspaceMembershipPolicyCommand` | `UpdateWorkspaceMembershipPolicyHandler` | `ws.settings.write` | — |
| `UpdateWorkspaceRoleCommand` | `UpdateWorkspaceRoleHandler` | `roles.write` | Системные роли (`workspace_id=None`) недоступны для изменения — выбрасывается `InsufficientWorkspacePermissionsException` |
| `UpdateWorkspaceSecurityPolicyCommand` | `UpdateWorkspaceSecurityPolicyHandler` | `ws.settings.write` | — |
| `UpdateWorkspaceTeamCommand` | `UpdateWorkspaceTeamHandler` | `teams.write` | — |

---

## Queries

### Запросы без проверки разрешений

| Запрос | Handler | Описание |
|---|---|---|
| `GetWorkspaceInvitationByTokenQuery` | `GetWorkspaceInvitationByTokenHandler` | Получение приглашения по токену ссылки. Доступно без авторизации — необходимо для работы ссылок-приглашений. |

### Запросы с `require_permission`

| Запрос | Handler | REQUIRED_PERMISSION | Дополнительные проверки |
|---|---|---|---|
| `GetChildWorkspacesQuery` | `GetChildWorkspacesHandler` | `ws.read` | — |
| `GetWorkspaceQuery` | `GetWorkspaceQuery` | `ws.read` | — |
| `GetWorkspaceInvitationsQuery` | `GetWorkspaceInvitationsHandler` | `members.invite` | — |
| `GetWorkspaceMemberQuery` | `GetWorkspaceMemberHandler` | `members.read` | — |
| `GetWorkspaceMembersQuery` | `GetWorkspaceMembersHandler` | `members.read` | — |
| `GetWorkspaceRolesQuery` | `GetWorkspaceRolesHandler` | `roles.read` | — |
| `GetWorkspaceSettingsQuery` | `GetWorkspaceSettingsHandler` | `ws.settings.read` | — |
| `GetWorkspaceTeamQuery` | `GetWorkspaceTeamHandler` | `teams.read` | — |
| `GetWorkspaceTeamsQuery` | `GetWorkspaceTeamsHandler` | `teams.read` | — |

### Запросы с условной проверкой `require_permission`

| Запрос | Handler | REQUIRED_PERMISSION | Условие | Дополнительные проверки |
|---|---|---|---|---|
| `GetWorkspaceRoleQuery` | `GetWorkspaceRoleHandler` | `roles.read` | Только для кастомных ролей (`workspace_id is not None`). Системные роли читаемы без проверки. | — |

### Запросы с `has_permission` (фильтрация)

| Запрос | Handler | Проверяемое разрешение | Описание |
|---|---|---|---|
| `GetRootWorkspacesQuery` | `GetRootWorkspacesHandler` | `ws.read` | Возвращает корневые workspace, отфильтрованные по наличию `ws.read` у `caller_id`. Используется `has_permission`. |
| `GetWorkspacesByOwnerQuery` | `GetWorkspacesByOwnerHandler` | `ws.read` | Возвращает workspace владельца, отфильтрованные по наличию `ws.read` у `caller_id`. Используется `has_permission`. |
| `SearchWorkspacesQuery` | `SearchWorkspacesHandler` | `ws.read` | Поиск workspace с двойной фильтрацией: 1) пользователь должен быть участником workspace; 2) наличие `ws.read`. Используется `has_permission`. |

### Запросы с кросс-BC проверкой (Organization Permission)

| Запрос | Handler | REQUIRED_ORG_PERMISSION | Способ проверки | Дополнительные проверки |
|---|---|---|---|---|
| `GetWorkspacesByOrganizationQuery` | `GetWorkspacesByOrganizationHandler` | `workspaces.read` | `has_permission` (мягкая проверка) | 1. Caller должен быть членом организации (`OrganizationMembershipPort.is_org_member`), иначе 403. 2. Если есть `workspaces.read` — возвращаются все workspace организации. 3. Иначе — только те, где caller является участником. |

---

## Сводная таблица разрешений

### Workspace-разрешения

| Разрешение | Commands | Queries |
|---|---|---|
| `ws.*` | `AddWorkspaceOwner`, `RemoveWorkspaceOwner`, `RequestWorkspaceDeletion`, `TransferWorkspaceOwnership` | — |
| `ws.settings.write` | `ArchiveWorkspace`, `MoveWorkspaceUnderParent`, `ReactivateWorkspace`, `RestoreWorkspace`, `SuspendWorkspace`, `UpdateWorkspaceInfo`, `UpdateWorkspaceLimits`, `UpdateWorkspaceMembershipPolicy`, `UpdateWorkspaceSecurityPolicy` | — |
| `ws.settings.read` | — | `GetWorkspaceSettings` |
| `ws.read` | — | `GetWorkspace`, `GetChildWorkspaces`, `GetRootWorkspaces`*, `GetWorkspacesByOwner`*, `SearchWorkspaces`* |
| `members.write` | `AddWorkspaceMember`, `ChangeWorkspaceMemberRole`, `DeactivateWorkspaceMember`, `ReactivateWorkspaceMember`, `RemoveWorkspaceMember`, `UpdateWorkspaceMemberDisplayName` | — |
| `members.read` | — | `GetWorkspaceMember`, `GetWorkspaceMembers` |
| `members.invite` | `DeclineWorkspaceInvitation`¶, `GenerateWorkspaceInvitationLink`, `RevokeWorkspaceInvitation`, `SendBulkWorkspaceInvitations`, `SendWorkspaceInvitation` | `GetWorkspaceInvitations` |
| `teams.write` | `AddWorkspaceTeamMember`, `CreateWorkspaceTeam`, `DeactivateWorkspaceTeam`, `ReactivateWorkspaceTeam`, `RemoveWorkspaceTeamMember`, `UpdateWorkspaceTeam` | — |
| `teams.read` | — | `GetWorkspaceTeam`, `GetWorkspaceTeams` |
| `roles.write` | `CreateWorkspaceRole`, `DeleteWorkspaceRole`, `UpdateWorkspaceRole` | — |
| `roles.read` | — | `GetWorkspaceRole`†, `GetWorkspaceRoles` |
| Без проверки | `AcceptWorkspaceInvitation` | `GetWorkspaceInvitationByToken` |

### Кросс-BC (Organization) разрешения

| Разрешение | Commands | Queries |
|---|---|---|
| `workspaces.create` | `CreateWorkspace`‡ | — |
| `workspaces.read` | — | `GetWorkspacesByOrganization`§ |

\* — используют `has_permission` для фильтрации, а не `require_permission`
† — `require_permission` применяется только для кастомных ролей; системные роли доступны без проверки
‡ — проверяется через `OrganizationPermissionCheckerPort.has_permission` только при наличии `organization_id`
§ — проверяется через `OrganizationPermissionCheckerPort.has_permission` + `OrganizationMembershipPort.is_org_member`
¶ — `members.invite` требуется только если отклоняющий не является адресатом приглашения (email совпадает)
