"""Интеграционные тесты ReactivateWorkspaceMemberHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.reactivate_workspace_member import (
    ReactivateWorkspaceMemberCommand,
    ReactivateWorkspaceMemberHandler,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from app.context.workspace.domain.value_objects.member_source import MemberSource
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker, _NoopEventBus


@pytest.mark.integration
class TestReactivateWorkspaceMemberHandler:
    """Тесты ReactivateWorkspaceMemberHandler."""

    @pytest.fixture
    def handler(self, ws_membership_repo) -> ReactivateWorkspaceMemberHandler:
        return ReactivateWorkspaceMemberHandler(
            membership_repo=ws_membership_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_reactivate_member_success(
        self, handler, ws_repo, ws_membership_repo, make_workspace_with_membership
    ) -> None:
        data = await make_workspace_with_membership()
        ws = data["workspace"]
        membership = data["membership"]
        new_user = Id.generate()
        membership.add_member(user_id=new_user, role_id=Id.generate(), source=MemberSource.DIRECT)
        membership.deactivate_member(new_user, is_owner=False)
        membership.clear_domain_events()
        await ws_membership_repo.update(membership)

        cmd = ReactivateWorkspaceMemberCommand(
            caller_id=str(ws.owner_ids[0]),
            workspace_id=str(ws.id),
            user_id=str(new_user),
        )
        await handler.handle(cmd)

        found = await ws_membership_repo.get_by_workspace_id(ws.id)
        assert found is not None
        member = found._find_member(new_user)
        assert member is not None
        assert member.is_active is True

    async def test_reactivate_member_not_found(self, handler) -> None:
        cmd = ReactivateWorkspaceMemberCommand(
            caller_id=str(Id.generate()),
            workspace_id=str(Id.generate()),
            user_id=str(Id.generate()),
        )
        with pytest.raises(WorkspaceNotFoundException):
            await handler.handle(cmd)
