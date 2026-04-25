from fastapi import APIRouter

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

_workspace_controller = WorkspaceController()
_workspace_member_controller = WorkspaceMemberController()
_workspace_invitation_controller = WorkspaceInvitationController()
_workspace_team_controller = WorkspaceTeamController()
_workspace_role_controller = WorkspaceRoleController()
_org_workspace_controller = OrgWorkspaceController()

api_v1_router.include_router(_workspace_controller.router)
api_v1_router.include_router(_workspace_member_controller.router)
api_v1_router.include_router(_workspace_invitation_controller.router)
api_v1_router.include_router(_workspace_team_controller.router)
api_v1_router.include_router(_workspace_role_controller.router)
api_v1_router.include_router(_org_workspace_controller.router)
