# События Workspace BC

## События, которые отдаёт Workspace BC

### Workspace Events

| Событие | Описание | Поля |
|---|---|---|
| `WorkspaceCreated` | Workspace создан | `workspace_id`, `owner_id`, `name`, `organization_id`, `parent_workspace_id`, `workspace_type` |
| `WorkspaceInfoChanged` | Информация workspace обновлена | `workspace_id`, `changed_fields` |
| `WorkspaceArchived` | Workspace архивирован | `workspace_id` |
| `WorkspaceRestored` | Workspace восстановлен из архива | `workspace_id` |
| `WorkspaceSuspended` | Workspace приостановлен | `workspace_id`, `reason` |
| `WorkspaceReactivated` | Workspace реактивирован | `workspace_id` |
| `WorkspaceDeletionRequested` | Запрос удаления workspace | `workspace_id` |
| `OwnershipTransferred` | Владение передано | `workspace_id`, `old_owner_id`, `new_owner_id` |
| `WorkspacePersonalizationChanged` | Персонализация workspace изменена | `workspace_id`, `changed_fields` |
| `SecurityPolicyChanged` | Политика безопасности изменена | `workspace_id`, `changed_fields` |
| `MembershipPolicyChanged` | Политика членства изменена | `workspace_id`, `changed_fields` |
| `WorkspaceLimitsChanged` | Лимиты workspace изменены | `workspace_id`, `changed_fields` |
| `ChildWorkspaceCreated` | Дочерний workspace создан | `parent_workspace_id`, `child_workspace_id` |

### Workspace Membership Events

| Событие | Описание | Поля |
|---|---|---|
| `WorkspaceMemberJoined` | Участник присоединился к workspace | `workspace_id`, `user_id`, `role_id`, `source` |
| `WorkspaceMemberDisplayNameChanged` | Отображаемое имя участника изменено | `workspace_id`, `user_id`, `display_name` |
| `WorkspaceMemberRoleChanged` | Роль участника изменена | `workspace_id`, `user_id`, `new_role_id` |
| `WorkspaceMemberRemoved` | Участник удалён из workspace | `workspace_id`, `user_id` |
| `WorkspaceMemberDeactivated` | Участник деактивирован | `workspace_id`, `user_id` |
| `WorkspaceMemberReactivated` | Участник реактивирован | `workspace_id`, `user_id` |
| `MemberAddedFromOrganization` | Участник добавлен из организации (ACL) | `workspace_id`, `user_id` |
| `MemberInheritedFromParent` | Участник унаследован из родительского workspace | `workspace_id`, `user_id`, `parent_workspace_id` |

### Workspace Role Events

| Событие | Описание | Поля |
|---|---|---|
| `WorkspaceRoleCreated` | Кастомная роль workspace создана | `workspace_id`, `role_name` |
| `WorkspaceRoleUpdated` | Роль workspace обновлена | `workspace_id`, `role_name` |
| `WorkspaceRoleDeleted` | Кастомная роль workspace удалена | `workspace_id`, `role_name` |

### Workspace Invitation Events

| Событие | Описание | Поля |
|---|---|---|
| `InvitationSent` | Приглашение отправлено | `workspace_id`, `email`, `role_id` |
| `InvitationAccepted` | Приглашение принято | `workspace_id`, `user_id` |
| `InvitationDeclined` | Приглашение отклонено | `workspace_id`, `email` |
| `InvitationRevoked` | Приглашение отозвано | `workspace_id`, `invitation_id` |
| `InvitationLinkGenerated` | Ссылка-приглашение сгенерирована | `workspace_id`, `token` |

### Workspace Team Events

| Событие | Описание | Поля |
|---|---|---|
| `WorkspaceTeamCreated` | Команда workspace создана | `workspace_id`, `team_id` |
| `WorkspaceTeamUpdated` | Команда workspace обновлена | `workspace_id`, `team_id`, `changed_fields` |
| `WorkspaceTeamDeleted` | Команда workspace удалена | `workspace_id`, `team_id` |
| `WorkspaceTeamMemberAdded` | Участник добавлен в команду workspace | `workspace_id`, `team_id`, `user_id` |
| `WorkspaceTeamMemberRemoved` | Участник удалён из команды workspace | `workspace_id`, `team_id`, `user_id` |

**Итого: 34 события**

---

## События, на которые подписывается Workspace BC

### Внутренние подписки (внутри Workspace BC)

| Обработчик | Событие | Топик | Описание |
|---|---|---|---|
| `OnMembershipPolicyCascade` | `MembershipPolicyChanged` | `workspace.events` | При изменении MembershipPolicy родительского workspace каскадно обновляет дочерние workspace с `inherit_from_parent=True`. |
| `OnSecurityPolicyCascade` | `SecurityPolicyChanged` | `workspace.events` | При изменении SecurityPolicy родительского workspace каскадно обновляет дочерние workspace с `inherit_from_parent=True`. |

### Кросс-BC подписки

| Обработчик | Источник (BC) | Событие | Топик | Описание |
|---|---|---|---|---|
| `OnOrgMemberJoinedAutoAdd` | Organization BC | `OrgMemberJoined` | `organization.events` | Если workspace привязан к организации и `auto_add_from_org=True`, автоматически добавляет нового участника организации в workspace. Идемпотентно — пропускает, если участник уже в workspace. |
| `OnOrgMemberDeactivatedCascade` | Organization BC | `OrgMemberDeactivated` | `organization.events` | Деактивирует пользователя во всех workspace организации при деактивации участника организации. Уже деактивированные пропускаются. |
| `OnOrgMemberRemovedCascade` | Organization BC | `OrgMemberRemoved` | `organization.events` | Удаляет пользователя из всех workspace организации при удалении участника из организации. Владельцы workspace пропускаются. |
| `OnUserDeletedCleanupMemberships` | Identity BC | `UserDeleted` | `identity.events` | Окончательно удаляет пользователя из всех workspace при удалении аккаунта. Идемпотентно. |

**Итого: 6 подписок** (2 внутренние + 4 кросс-BC: 3 из Organization BC + 1 из Identity BC)
