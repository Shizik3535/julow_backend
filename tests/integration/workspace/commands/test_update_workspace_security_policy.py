"""Интеграционные тесты UpdateWorkspaceSecurityPolicyHandler."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.application.commands.update_workspace_security_policy import (
    UpdateWorkspaceSecurityPolicyCommand,
    UpdateWorkspaceSecurityPolicyHandler,
)
from app.context.workspace.domain.exceptions.workspace_exceptions import WorkspaceNotFoundException
from tests.integration.workspace.conftest import _AlwaysAllowPermissionChecker, _NoopEventBus


@pytest.mark.integration
class TestUpdateWorkspaceSecurityPolicyHandler:
    """Тесты UpdateWorkspaceSecurityPolicyHandler."""

    @pytest.fixture
    def handler(self, ws_repo) -> UpdateWorkspaceSecurityPolicyHandler:
        return UpdateWorkspaceSecurityPolicyHandler(
            ws_repo=ws_repo,
            permission_checker=_AlwaysAllowPermissionChecker(),
            event_bus=_NoopEventBus(),
        )

    async def test_update_security_policy_success(self, handler, ws_repo, make_workspace) -> None:
        ws = await make_workspace()
        cmd = UpdateWorkspaceSecurityPolicyCommand(
            caller_id=str(ws.owner_ids[0]),
            workspace_id=str(ws.id),
            pin_code_enabled=True,
            password_enabled=True,
            require_2fa=True,
        )
        await handler.handle(cmd)

        found = await ws_repo.get_by_id(ws.id)
        assert found is not None
        assert found.security_policy.pin_code_enabled is True
        assert found.security_policy.password_enabled is True
        assert found.security_policy.require_2fa is True

    async def test_update_security_policy_not_found(self, handler) -> None:
        cmd = UpdateWorkspaceSecurityPolicyCommand(
            caller_id=str(Id.generate()),
            workspace_id=str(Id.generate()),
            pin_code_enabled=True,
        )
        with pytest.raises(WorkspaceNotFoundException):
            await handler.handle(cmd)
