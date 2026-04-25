"""Интеграционные тесты ChangeWorkspaceMemberRoleHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.change_workspace_member_role import (
    ChangeWorkspaceMemberRoleCommand,
    ChangeWorkspaceMemberRoleHandler,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from app.context.workspace.domain.value_objects.member_source import MemberSource
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker, _NoopEventBus


@pytest.mark.integration
class TestChangeWorkspaceMemberRoleHandler:
    """Тесты ChangeWorkspaceMemberRoleHandler."""

    @pytest.fixture
    def handler(self, ws_membership_repo) -> ChangeWorkspaceMemberRoleHandler:
        return ChangeWorkspaceMemberRoleHandler(
            membership_repo=ws_membership_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_change_role_success(
        self, handler, ws_membership_repo, make_workspace_with_membership
    ) -> None:
        data = await make_workspace_with_membership()
        ws = data["workspace"]
        membership = data["membership"]
        new_user = Id.generate()
        old_role = Id.generate()
        membership.add_member(user_id=new_user, role_id=old_role, source=MemberSource.DIRECT)
        membership.clear_domain_events()
        await ws_membership_repo.update(membership)

        new_role = Id.generate()
        cmd = ChangeWorkspaceMemberRoleCommand(
            caller_id=str(ws.owner_ids[0]),
            workspace_id=str(ws.id),
            user_id=str(new_user),
            new_role_id=str(new_role),
        )
        await handler.handle(cmd)

        found = await ws_membership_repo.get_by_workspace_id(ws.id)
        assert found is not None
        member = found._find_member(new_user)
        assert member is not None
        assert member.role_id == new_role

    async def test_change_role_not_found(self, handler) -> None:
        cmd = ChangeWorkspaceMemberRoleCommand(
            caller_id=str(Id.generate()),
            workspace_id=str(Id.generate()),
            user_id=str(Id.generate()),
            new_role_id=str(Id.generate()),
        )
        with pytest.raises(WorkspaceNotFoundException):
            await handler.handle(cmd)
