"""
Интеграционные тесты WorkspaceMembershipProviderAdapter (outboard).

Адаптер предоставляет данные членства и разрешений другим BC.
Использует реальные Sql-репозитории для проверки маппинга AR → DTO.
"""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.domain.aggregates.workspace_membership import WorkspaceMembership
from app.context.workspace.domain.aggregates.workspace_role import WorkspaceRole
from app.context.workspace.domain.value_objects.member_source import MemberSource
from app.context.workspace.infrastructure.integration.outboard.workspace_membership_provider_adapter import (
    WorkspaceMembershipProviderAdapter,
)


@pytest.mark.integration
class TestWorkspaceMembershipProviderAdapter:
    """Тесты WorkspaceMembershipProviderAdapter."""

    async def test_is_member_true(
        self, ws_repo, ws_membership_repo, ws_role_repo, make_workspace
    ) -> None:
        ws = await make_workspace()
        owner_id = ws.owner_ids[0]
        membership = WorkspaceMembership.create(workspace_id=ws.id, owner_id=owner_id)
        membership.clear_domain_events()
        await ws_membership_repo.add(membership)

        adapter = WorkspaceMembershipProviderAdapter(
            membership_repo=ws_membership_repo,
            workspace_role_repo=ws_role_repo,
            workspace_repo=ws_repo,
        )
        result = await adapter.is_member(str(ws.id), str(owner_id))
        assert result is True

    async def test_is_member_false(
        self, ws_repo, ws_membership_repo, ws_role_repo, make_workspace
    ) -> None:
        ws = await make_workspace()
        adapter = WorkspaceMembershipProviderAdapter(
            membership_repo=ws_membership_repo,
            workspace_role_repo=ws_role_repo,
            workspace_repo=ws_repo,
        )
        result = await adapter.is_member(str(ws.id), str(Id.generate()))
        assert result is False

    async def test_get_member_role(
        self, ws_repo, ws_membership_repo, ws_role_repo, make_workspace
    ) -> None:
        ws = await make_workspace()
        owner_id = ws.owner_ids[0]
        role = WorkspaceRole.create_system(name="owner", permissions=["ws.*"])
        role.clear_domain_events()
        await ws_role_repo.add(role)

        membership = WorkspaceMembership.create(workspace_id=ws.id, owner_id=owner_id)
        membership.clear_domain_events()
        await ws_membership_repo.add(membership)

        adapter = WorkspaceMembershipProviderAdapter(
            membership_repo=ws_membership_repo,
            workspace_role_repo=ws_role_repo,
            workspace_repo=ws_repo,
        )
        result = await adapter.get_member_role(str(ws.id), str(owner_id))
        assert result is not None

    async def test_get_member_role_not_member(
        self, ws_repo, ws_membership_repo, ws_role_repo, make_workspace
    ) -> None:
        ws = await make_workspace()
        adapter = WorkspaceMembershipProviderAdapter(
            membership_repo=ws_membership_repo,
            workspace_role_repo=ws_role_repo,
            workspace_repo=ws_repo,
        )
        result = await adapter.get_member_role(str(ws.id), str(Id.generate()))
        assert result is None

    async def test_get_members(
        self, ws_repo, ws_membership_repo, ws_role_repo, make_workspace
    ) -> None:
        ws = await make_workspace()
        owner_id = ws.owner_ids[0]
        membership = WorkspaceMembership.create(workspace_id=ws.id, owner_id=owner_id)
        membership.clear_domain_events()
        await ws_membership_repo.add(membership)

        adapter = WorkspaceMembershipProviderAdapter(
            membership_repo=ws_membership_repo,
            workspace_role_repo=ws_role_repo,
            workspace_repo=ws_repo,
        )
        result = await adapter.get_members(str(ws.id))
        assert len(result) >= 1
        assert any(m.user_id == str(owner_id) for m in result)

    async def test_get_members_empty(
        self, ws_repo, ws_membership_repo, ws_role_repo, make_workspace
    ) -> None:
        ws = await make_workspace()
        adapter = WorkspaceMembershipProviderAdapter(
            membership_repo=ws_membership_repo,
            workspace_role_repo=ws_role_repo,
            workspace_repo=ws_repo,
        )
        result = await adapter.get_members(str(ws.id))
        assert result == []

    async def test_has_permission_with_role(
        self, ws_repo, ws_membership_repo, ws_role_repo, make_workspace
    ) -> None:
        ws = await make_workspace()
        owner_id = ws.owner_ids[0]
        role = WorkspaceRole.create_system(name="owner", permissions=["ws.*", "members.read", "members.write"])
        role.clear_domain_events()
        await ws_role_repo.add(role)

        membership = WorkspaceMembership.create(workspace_id=ws.id, owner_id=owner_id)
        membership.change_member_role(user_id=owner_id, new_role_id=role.id)
        membership.clear_domain_events()
        await ws_membership_repo.add(membership)

        adapter = WorkspaceMembershipProviderAdapter(
            membership_repo=ws_membership_repo,
            workspace_role_repo=ws_role_repo,
            workspace_repo=ws_repo,
        )
        result = await adapter.has_permission(str(ws.id), str(owner_id), "members.read")
        assert result is True

    async def test_has_permission_no_role(
        self, ws_repo, ws_membership_repo, ws_role_repo, make_workspace
    ) -> None:
        ws = await make_workspace()
        adapter = WorkspaceMembershipProviderAdapter(
            membership_repo=ws_membership_repo,
            workspace_role_repo=ws_role_repo,
            workspace_repo=ws_repo,
        )
        result = await adapter.has_permission(str(ws.id), str(Id.generate()), "members.read")
        assert result is False

    async def test_permission_grants_wildcard(self) -> None:
        from app.context.workspace.infrastructure.integration.outboard.workspace_membership_provider_adapter import (
            WorkspaceMembershipProviderAdapter,
        )
        assert WorkspaceMembershipProviderAdapter._permission_grants(["members.*"], "members.read") is True
        assert WorkspaceMembershipProviderAdapter._permission_grants(["members.*"], "members.write") is True
        assert WorkspaceMembershipProviderAdapter._permission_grants(["ws.*"], "ws.settings.write") is True
        assert WorkspaceMembershipProviderAdapter._permission_grants(["ws.*"], "members.read") is False
        assert WorkspaceMembershipProviderAdapter._permission_grants(["members.read"], "members.read") is True
        assert WorkspaceMembershipProviderAdapter._permission_grants(["members.read"], "members.write") is False
