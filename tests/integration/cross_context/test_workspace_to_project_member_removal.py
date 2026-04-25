"""Cross-context: Workspace → Project — при удалении участника workspace,
участник удаляется из всех проектов workspace."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.event_handlers.on_workspace_member_removed import (
    OnWorkspaceMemberRemoved,
)
from app.context.workspace.domain.events.workspace_membership_events import WorkspaceMemberRemoved
from app.shared.application.messaging.domain_event_bus import DomainEventBus


class _NoopEventBus(DomainEventBus):
    async def publish_all(self, events: list) -> None:
        pass

    async def publish(self, event) -> None:
        pass


@pytest.mark.integration
class TestWorkspaceMemberRemovedRemovesProjectMember:
    """Cross-context: WorkspaceMemberRemoved → Project membership updated."""

    @pytest.fixture
    def handler(self, project_repo, proj_membership_repo) -> OnWorkspaceMemberRemoved:
        return OnWorkspaceMemberRemoved(
            project_repo=project_repo,
            membership_repo=proj_membership_repo,
            event_bus=_NoopEventBus(),
        )

    async def test_member_removed_from_all_projects(
        self, handler, proj_membership_repo, make_ws_with_membership, make_project_with_membership, make_user,
    ) -> None:
        ws_data = await make_ws_with_membership()
        ws = ws_data["workspace"]
        owner_id = ws_data["owner_id"]

        proj1 = await make_project_with_membership(workspace_id=ws.id, owner_id=owner_id)
        proj2 = await make_project_with_membership(workspace_id=ws.id, owner_id=owner_id)

        new_user = await make_user()
        proj1["membership"].add_member(user_id=new_user.id, role_id=proj1["system_roles"][0].id)
        proj1["membership"].clear_domain_events()
        await proj_membership_repo.update(proj1["membership"])

        proj2["membership"].add_member(user_id=new_user.id, role_id=proj2["system_roles"][0].id)
        proj2["membership"].clear_domain_events()
        await proj_membership_repo.update(proj2["membership"])

        event = WorkspaceMemberRemoved(
            workspace_id=str(ws.id),
            user_id=str(new_user.id),
        )
        await handler.handle(event)

        m1 = await proj_membership_repo.get_by_project_id(proj1["project"].id)
        m2 = await proj_membership_repo.get_by_project_id(proj2["project"].id)
        assert m1 is not None
        assert m2 is not None
        assert not any(m.user_id == new_user.id and m.is_active for m in m1.members)
        assert not any(m.user_id == new_user.id and m.is_active for m in m2.members)

    async def test_owner_not_removed(
        self, handler, proj_membership_repo, make_ws_with_membership, make_project_with_membership,
    ) -> None:
        ws_data = await make_ws_with_membership()
        ws = ws_data["workspace"]
        owner_id = ws_data["owner_id"]

        proj_data = await make_project_with_membership(workspace_id=ws.id, owner_id=owner_id)

        event = WorkspaceMemberRemoved(
            workspace_id=str(ws.id),
            user_id=str(owner_id),
        )
        await handler.handle(event)

        m = await proj_membership_repo.get_by_project_id(proj_data["project"].id)
        assert m is not None
        assert any(mem.user_id == owner_id for mem in m.members)
