from fastapi import APIRouter

from app.api.v1.ws import ws_router

# Единое место для сборки всех endpoint'ов API v1.
#
# Каждый Bounded Context регистрирует свои роуты через
# включение своего APIRouter в этот корневой роутер.
#
# Порядок включения определяет порядок в OpenAPI документации.
#
# При переходе на микросервисы — каждый BC получает свой
# собственный router.py, а этот файл удаляется.


api_v1_router = APIRouter()

# --- Регистрация роутов Bounded Context'ов ---

# Identity BC
from app.context.identity.presentation.controllers import (
    AccountController,
    AdminController,
    AuthController,
    SecurityController,
)

_auth_controller = AuthController()
_account_controller = AccountController()
_security_controller = SecurityController()
_admin_controller = AdminController()

api_v1_router.include_router(_auth_controller.router)
api_v1_router.include_router(_account_controller.router)
api_v1_router.include_router(_security_controller.router)
api_v1_router.include_router(_admin_controller.router)

# Profile BC
from app.context.profile.presentation.controllers import ProfileController

_profile_controller = ProfileController()

api_v1_router.include_router(_profile_controller.router)

# Organization BC
from app.context.organization.presentation.controllers import (
    DepartmentController,
    IntegrationController,
    InvitationController,
    MemberController,
    OrganizationController,
    RoleController,
    TeamController,
)

_organization_controller = OrganizationController()
_member_controller = MemberController()
_invitation_controller = InvitationController()
_department_controller = DepartmentController()
_team_controller = TeamController()
_role_controller = RoleController()
_integration_controller = IntegrationController()

api_v1_router.include_router(_organization_controller.router)
api_v1_router.include_router(_member_controller.router)
api_v1_router.include_router(_invitation_controller.router)
api_v1_router.include_router(_department_controller.router)
api_v1_router.include_router(_team_controller.router)
api_v1_router.include_router(_role_controller.router)
api_v1_router.include_router(_integration_controller.router)

# Workspace BC
from app.context.workspace.presentation.controllers import (
    OrgWorkspaceController,
    WorkspaceController,
    WorkspaceInvitationController,
    WorkspaceMemberController,
    WorkspaceRoleController,
    WorkspaceTeamController,
)

_org_workspace_controller = OrgWorkspaceController()
_workspace_controller = WorkspaceController()
_workspace_member_controller = WorkspaceMemberController()
_workspace_invitation_controller = WorkspaceInvitationController()
_workspace_team_controller = WorkspaceTeamController()
_workspace_role_controller = WorkspaceRoleController()

api_v1_router.include_router(_org_workspace_controller.router)
api_v1_router.include_router(_workspace_controller.router)
api_v1_router.include_router(_workspace_member_controller.router)
api_v1_router.include_router(_workspace_invitation_controller.router)
api_v1_router.include_router(_workspace_team_controller.router)
api_v1_router.include_router(_workspace_role_controller.router)

# Project BC
from app.context.project.presentation.controllers import (
    EpicController,
    MyProjectsController,
    ProjectBoardController,
    ProjectController,
    ProjectMemberController,
    ProjectRoleController,
    RetroTemplateController,
    SprintController,
    WorkspaceRetroTemplateController,
)

_my_projects_controller = MyProjectsController()
_project_controller = ProjectController()
_project_member_controller = ProjectMemberController()
_project_role_controller = ProjectRoleController()
_sprint_controller = SprintController()
_epic_controller = EpicController()
_project_board_controller = ProjectBoardController()
_retro_template_controller = RetroTemplateController()
_workspace_retro_template_controller = WorkspaceRetroTemplateController()

api_v1_router.include_router(_my_projects_controller.router)
api_v1_router.include_router(_project_controller.router)
api_v1_router.include_router(_project_member_controller.router)
api_v1_router.include_router(_project_role_controller.router)
api_v1_router.include_router(_sprint_controller.router)
api_v1_router.include_router(_epic_controller.router)
api_v1_router.include_router(_project_board_controller.router)
api_v1_router.include_router(_retro_template_controller.router)
api_v1_router.include_router(_workspace_retro_template_controller.router)

# Task BC
from app.context.task.presentation.controllers import (
    MyTasksController,
    ProjectTaskTemplateController,
    TaskAssigneeController,
    TaskChecklistController,
    TaskController,
    TaskDetailController,
    TaskHistoryController,
    TaskMetadataController,
    TaskRelationController,
    TaskTemplateController,
)

_my_tasks_controller = MyTasksController()
_task_controller = TaskController()
_task_detail_controller = TaskDetailController()
_task_assignee_controller = TaskAssigneeController()
_task_checklist_controller = TaskChecklistController()
_task_relation_controller = TaskRelationController()
_task_metadata_controller = TaskMetadataController()
_task_history_controller = TaskHistoryController()
_task_template_controller = TaskTemplateController()
_project_task_template_controller = ProjectTaskTemplateController()

api_v1_router.include_router(_my_tasks_controller.router)
api_v1_router.include_router(_task_controller.router)
api_v1_router.include_router(_task_detail_controller.router)
api_v1_router.include_router(_task_assignee_controller.router)
api_v1_router.include_router(_task_checklist_controller.router)
api_v1_router.include_router(_task_relation_controller.router)
api_v1_router.include_router(_task_metadata_controller.router)
api_v1_router.include_router(_task_history_controller.router)
api_v1_router.include_router(_task_template_controller.router)
api_v1_router.include_router(_project_task_template_controller.router)

# TimeTracking BC
from app.context.timetracking.presentation.controllers import (
    ActivityCategoryController,
    TimeEntryApprovalController,
    TimeEntryController,
    TimeEntryTagController,
)

_time_entry_controller = TimeEntryController()
_time_entry_approval_controller = TimeEntryApprovalController()
_activity_category_controller = ActivityCategoryController()
_time_entry_tag_controller = TimeEntryTagController()

api_v1_router.include_router(_time_entry_controller.router)
api_v1_router.include_router(_time_entry_approval_controller.router)
api_v1_router.include_router(_activity_category_controller.router)
api_v1_router.include_router(_time_entry_tag_controller.router)

# Communication BC
from app.context.communication.presentation.controllers import (
    ChatController,
    CommentController,
    MeetingController,
    MessageController,
)

_chat_controller = ChatController()
_comment_controller = CommentController()
_meeting_controller = MeetingController()
_message_controller = MessageController()

api_v1_router.include_router(_chat_controller.router)
api_v1_router.include_router(_comment_controller.router)
api_v1_router.include_router(_meeting_controller.router)
api_v1_router.include_router(_message_controller.router)

# FileStorage BC
from app.context.filestorage.presentation.controllers import (
    FileController,
    FolderController,
    ShareLinkController,
    StorageController,
)

_file_controller = FileController()
_folder_controller = FolderController()
_share_link_controller = ShareLinkController()
_storage_controller = StorageController()

api_v1_router.include_router(_file_controller.router)
api_v1_router.include_router(_folder_controller.router)
api_v1_router.include_router(_share_link_controller.router)
api_v1_router.include_router(_storage_controller.router)

# Notification BC
from app.context.notification.presentation.controllers import (
    NotificationController,
    NotificationSettingsController,
)

_notification_controller = NotificationController()
_notification_settings_controller = NotificationSettingsController()

api_v1_router.include_router(_notification_controller.router)
api_v1_router.include_router(_notification_settings_controller.router)

# Analytics BC
from app.context.analytics.presentation.controllers import (
    AnalyticsQueryController,
    DashboardController,
    DashboardTemplateController,
    ReportController,
)

_analytics_query_controller = AnalyticsQueryController()
_dashboard_controller = DashboardController()
_dashboard_template_controller = DashboardTemplateController()
_report_controller = ReportController()

api_v1_router.include_router(_analytics_query_controller.router)
api_v1_router.include_router(_dashboard_controller.router)
api_v1_router.include_router(_dashboard_template_controller.router)
api_v1_router.include_router(_report_controller.router)

# WebSocket
api_v1_router.include_router(ws_router)
