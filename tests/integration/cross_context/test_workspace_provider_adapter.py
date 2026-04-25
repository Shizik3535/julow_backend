"""
Cross-context: Workspace → Identity.
Тестируем WorkspaceProviderAdapter и WorkspaceMembershipProviderAdapter
через реальные Identity BC репозитории.
"""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.infrastructure.integration.outboard.workspace_provider_adapter import (
    WorkspaceProviderAdapter,
)
from app.context.workspace.infrastructure.integration.outboard.workspace_membership_provider_adapter import (
    WorkspaceMembershipProviderAdapter,
)


@pytest.mark.integration
class TestWorkspaceProviderCrossContext:
    """Cross-context тесты WorkspaceProviderAdapter."""

    async def test_workspace_exists_across_bc(self, ws_repo, make_ws) -> None:
        ws = await make_ws()
        adapter = WorkspaceProviderAdapter(repo=ws_repo)

        result = await adapter.workspace_exists(str(ws.id))
        assert result is True

    async def test_get_workspace_across_bc(self, ws_repo, make_ws) -> None:
        ws = await make_ws(name="Cross WS")
        adapter = WorkspaceProviderAdapter(repo=ws_repo)

        result = await adapter.get_workspace(str(ws.id))
        assert result is not None
        assert result.name == "Cross WS"

    async def test_get_workspaces_by_org_across_bc(
        self, ws_repo, make_ws, make_org
    ) -> None:
        org = await make_org()
        await make_ws(organization_id=org.id, name="Org Cross WS")
        adapter = WorkspaceProviderAdapter(repo=ws_repo)

        result = await adapter.get_workspaces_by_organization(str(org.id))
        assert len(result) >= 1


@pytest.mark.integration
class TestWorkspaceMembershipProviderCrossContext:
    """Cross-context тесты WorkspaceMembershipProviderAdapter."""

    async def test_is_member_across_bc(
        self, ws_repo, ws_membership_repo, ws_role_repo, make_ws_with_membership
    ) -> None:
        data = await make_ws_with_membership()
        ws = data["workspace"]
        owner_id = data["owner_id"]

        adapter = WorkspaceMembershipProviderAdapter(
            membership_repo=ws_membership_repo,
            workspace_role_repo=ws_role_repo,
            workspace_repo=ws_repo,
        )
        result = await adapter.is_member(str(ws.id), str(owner_id))
        assert result is True

    async def test_get_members_across_bc(
        self, ws_repo, ws_membership_repo, ws_role_repo, make_ws_with_membership
    ) -> None:
        data = await make_ws_with_membership()
        ws = data["workspace"]

        adapter = WorkspaceMembershipProviderAdapter(
            membership_repo=ws_membership_repo,
            workspace_role_repo=ws_role_repo,
            workspace_repo=ws_repo,
        )
        result = await adapter.get_members(str(ws.id))
        assert len(result) >= 1
