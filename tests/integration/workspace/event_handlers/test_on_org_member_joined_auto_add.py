"""Интеграционные тесты OnOrgMemberJoinedAutoAdd."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.event_handlers.on_org_member_joined_auto_add import (
    OnOrgMemberJoinedAutoAdd,
)
from app.context.workspace.domain.aggregates.workspace_role import WorkspaceRole
from app.context.workspace.domain.value_objects.member_source import MemberSource
from app.context.workspace.domain.value_objects.workspace_type import WorkspaceType


@pytest.mark.integration
class TestOnOrgMemberJoinedAutoAdd:
    """Тесты OnOrgMemberJoinedAutoAdd."""

    @pytest.fixture
    def handler(self, ws_repo, ws_membership_repo, ws_role_repo) -> OnOrgMemberJoinedAutoAdd:
        return OnOrgMemberJoinedAutoAdd(
            ws_repo=ws_repo,
            membership_repo=ws_membership_repo,
            role_repo=ws_role_repo,
        )

    async def test_auto_add_when_policy_enabled(
        self, handler, ws_repo, ws_membership_repo, ws_role_repo, make_workspace_with_membership
    ) -> None:
        org_id = Id.generate()
        data = await make_workspace_with_membership(organization_id=org_id)
        ws = data["workspace"]

        from app.context.workspace.domain.value_objects.membership_policy import MembershipPolicy
        policy = MembershipPolicy(auto_add_from_org=True, default_role="member")
        ws.update_membership_policy(policy)
        ws.clear_domain_events()
        await ws_repo.update(ws)

        member_role = await ws_role_repo.get_by_name("member")

        new_user = Id.generate()
        event = {
            "event_type": "OrgMemberJoined",
            "payload": {"org_id": str(org_id), "user_id": str(new_user)},
        }
        await handler.handle(event)

        membership = await ws_membership_repo.get_by_workspace_id(ws.id)
        assert membership is not None
        member = membership._find_member(new_user)
        assert member is not None
        assert member.source == MemberSource.ORGANIZATION

    async def test_skip_when_policy_disabled(
        self, handler, ws_repo, ws_membership_repo, make_workspace_with_membership
    ) -> None:
        org_id = Id.generate()
        data = await make_workspace_with_membership(organization_id=org_id)
        ws = data["workspace"]

        from app.context.workspace.domain.value_objects.membership_policy import MembershipPolicy
        policy = MembershipPolicy(auto_add_from_org=False)
        ws.update_membership_policy(policy)
        ws.clear_domain_events()
        await ws_repo.update(ws)

        new_user = Id.generate()
        event = {
            "event_type": "OrgMemberJoined",
            "payload": {"org_id": str(org_id), "user_id": str(new_user)},
        }
        await handler.handle(event)

        membership = await ws_membership_repo.get_by_workspace_id(ws.id)
        assert membership is not None
        member = membership._find_member(new_user)
        assert member is None

    async def test_idempotent_skip_existing_member(
        self, handler, ws_repo, ws_membership_repo, make_workspace_with_membership
    ) -> None:
        org_id = Id.generate()
        data = await make_workspace_with_membership(organization_id=org_id)
        ws = data["workspace"]
        owner_id = data["owner_id"]

        from app.context.workspace.domain.value_objects.membership_policy import MembershipPolicy
        policy = MembershipPolicy(auto_add_from_org=True, default_role="member")
        ws.update_membership_policy(policy)
        ws.clear_domain_events()
        await ws_repo.update(ws)

        event = {
            "event_type": "OrgMemberJoined",
            "payload": {"org_id": str(org_id), "user_id": str(owner_id)},
        }
        await handler.handle(event)

        membership = await ws_membership_repo.get_by_workspace_id(ws.id)
        assert membership is not None
        assert len(membership.members) == 1

    async def test_ignore_non_target_event_type(self, handler) -> None:
        event = {
            "event_type": "OrgMemberRemoved",
            "payload": {"org_id": str(Id.generate()), "user_id": str(Id.generate())},
        }
        await handler.handle(event)

    async def test_graceful_skip_missing_org_id(self, handler) -> None:
        event = {
            "event_type": "OrgMemberJoined",
            "payload": {"user_id": str(Id.generate())},
        }
        await handler.handle(event)

    async def test_graceful_skip_missing_user_id(self, handler) -> None:
        event = {
            "event_type": "OrgMemberJoined",
            "payload": {"org_id": str(Id.generate())},
        }
        await handler.handle(event)
