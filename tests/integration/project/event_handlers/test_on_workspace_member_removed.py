"""Интеграционные тесты OnWorkspaceMemberRemoved (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.event_handlers.on_workspace_member_removed import (
    OnWorkspaceMemberRemoved,
)
from app.context.workspace.domain.events.workspace_membership_events import WorkspaceMemberRemoved
from tests.integration.project.conftest import _NoopEventBus


@pytest.mark.integration
class TestOnWorkspaceMemberRemoved:
    """Тесты OnWorkspaceMemberRemoved — cross-BC event handler."""

    @pytest.fixture
    def handler(self, project_repo, membership_repo, event_bus_stub) -> OnWorkspaceMemberRemoved:
        return OnWorkspaceMemberRemoved(
            project_repo=project_repo,
            membership_repo=membership_repo,
            event_bus=event_bus_stub,
        )

    async def test_removes_member_from_projects(self, handler, membership_repo, make_project_with_membership, make_user) -> None:
        ws_id = Id.generate()
        data = await make_project_with_membership(workspace_id=ws_id)
        project = data["project"]
        membership = data["membership"]
        owner_id = data["owner_id"]

        new_user = await make_user()
        membership.add_member(user_id=new_user.id, role_id=data["system_roles"][0].id)
        membership.clear_domain_events()
        await membership_repo.update(membership)

        event = WorkspaceMemberRemoved(
            workspace_id=str(ws_id),
            user_id=str(new_user.id),
        )
        await handler.handle(event)

        found = await membership_repo.get_by_project_id(project.id)
        assert found is not None
        assert not any(m.user_id == new_user.id and m.is_active for m in found.members)

    async def test_skips_owner_removal(self, handler, membership_repo, make_project_with_membership) -> None:
        ws_id = Id.generate()
        data = await make_project_with_membership(workspace_id=ws_id)
        project = data["project"]
        owner_id = data["owner_id"]

        event = WorkspaceMemberRemoved(
            workspace_id=str(ws_id),
            user_id=str(owner_id),
        )
        await handler.handle(event)

        found = await membership_repo.get_by_project_id(project.id)
        assert found is not None
        assert any(m.user_id == owner_id for m in found.members)

    async def test_idempotent_no_error(self, handler, make_project_with_membership) -> None:
        ws_id = Id.generate()
        data = await make_project_with_membership(workspace_id=ws_id)
        non_member_id = Id.generate()

        event = WorkspaceMemberRemoved(
            workspace_id=str(ws_id),
            user_id=str(non_member_id),
        )
        # Should not raise
        await handler.handle(event)

    async def test_no_projects_in_workspace(self, handler) -> None:
        event = WorkspaceMemberRemoved(
            workspace_id=str(Id.generate()),
            user_id=str(Id.generate()),
        )
        # Should not raise
        await handler.handle(event)
