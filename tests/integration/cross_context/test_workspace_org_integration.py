"""
Cross-context: Organization + Workspace.
Тестируем сценарий создания workspace в организации
с реальными Organization BC репозиториями.
"""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.create_workspace import (
    CreateWorkspaceCommand,
    CreateWorkspaceHandler,
)
from app.context.workspace.application.event_handlers.on_org_member_joined_auto_add import (
    OnOrgMemberJoinedAutoAdd,
)
from app.context.workspace.domain.value_objects.member_source import MemberSource
from app.context.workspace.domain.value_objects.workspace_type import WorkspaceType
from tests.integration.workspace.conftest import (
    _AlwaysAllowOrgPermissionChecker,
    _StubIdentityUserPort,
    _NoopEventBus,
)


@pytest.mark.integration
class TestCreateWorkspaceInOrgCrossContext:
    """Cross-context: создание workspace в организации."""

    async def test_create_workspace_with_real_org(
        self, ws_repo, ws_membership_repo, ws_role_repo, make_org_with_membership
    ) -> None:
        data = await make_org_with_membership()
        org = data["org"]
        owner_id = data["owner_id"]

        handler = CreateWorkspaceHandler(
            ws_repo=ws_repo,
            membership_repo=ws_membership_repo,
            role_repo=ws_role_repo,
            identity_port=_StubIdentityUserPort(),
            org_permission_checker=_AlwaysAllowOrgPermissionChecker(),
            event_bus=_NoopEventBus(),
        )
        cmd = CreateWorkspaceCommand(
            caller_id=str(owner_id),
            name="Org Workspace",
            owner_id=str(owner_id),
            workspace_type="TEAM",
            organization_id=str(org.id),
        )
        result = await handler.handle(cmd)

        assert result.organization_id == str(org.id)
        assert result.name == "Org Workspace"


@pytest.mark.integration
class TestOrgMemberAutoAddCrossContext:
    """Cross-context: авто-добавление участника организации в workspace."""

    async def test_auto_add_on_org_member_joined(
        self, ws_repo, ws_membership_repo, ws_role_repo, make_org_with_membership, make_ws_with_membership
    ) -> None:
        data = await make_org_with_membership()
        org = data["org"]
        owner_id = data["owner_id"]

        ws_data = await make_ws_with_membership(organization_id=org.id)
        ws = ws_data["workspace"]

        from app.context.workspace.domain.value_objects.membership_policy import MembershipPolicy
        policy = MembershipPolicy(auto_add_from_org=True, default_role="member")
        ws.update_membership_policy(policy)
        ws.clear_domain_events()
        await ws_repo.update(ws)

        member_role = await ws_role_repo.get_by_name("member")

        new_user = Id.generate()
        handler = OnOrgMemberJoinedAutoAdd(
            ws_repo=ws_repo,
            membership_repo=ws_membership_repo,
            role_repo=ws_role_repo,
        )
        event = {
            "event_type": "OrgMemberJoined",
            "payload": {"org_id": str(org.id), "user_id": str(new_user)},
        }
        await handler.handle(event)

        membership = await ws_membership_repo.get_by_workspace_id(ws.id)
        assert membership is not None
        member = membership._find_member(new_user)
        assert member is not None
        assert member.source == MemberSource.ORGANIZATION
