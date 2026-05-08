# События Notification BC

## События, которые отдаёт Notification BC

### Notification Events

| Событие | Описание | Поля |
|---|---|---|
| `NotificationCreated` | Уведомление создано | `notification_id`, `recipient_id`, `notification_type`, `title`, `body`, `priority`, `channels` |
| `NotificationRead` | Уведомление прочитано | `notification_id` |
| `AllNotificationsRead` | Все уведомления прочитаны | `user_id`, `workspace_id`, `count` |
| `NotificationArchived` | Уведомление архивировано | `notification_id` |
| `NotificationPreferenceUpdated` | Настройка уведомлений обновлена | `user_id`, `notification_type`, `channel`, `enabled`, `scope` |
| `DndSettingsUpdated` | DND обновлён | `user_id`, `enabled` |
| `DigestSettingsUpdated` | Дайджест обновлён | `user_id`, `enabled`, `frequency` |
| `DigestSent` | Дайджест отправлен | `user_id`, `notification_count` |
| `DeviceTokenRegistered` | Токен устройства зарегистрирован | `user_id`, `platform` |
| `DeviceTokenRemoved` | Токен устройства удалён/деактивирован | `user_id`, `platform` |
| `ReminderWindowUpdated` | Окно напоминания обновлено | `user_id`, `hours` |

**Итого: 11 событий**

---

## События, на которые подписывается Notification BC

### Внутренние подписки (внутри Notification BC)

| Обработчик | Событие | Описание |
|---|---|---|
| `OnNotificationCreatedSend` | `NotificationCreated` | Отправляет уведомление по каналам через NotificationSenderPort. SenderPort сам проверяет preferences и DND. |

### Кросс-BC подписки

| Обработчик | Источник (BC) | Событие | Топик | Описание |
|---|---|---|---|---|
| `OnUserRegisteredCreatePreferences` | Identity BC | `UserRegistered` | `identity.events` | Создаёт NotificationPreferences для нового пользователя. Идемпотентно — пропускает, если настройки уже существуют. |
| `OnEmailConfirmedSendWelcome` | Identity BC | `EmailConfirmed` | `identity.events` | Создаёт welcome-уведомление после подтверждения email. |
| `OnPasswordChangedNotify` | Identity BC | `PasswordChanged` | `identity.events` | Создаёт security_password_changed уведомление. |
| `OnAuthFactorChangedNotify` | Identity BC | `AuthFactorEnabled` / `AuthFactorDisabled` | `identity.events` | Создаёт security_2fa_changed уведомление при изменении 2FA. |
| `OnNewDeviceLoginNotify` | Identity BC | `NewDeviceLogin` | `identity.events` | Создаёт security_new_device уведомление при входе с нового устройства. |
| `OnUserDeletedCleanup` | Identity BC | `UserDeleted` | `identity.events` | Деактивирует настройки уведомлений и токены устройств пользователя. Идемпотентно. |
| `OnOrgInvitationSentNotify` | Organization BC | `InvitationSent` | `organization.events` | Создаёт organization_invitation уведомление при приглашении в организацию. |
| `OnWorkspaceInvitationSentNotify` | Workspace BC | `InvitationSent` | `workspace.events` | Создаёт workspace_invitation уведомление при приглашении в workspace. |
| `OnProjectMemberJoinedNotify` | Project BC | `ProjectMemberJoined` | `project.events` | Создаёт project_invitation уведомление при добавлении в проект. |
| `OnProjectDeadlineApproachingNotify` | Project BC | `ProjectDeadlineApproaching` | `project.events` | Создаёт project_deadline_approaching уведомление для каждого участника проекта. Дедупликация по типу и target. |
| `OnSprintStartedNotify` | Project BC | `SprintStarted` | `project.events` | Создаёт sprint_started уведомление. |
| `OnSprintCompletedNotify` | Project BC | `SprintCompleted` | `project.events` | Создаёт sprint_completed уведомление. |
| `OnTaskAssignedNotify` | Task BC | `TaskAssigned` | `task.events` | Создаёт task_assigned уведомление для назначенного исполнителя. |
| `OnTaskUnassignedNotify` | Task BC | `TaskUnassigned` | `task.events` | Создаёт task_unassigned уведомление для снятого исполнителя. |
| `OnTaskStatusChangedNotify` | Task BC | `TaskStatusChanged` | `task.events` | Создаёт task_status_changed уведомление для каждого участника задачи (кроме инициатора изменения). |
| `OnTaskInfoChangedNotify` | Task BC | `TaskInfoChanged` | `task.events` | Если changed_fields содержит «due_date», создаёт task_deadline_changed уведомление для каждого участника задачи. |
| `OnCommentAddedNotify` | Communication BC | `CommentAdded` | `communication.events` | Маршрутизация по `target_type`: `task` → task_comment всем участникам задачи (`TaskParticipantPort`), `project` → project_comment всем участникам проекта (`ProjectMemberPort`). Автор исключается. `epic`/`sprint`/`milestone` логируются как warning и пропускаются. |
| `OnMeetingParticipantAddedNotify` | Communication BC | `MeetingParticipantAdded` | `communication.events` | Создаёт meeting_scheduled уведомление добавленному участнику совещания. |
| `OnChatMemberAddedNotify` | Communication BC | `ChatMemberAdded` | `communication.events` | Создаёт chat_member_added уведомление пользователю, которого добавили в чат. |
| `OnMessageSentNotify` | Communication BC | `MessageSent` | `communication.events` | Создаёт chat_message уведомление всем участникам чата (кроме отправителя). Использует `ChatMembersPort`. Системные (`message_type=system`) не нотифицируются. |
| `OnTaskDeadlineApproachingNotify` | Task BC | `TaskDeadlineApproaching` | `task.events` | Создаёт task_due_approaching уведомление для каждого исполнителя задачи. Дедупликация по типу и target. |
| `OnTaskOverdueNotify` | Task BC | `TaskOverdue` | `task.events` | Создаёт task_overdue уведомление для каждого исполнителя задачи. |

**Итого: 24 подписки** (1 внутренняя + 23 кросс-BC: 6 из Identity BC + 1 из Organization BC + 1 из Workspace BC + 5 из Project BC + 6 из Task BC + 4 из Communication BC)
