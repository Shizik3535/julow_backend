"""
DI-провайдеры для Workspace BC.

На текущем этапе здесь определены только фабрики, связанные с авторизацией.
Workspace persistence layer (mappers/repositories) ещё не реализован;
по мере его появления добавятся фабрики для репозиториев и провайдеров.
"""
from __future__ import annotations

from app.context.organization.application.ports.integration.outboard.organization_permission_provider import (
    OrganizationPermissionProvider,
)
from app.context.workspace.application.ports.authorization.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.workspace.application.ports.integration.inboard.organization_permission_checker_port import (
    OrganizationPermissionCheckerPort,
)
from app.context.workspace.domain.repositories.workspace_membership_repository import (
    WorkspaceMembershipRepository,
)
from app.context.workspace.domain.repositories.workspace_repository import WorkspaceRepository
from app.context.workspace.domain.repositories.workspace_role_repository import WorkspaceRoleRepository
from app.context.workspace.infrastructure.authorization.workspace_role_based_permission_checker import (
    WorkspaceRoleBasedPermissionChecker,
)
from app.context.workspace.infrastructure.integration.inboard.organization_permission_checker_adapter import (
    OrganizationPermissionCheckerAdapter,
)


# --- Inboard adapters (кросс-BC) ---

def create_ws_org_permission_checker_adapter(
    org_permission_provider: OrganizationPermissionProvider,
) -> OrganizationPermissionCheckerPort:
    """
    Создать адаптер inboard-порта `OrganizationPermissionCheckerPort`
    для Workspace BC. Делегирует в outboard Organization BC.
    """
    return OrganizationPermissionCheckerAdapter(org_permission_provider=org_permission_provider)


# --- Authorization ---

def create_workspace_permission_checker(
    membership_repo: WorkspaceMembershipRepository,
    workspace_role_repo: WorkspaceRoleRepository,
    ws_repo: WorkspaceRepository,
    org_permission_checker: OrganizationPermissionCheckerPort,
) -> WorkspacePermissionCheckerPort:
    """
    Создать WorkspaceRoleBasedPermissionChecker с каскадом OrgRole → Workspace.
    """
    return WorkspaceRoleBasedPermissionChecker(
        membership_repo=membership_repo,
        workspace_role_repo=workspace_role_repo,
        ws_repo=ws_repo,
        org_permission_checker=org_permission_checker,
    )
