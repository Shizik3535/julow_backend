"""Интеграционные тесты UpdateSecurityPolicyHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.update_security_policy import (
    UpdateSecurityPolicyCommand,
    UpdateSecurityPolicyHandler,
)


@pytest.mark.integration
class TestUpdateSecurityPolicyHandler:
    @pytest.fixture
    def handler(self, org_repo, event_bus_stub):
        return UpdateSecurityPolicyHandler(org_repo=org_repo, event_bus=event_bus_stub)

    async def test_update_policy(self, handler, make_org, org_repo) -> None:
        org = await make_org()
        cmd = UpdateSecurityPolicyCommand(
            org_id=str(org.id), require_2fa=True, password_min_length=12
        )
        await handler.handle(cmd)
        found = await org_repo.get_by_id(org.id)
        assert found is not None
        assert found.security_policy.require_2fa is True
        assert found.security_policy.password_min_length == 12
