"""
Интеграционные тесты WorkspaceRoleBasedPermissionChecker (authorization).

Проверяем логику проверки разрешений: workspace-роль, wildcard,
каскад к организации, маппинг ws → org разрешений.
"""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.domain.aggregates.workspace import Workspace
from app.context.workspace.domain.aggregates.workspace_membership import WorkspaceMembership
from app.context.workspace.domain.aggregates.workspace_role import WorkspaceRole
from app.context.workspace.domain.value_objects.member_source import MemberSource
from app.context.workspace.domain.value_objects.workspace_type import WorkspaceType
from app.context.workspace.infrastructure.authorization.workspace_role_based_permission_checker import (
    WorkspaceRoleBasedPermissionChecker,
)
from app.context.workspace.application.exceptions.authorization_exceptions import InsufficientWorkspacePermissionsException


class _StubOrgPermissionChecker:
    """Stub: отслеживает вызовы к org permission checker."""

    def __init__(self, allowed_perms: set[tuple[str, str, str]] | None = None):
        self._allowed = allowed_perms or set()
        self.calls: list[tuple[str, str, str]] = []

    async def has_permission(self, user_id: str, org_id: str, permission: str) -> bool:
        self.calls.append((user_id, org_id, permission))
        return (user_id, org_id, permission) in self._allowed


@pytest.mark.integration
class TestWorkspaceRoleBasedPermissionChecker:
    """Тесты WorkspaceRoleBasedPermissionChecker."""

    async def test_has_permission_via_workspace_role_exact(
        self, ws_repo, ws_membership_repo, ws_role_repo
    ) -> None:
        owner_id = Id.generate()
        ws = Workspace.create(name="perm-ws", owner_id=owner_id, workspace_type=WorkspaceType.TEAM)
        ws.clear_domain_events()
        await ws_repo.add(ws)

        role = WorkspaceRole.create_system(name="editor", permissions=["members.read", "members.write"])
        role.clear_domain_events()
        await ws_role_repo.add(role)

        membership = WorkspaceMembership.create(workspace_id=ws.id, owner_id=owner_id, owner_role_id=role.id)
        membership.clear_domain_events()
        await ws_membership_repo.add(membership)

        checker = WorkspaceRoleBasedPermissionChecker(
            membership_repo=ws_membership_repo,
            workspace_role_repo=ws_role_repo,
            ws_repo=ws_repo,
            org_permission_checker=None,
        )
        result = await checker.has_permission(owner_id, ws.id, "members.read")
        assert result is True

    async def test_has_permission_via_wildcard(
        self, ws_repo, ws_membership_repo, ws_role_repo
    ) -> None:
        owner_id = Id.generate()
        ws = Workspace.create(name="wild-ws", owner_id=owner_id, workspace_type=WorkspaceType.TEAM)
        ws.clear_domain_events()
        await ws_repo.add(ws)

        role = WorkspaceRole.create_system(name="admin", permissions=["members.*"])
        role.clear_domain_events()
        await ws_role_repo.add(role)

        membership = WorkspaceMembership.create(workspace_id=ws.id, owner_id=owner_id, owner_role_id=role.id)
        membership.clear_domain_events()
        await ws_membership_repo.add(membership)

        checker = WorkspaceRoleBasedPermissionChecker(
            membership_repo=ws_membership_repo,
            workspace_role_repo=ws_role_repo,
            ws_repo=ws_repo,
            org_permission_checker=None,
        )
        assert await checker.has_permission(owner_id, ws.id, "members.read") is True
        assert await checker.has_permission(owner_id, ws.id, "members.write") is True
        assert await checker.has_permission(owner_id, ws.id, "teams.read") is False

    async def test_has_permission_no_membership_no_org(
        self, ws_repo, ws_membership_repo, ws_role_repo
    ) -> None:
        owner_id = Id.generate()
        ws = Workspace.create(name="no-member-ws", owner_id=owner_id, workspace_type=WorkspaceType.TEAM)
        ws.clear_domain_events()
        await ws_repo.add(ws)

        checker = WorkspaceRoleBasedPermissionChecker(
            membership_repo=ws_membership_repo,
            workspace_role_repo=ws_role_repo,
            ws_repo=ws_repo,
            org_permission_checker=None,
        )
        result = await checker.has_permission(Id.generate(), ws.id, "members.read")
        assert result is False

    async def test_has_permission_cascade_to_org(
        self, ws_repo, ws_membership_repo, ws_role_repo
    ) -> None:
        owner_id = Id.generate()
        org_id = Id.generate()
        ws = Workspace.create(
            name="org-ws", owner_id=owner_id, workspace_type=WorkspaceType.TEAM, organization_id=org_id
        )
        ws.clear_domain_events()
        await ws_repo.add(ws)

        org_checker = _StubOrgPermissionChecker(
            allowed_perms={(str(owner_id), str(org_id), "workspaces.members.read")}
        )

        checker = WorkspaceRoleBasedPermissionChecker(
            membership_repo=ws_membership_repo,
            workspace_role_repo=ws_role_repo,
            ws_repo=ws_repo,
            org_permission_checker=org_checker,
        )
        result = await checker.has_permission(owner_id, ws.id, "members.read")
        assert result is True
        assert len(org_checker.calls) >= 1

    async def test_require_permission_raises(
        self, ws_repo, ws_membership_repo, ws_role_repo
    ) -> None:
        owner_id = Id.generate()
        ws = Workspace.create(name="deny-ws", owner_id=owner_id, workspace_type=WorkspaceType.TEAM)
        ws.clear_domain_events()
        await ws_repo.add(ws)

        checker = WorkspaceRoleBasedPermissionChecker(
            membership_repo=ws_membership_repo,
            workspace_role_repo=ws_role_repo,
            ws_repo=ws_repo,
            org_permission_checker=None,
        )
        with pytest.raises(InsufficientWorkspacePermissionsException):
            await checker.require_permission(Id.generate(), ws.id, "members.read")

    async def test_map_to_org_permission(self) -> None:
        assert WorkspaceRoleBasedPermissionChecker._map_to_org_permission("ws.*") == "workspaces.*"
        assert WorkspaceRoleBasedPermissionChecker._map_to_org_permission("members.write") == "workspaces.members.write"
        assert WorkspaceRoleBasedPermissionChecker._map_to_org_permission("roles.read") == "workspaces.roles.read"
        assert WorkspaceRoleBasedPermissionChecker._map_to_org_permission("teams.*") == "workspaces.teams.*"
