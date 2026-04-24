# Event Flows — Потоки событий между BC

События пересекают границы BC только на **application/infrastructure** слоях.
На доменном слое BC не знают друг о друге.

---

## Регистрация и профиль

```
Identity: UserRegistered ──→ Profile: создаёт UserProfile (via ACL)
Identity: UserLoggedIn   ──→ Security: AuditEntryCreated (LOGIN, USER)
Identity: LoginFailed    ──→ Security: AuditEntryCreated (LOGIN, USER)
```

## Организация → Workspace

```
Organization: OrgMemberJoined    ──→ Workspace: MemberAddedFromOrganization (via ACL)
Organization: OrgMemberRemoved   ──→ Workspace: WorkspaceMemberRemoved (via ACL)
Organization: OrganizationCreated ──→ Billing: SubscriptionCreated (FREE) (via ACL)
Organization: OrgStorageAdded    ──→ FileStorage: Storage создано (via ACL)
```

## Workspace → Project → Task

```
Workspace: WorkspaceCreated ──→ FileStorage: Storage создано (via ACL)
Project: ProjectCreated     ──→ Task: создаёт задачи по шаблону (via ACL)
Project: SprintStarted      ──→ Task: назначает задачи на спринт (via ACL)
Project: SprintCompleted    ──→ Task: TasksMovedToBacklog / TasksMovedToNextSprint
```

## Task → Notification

```
Task: TaskAssigned           ──→ Notification: TASK_ASSIGNED
Task: TaskStatusChanged      ──→ Notification: STATUS_CHANGED
Task: TaskDeadlineApproaching ──→ Notification: DEADLINE_APPROACHING
Task: TaskOverdue            ──→ Notification: OVERDUE_TASK
```

## Communication → Notification

```
Communication: CommentAdded   ──→ Notification: NEW_COMMENT
Communication: UserMentioned  ──→ Notification: MENTIONED
Communication: MeetingScheduled ──→ Notification: INVITED
```

## FileStorage → Notification

```
FileStorage: StorageQuotaApproaching ──→ Notification: SYSTEM
FileStorage: VirusDetected          ──→ Notification: SECURITY
```

## Billing → Notification

```
Billing: PaymentSucceeded      ──→ Notification: BILLING
Billing: PaymentFailed         ──→ Notification: BILLING
Billing: CardExpiringWarning   ──→ Notification: BILLING
Billing: TrialExpired          ──→ Notification: BILLING
Billing: PlanLimitApproaching  ──→ Notification: SYSTEM
Billing: PlanLimitExceeded     ──→ Notification: SYSTEM
```

## Security → Notification

```
Security: SuspiciousActivityDetected ──→ Notification: SECURITY
Security: ComplianceViolationDetected ──→ Notification: SECURITY
```

## TimeTracking → Notification

```
TimeTracking: UnfilledTimeReminderTriggered ──→ Notification: SYSTEM
```

## Любой BC → Security (Audit)

```
Communication: CommentAdded  ──→ Security: AuditEntryCreated (CREATE, TASK)
Communication: MessageSent    ──→ Security: AuditEntryCreated (CREATE, SYSTEM)
Task: TaskCreated             ──→ Security: AuditEntryCreated (CREATE, TASK)
Task: TaskDeleted             ──→ Security: AuditEntryCreated (DELETE, TASK)
ImportExport: ExportStarted   ──→ Security: AuditEntryCreated (EXPORT, TASK)
ImportExport: ImportStarted   ──→ Security: AuditEntryCreated (CREATE, TASK)
Identity: UserLoggedIn        ──→ Security: AuditEntryCreated (LOGIN, USER)
Billing: SubscriptionUpgraded ──→ Security: AuditEntryCreated (CONFIG_CHANGE, SYSTEM)
Administration: SystemSettingsUpdated ──→ Security: AuditEntryCreated (CONFIG_CHANGE, SYSTEM)
```

## Administration → Notification

```
Administration: MaintenanceModeEnabled ──→ Notification: SYSTEM (всем пользователям)
Administration: FeatureFlagToggled     ──→ влияет на доступность фич (infrastructure)
```

## Support

```
Support: TicketCreated ──→ Notification: SYSTEM (support agents)
```
