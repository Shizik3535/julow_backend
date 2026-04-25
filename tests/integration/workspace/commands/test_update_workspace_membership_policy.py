"""Интеграционные тесты UpdateWorkspaceMembershipPolicyHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.update_workspace_membership_policy import (
    UpdateWorkspaceMembershipPolicyCommand,
    UpdateWorkspaceMembershipPolicyHandler,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker, _NoopEventBus


@pytest.mark.integration
class TestUpdateWorkspaceMembershipPolicyHandler:
    """Тесты UpdateWorkspaceMembershipPolicyHandler."""

    @pytest.fixture
    def handler(self, ws_repo) -> UpdateWorkspaceMembershipPolicyHandler:
        return UpdateWorkspaceMembershipPolicyHandler(
            ws_repo=ws_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_update_membership_policy_success(self, handler, ws_repo, make_workspace) -> None:
        ws = await make_workspace()
        cmd = UpdateWorkspaceMembershipPolicyCommand(
            caller_id=str(ws.owner_ids[0]),
            workspace_id=str(ws.id),
            allow_invitation_links=True,
            max_members=50,
            auto_add_from_org=True,
        )
        await handler.handle(cmd)

        found = await ws_repo.get_by_id(ws.id)
        assert found is not None
        assert found.membership_policy.allow_invitation_links is True
        assert found.membership_policy.max_members == 50
        assert found.membership_policy.auto_add_from_org is True

    async def test_update_membership_policy_not_found(self, handler) -> None:
        cmd = UpdateWorkspaceMembershipPolicyCommand(
            caller_id=str(Id.generate()),
            workspace_id=str(Id.generate()),
            max_members=10,
        )
        with pytest.raises(WorkspaceNotFoundException):
            await handler.handle(cmd)
