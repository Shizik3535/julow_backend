"""Интеграционные тесты UpdateWorkspaceMemberDisplayNameHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.update_workspace_member_display_name import (
    UpdateWorkspaceMemberDisplayNameCommand,
    UpdateWorkspaceMemberDisplayNameHandler,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from app.context.workspace.domain.value_objects.member_source import MemberSource
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker, _NoopEventBus


@pytest.mark.integration
class TestUpdateWorkspaceMemberDisplayNameHandler:
    """Тесты UpdateWorkspaceMemberDisplayNameHandler."""

    @pytest.fixture
    def handler(self, ws_membership_repo) -> UpdateWorkspaceMemberDisplayNameHandler:
        return UpdateWorkspaceMemberDisplayNameHandler(
            membership_repo=ws_membership_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_update_display_name_success(
        self, handler, ws_membership_repo, make_workspace_with_membership
    ) -> None:
        data = await make_workspace_with_membership()
        ws = data["workspace"]
        membership = data["membership"]
        new_user = Id.generate()
        membership.add_member(user_id=new_user, role_id=Id.generate(), source=MemberSource.DIRECT)
        membership.clear_domain_events()
        await ws_membership_repo.update(membership)

        cmd = UpdateWorkspaceMemberDisplayNameCommand(
            caller_id=str(ws.owner_ids[0]),
            workspace_id=str(ws.id),
            user_id=str(new_user),
            display_name="New Display Name",
        )
        await handler.handle(cmd)

        found = await ws_membership_repo.get_by_workspace_id(ws.id)
        assert found is not None
        member = found._find_member(new_user)
        assert member is not None
        assert member.display_name == "New Display Name"

    async def test_update_display_name_not_found(self, handler) -> None:
        cmd = UpdateWorkspaceMemberDisplayNameCommand(
            caller_id=str(Id.generate()),
            workspace_id=str(Id.generate()),
            user_id=str(Id.generate()),
            display_name="Nope",
        )
        with pytest.raises(WorkspaceNotFoundException):
            await handler.handle(cmd)
