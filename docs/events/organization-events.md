# События Organization BC

## События, которые отдаёт Organization BC

### Organization Events

| Событие | Описание | Поля |
|---|---|---|
| `OrganizationCreated` | Организация создана | `org_id`, `owner_id`, `name` |
| `OrganizationInfoChanged` | Информация обновлена | `org_id`, `changed_fields` |
| `OrganizationSuspended` | Организация приостановлена | `org_id`, `reason` |
| `OrganizationReactivated` | Организация реактивирована | `org_id` |
| `OrganizationDeletionRequested` | Запрос удаления организации | `org_id` |
| `OwnershipTransferred` | Владение передано | `org_id`, `old_owner_id`, `new_owner_id` |
| `OrgPersonalizationChanged` | Персонализация изменена | `org_id`, `changed_fields` |
| `SecurityPolicyChanged` | Политика безопасности изменена | `org_id`, `changed_fields` |
| `MembershipPolicyChanged` | Политика членства изменена | `org_id`, `changed_fields` |

### Org Membership Events

| Событие | Описание | Поля |
|---|---|---|
| `OrgMemberJoined` | Участник присоединился | `org_id`, `user_id`, `role_id` |
| `OrgMemberDisplayNameChanged` | Отображаемое имя изменено | `org_id`, `user_id`, `display_name` |
| `OrgMemberRoleChanged` | Роль участника изменена | `org_id`, `user_id`, `new_role_id` |
| `OrgMemberRemoved` | Участник удалён | `org_id`, `user_id` |
| `OrgMemberDeactivated` | Участник деактивирован | `org_id`, `user_id` |
| `OrgMemberReactivated` | Участник реактивирован | `org_id`, `user_id` |

### Org Role Events

| Событие | Описание | Поля |
|---|---|---|
| `OrgRoleCreated` | Кастомная роль создана | `org_id`, `role_name` |
| `OrgRoleUpdated` | Роль обновлена | `org_id`, `role_name` |
| `OrgRoleDeleted` | Кастомная роль удалена | `org_id`, `role_name` |

### Invitation Events

| Событие | Описание | Поля |
|---|---|---|
| `InvitationSent` | Приглашение отправлено | `org_id`, `email`, `role_id` |
| `InvitationAccepted` | Приглашение принято | `org_id`, `user_id` |
| `InvitationDeclined` | Приглашение отклонено | `org_id`, `email` |
| `InvitationRevoked` | Приглашение отозвано | `org_id`, `invitation_id` |
| `InvitationLinkGenerated` | Ссылка-приглашение сгенерирована | `org_id`, `token` |

### Department Events

| Событие | Описание | Поля |
|---|---|---|
| `DepartmentCreated` | Подразделение создано | `org_id`, `department_id` |
| `DepartmentUpdated` | Подразделение обновлено | `org_id`, `department_id`, `changed_fields` |
| `DepartmentDeleted` | Подразделение удалено | `org_id`, `department_id` |
| `DepartmentMemberAdded` | Участник добавлен в подразделение | `org_id`, `department_id`, `user_id` |
| `DepartmentMemberRemoved` | Участник удалён из подразделения | `org_id`, `department_id`, `user_id` |

### Team Events

| Событие | Описание | Поля |
|---|---|---|
| `TeamCreated` | Команда создана | `org_id`, `team_id` |
| `TeamUpdated` | Команда обновлена | `org_id`, `team_id`, `changed_fields` |
| `TeamDeleted` | Команда удалена | `org_id`, `team_id` |
| `TeamMemberAdded` | Участник добавлен в команду | `org_id`, `team_id`, `user_id` |
| `TeamMemberRemoved` | Участник удалён из команды | `org_id`, `team_id`, `user_id` |

### SSO Integration Events

| Событие | Описание | Поля |
|---|---|---|
| `SSOIntegrationAdded` | SSO-интеграция добавлена | `org_id`, `provider` |
| `SSOIntegrationUpdated` | SSO-интеграция обновлена | `org_id`, `provider` |
| `SSOIntegrationDeactivated` | SSO-интеграция деактивирована | `org_id`, `provider` |

### Storage Integration Events

| Событие | Описание | Поля |
|---|---|---|
| `OrgStorageAdded` | Хранилище добавлено | `org_id`, `storage_id` |
| `OrgStorageUpdated` | Хранилище обновлено | `org_id`, `changed_fields` |
| `OrgStorageQuotaExceeded` | Квота хранилища превышена | `org_id` |

**Итого: 30 событий**

---

## События, на которые подписывается Organization BC

| Обработчик | Источник (BC) | Событие | Топик | Описание |
|---|---|---|---|---|
| `OnAccountDeletionRequestedCleanupMemberships` | Identity BC | `AccountDeletionRequested` | `identity.events` | Удаляет пользователя из всех организаций при удалении аккаунта. Идемпотентно. |

**Итого: 1 подписка**
