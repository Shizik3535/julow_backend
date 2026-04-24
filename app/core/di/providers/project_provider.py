"""
DI-провайдеры для Project BC.

На текущем этапе здесь определены только фабрики, связанные с авторизацией
(ProjectRoleBasedPermissionChecker + адаптеры inboard/outboard портов).
Project persistence layer (mappers/repositories) ещё не реализован;
по мере его появления добавятся фабрики для репозиториев и провайдеров.
"""
from __future__ import annotations

from app.context.organization.application.ports.integration.outboard.organization_membership_provider import (
    OrganizationMembershipProvider,
)
from app.context.project.application.ports.authorization.project_permission_checker_port import (
    ProjectPermissionCheckerPort,
)
from app.context.project.application.ports.integration.inboard.organization_membership_port import (
    OrganizationMembershipPort,
)
from app.context.project.application.ports.integration.inboard.workspace_permission_checker_port import (
    WorkspacePermissionCheckerPort,
)
from app.context.project.application.ports.integration.outboard.project_permission_provider import (
    ProjectPermissionProvider,
)
from app.context.project.domain.repositories.project_membership_repository import (
    ProjectMembershipRepository,
)
from app.context.project.domain.repositories.project_repository import ProjectRepository
from app.context.project.domain.repositories.project_role_repository import ProjectRoleRepository
from app.context.project.infrastructure.authorization.project_role_based_permission_checker import (
    ProjectRoleBasedPermissionChecker,
)
from app.context.project.infrastructure.integration.inboard.organization_membership_adapter import (
    OrganizationMembershipAdapter,
)
from app.context.project.infrastructure.integration.inboard.workspace_permission_checker_adapter import (
    WorkspacePermissionCheckerAdapter,
)
from app.context.project.infrastructure.integration.outboard.project_permission_provider_impl import (
    ProjectPermissionProviderImpl,
)
from app.context.workspace.application.ports.integration.outboard.workspace_membership_provider import (
    WorkspaceMembershipProvider,
)


# --- Inboard adapters (кросс-BC) ---

def create_project_workspace_permission_checker_adapter(
    workspace_membership_provider: WorkspaceMembershipProvider,
) -> WorkspacePermissionCheckerPort:
    """
    Создать адаптер inboard-порта `WorkspacePermissionCheckerPort`
    для Project BC. Делегирует в outboard Workspace BC.
    """
    return WorkspacePermissionCheckerAdapter(
        workspace_membership_provider=workspace_membership_provider,
    )


def create_project_org_membership_adapter(
    org_membership_provider: OrganizationMembershipProvider,
) -> OrganizationMembershipPort:
    """
    Создать адаптер inboard-порта `OrganizationMembershipPort`
    для Project BC. Делегирует в outboard Organization BC.
    """
    return OrganizationMembershipAdapter(org_membership_provider=org_membership_provider)


# --- Authorization ---

def create_project_permission_checker(
    membership_repo: ProjectMembershipRepository,
    project_role_repo: ProjectRoleRepository,
    project_repo: ProjectRepository,
    workspace_permission_checker: WorkspacePermissionCheckerPort,
) -> ProjectPermissionCheckerPort:
    """
    Создать ProjectRoleBasedPermissionChecker с каскадом
    ProjectRole → WorkspaceRole → OrgRole.
    """
    return ProjectRoleBasedPermissionChecker(
        membership_repo=membership_repo,
        project_role_repo=project_role_repo,
        project_repo=project_repo,
        workspace_permission_checker=workspace_permission_checker,
    )


# --- Outboard provider (для других BC) ---

def create_project_permission_provider(
    checker: ProjectPermissionCheckerPort,
) -> ProjectPermissionProvider:
    """
    Создать реализацию outboard-порта `ProjectPermissionProvider`,
    делегирующую в `ProjectPermissionCheckerPort`.
    """
    return ProjectPermissionProviderImpl(checker=checker)
