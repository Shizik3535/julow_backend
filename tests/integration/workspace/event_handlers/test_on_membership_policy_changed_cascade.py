"""Интеграционные тесты OnMembershipPolicyCascade."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.event_handlers.on_membership_policy_changed_cascade import (
    OnMembershipPolicyCascade,
)


@pytest.mark.integration
class TestOnMembershipPolicyCascade:
    """Тесты OnMembershipPolicyCascade."""

    @pytest.fixture
    def handler(self, ws_repo) -> OnMembershipPolicyCascade:
        return OnMembershipPolicyCascade(ws_repo=ws_repo)

    async def test_cascade_to_inheriting_child(
        self, handler, ws_repo, make_workspace
    ) -> None:
        parent = await make_workspace(name="Mem Parent")
        child = await make_workspace(name="Mem Child", parent_workspace_id=parent.id)

        from app.context.workspace.domain.value_objects.membership_policy import MembershipPolicy

        child_policy = MembershipPolicy(
            allow_invitation_links=False,
            default_role="member",
            require_approval=False,
            max_members=None,
            allowed_email_domains=[],
            auto_add_from_org=False,
            inherit_from_parent=True,
        )
        child.update_membership_policy(child_policy)
        child.clear_domain_events()
        await ws_repo.update(child)

        new_policy = MembershipPolicy(
            allow_invitation_links=True,
            default_role="editor",
            require_approval=True,
            max_members=100,
            allowed_email_domains=["example.com"],
            auto_add_from_org=True,
            inherit_from_parent=False,
        )
        parent.update_membership_policy(new_policy)
        parent.clear_domain_events()
        await ws_repo.update(parent)

        event = {
            "event_type": "MembershipPolicyChanged",
            "payload": {"workspace_id": str(parent.id)},
        }
        await handler.handle(event)

        updated_child = await ws_repo.get_by_id(child.id)
        assert updated_child is not None
        assert updated_child.membership_policy.allow_invitation_links is True
        assert updated_child.membership_policy.max_members == 100
        assert updated_child.membership_policy.auto_add_from_org is True

    async def test_skip_non_inheriting_child(
        self, handler, ws_repo, make_workspace
    ) -> None:
        parent = await make_workspace(name="Mem Parent 2")
        child = await make_workspace(name="Mem Child 2", parent_workspace_id=parent.id)

        from app.context.workspace.domain.value_objects.membership_policy import MembershipPolicy

        child_policy = MembershipPolicy(
            allow_invitation_links=False,
            default_role="member",
            require_approval=False,
            max_members=None,
            allowed_email_domains=[],
            auto_add_from_org=False,
            inherit_from_parent=False,
        )
        child.update_membership_policy(child_policy)
        child.clear_domain_events()
        await ws_repo.update(child)

        new_policy = MembershipPolicy(
            allow_invitation_links=True,
            default_role="editor",
            require_approval=True,
            max_members=50,
            allowed_email_domains=[],
            auto_add_from_org=True,
            inherit_from_parent=False,
        )
        parent.update_membership_policy(new_policy)
        parent.clear_domain_events()
        await ws_repo.update(parent)

        event = {
            "event_type": "MembershipPolicyChanged",
            "payload": {"workspace_id": str(parent.id)},
        }
        await handler.handle(event)

        updated_child = await ws_repo.get_by_id(child.id)
        assert updated_child is not None
        assert updated_child.membership_policy.allow_invitation_links is False

    async def test_ignore_non_target_event(self, handler) -> None:
        event = {"event_type": "OtherEvent", "payload": {}}
        await handler.handle(event)
