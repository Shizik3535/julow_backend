from __future__ import annotations

from enum import Enum

from app.context.analytics.domain.value_objects.bounded_context_ref import BoundedContextRef


class DataSource(Enum):
    """Источник данных аналитики.

    Каждое значение принадлежит конкретному BC (см. `bounded_context`).
    Расширяется добавлением значения + соответствующего ACL-резолвера
    на infrastructure слое. Domain слой Analytics BC не импортирует другие BC.
    """

    # ---- Task BC ----
    TASKS = "tasks"
    TASK_STATUS_HISTORY = "task_status_history"
    TASK_ASSIGNMENTS = "task_assignments"
    TASK_TAGS = "task_tags"
    SPRINTS = "sprints"
    SPRINT_BURNDOWN = "sprint_burndown"
    SPRINT_VELOCITY = "sprint_velocity"
    EPICS = "epics"

    # ---- Project BC ----
    PROJECTS = "projects"
    PROJECT_MEMBERS = "project_members"
    PROJECT_MILESTONES = "project_milestones"
    PROJECT_PROGRESS = "project_progress"

    # ---- TimeTracking BC ----
    TIME_ENTRIES = "time_entries"
    ACTIVITY_CATEGORIES = "activity_categories"
    TIME_ENTRY_TAGS = "time_entry_tags"
    WORKLOAD = "workload"

    # ---- Communication BC ----
    COMMENTS = "comments"
    MENTIONS = "mentions"
    REACTIONS = "reactions"

    # ---- FileStorage BC ----
    FILES = "files"
    FILE_VERSIONS = "file_versions"
    FILE_STORAGE_USAGE = "file_storage_usage"

    # ---- Notification BC ----
    NOTIFICATIONS = "notifications"
    NOTIFICATION_DELIVERIES = "notification_deliveries"

    # ---- Identity BC ----
    USERS = "users"
    USER_SESSIONS = "user_sessions"
    LOGIN_ATTEMPTS = "login_attempts"

    # ---- Profile BC ----
    PROFILES = "profiles"

    # ---- Organization BC ----
    ORGANIZATIONS = "organizations"
    ORGANIZATION_MEMBERS = "organization_members"

    # ---- Workspace BC ----
    WORKSPACES = "workspaces"
    WORKSPACE_MEMBERS = "workspace_members"
    WORKSPACE_INVITATIONS = "workspace_invitations"

    # ---- Security BC ----
    AUDIT_LOGS = "audit_logs"
    SECURITY_EVENTS = "security_events"

    # ---- Billing BC ----
    SUBSCRIPTIONS = "subscriptions"
    INVOICES = "invoices"
    PAYMENTS = "payments"

    # ---- Произвольный (раскрывается на app-слое) ----
    CUSTOM = "custom"

    @property
    def bounded_context(self) -> BoundedContextRef:
        return _DATA_SOURCE_TO_BC[self]


_DATA_SOURCE_TO_BC: dict[DataSource, BoundedContextRef] = {
    DataSource.TASKS: BoundedContextRef.TASK,
    DataSource.TASK_STATUS_HISTORY: BoundedContextRef.TASK,
    DataSource.TASK_ASSIGNMENTS: BoundedContextRef.TASK,
    DataSource.TASK_TAGS: BoundedContextRef.TASK,
    DataSource.SPRINTS: BoundedContextRef.TASK,
    DataSource.SPRINT_BURNDOWN: BoundedContextRef.TASK,
    DataSource.SPRINT_VELOCITY: BoundedContextRef.TASK,
    DataSource.EPICS: BoundedContextRef.TASK,
    DataSource.PROJECTS: BoundedContextRef.PROJECT,
    DataSource.PROJECT_MEMBERS: BoundedContextRef.PROJECT,
    DataSource.PROJECT_MILESTONES: BoundedContextRef.PROJECT,
    DataSource.PROJECT_PROGRESS: BoundedContextRef.PROJECT,
    DataSource.TIME_ENTRIES: BoundedContextRef.TIMETRACKING,
    DataSource.ACTIVITY_CATEGORIES: BoundedContextRef.TIMETRACKING,
    DataSource.TIME_ENTRY_TAGS: BoundedContextRef.TIMETRACKING,
    DataSource.WORKLOAD: BoundedContextRef.TIMETRACKING,
    DataSource.COMMENTS: BoundedContextRef.COMMUNICATION,
    DataSource.MENTIONS: BoundedContextRef.COMMUNICATION,
    DataSource.REACTIONS: BoundedContextRef.COMMUNICATION,
    DataSource.FILES: BoundedContextRef.FILESTORAGE,
    DataSource.FILE_VERSIONS: BoundedContextRef.FILESTORAGE,
    DataSource.FILE_STORAGE_USAGE: BoundedContextRef.FILESTORAGE,
    DataSource.NOTIFICATIONS: BoundedContextRef.NOTIFICATION,
    DataSource.NOTIFICATION_DELIVERIES: BoundedContextRef.NOTIFICATION,
    DataSource.USERS: BoundedContextRef.IDENTITY,
    DataSource.USER_SESSIONS: BoundedContextRef.IDENTITY,
    DataSource.LOGIN_ATTEMPTS: BoundedContextRef.IDENTITY,
    DataSource.PROFILES: BoundedContextRef.PROFILE,
    DataSource.ORGANIZATIONS: BoundedContextRef.ORGANIZATION,
    DataSource.ORGANIZATION_MEMBERS: BoundedContextRef.ORGANIZATION,
    DataSource.WORKSPACES: BoundedContextRef.WORKSPACE,
    DataSource.WORKSPACE_MEMBERS: BoundedContextRef.WORKSPACE,
    DataSource.WORKSPACE_INVITATIONS: BoundedContextRef.WORKSPACE,
    DataSource.AUDIT_LOGS: BoundedContextRef.SECURITY,
    DataSource.SECURITY_EVENTS: BoundedContextRef.SECURITY,
    DataSource.SUBSCRIPTIONS: BoundedContextRef.BILLING,
    DataSource.INVOICES: BoundedContextRef.BILLING,
    DataSource.PAYMENTS: BoundedContextRef.BILLING,
    DataSource.CUSTOM: BoundedContextRef.ANALYTICS,
}
