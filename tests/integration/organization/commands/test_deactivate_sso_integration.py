"""Интеграционные тесты DeactivateSSOIntegrationHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.deactivate_sso_integration import (
    DeactivateSSOIntegrationCommand,
    DeactivateSSOIntegrationHandler,
)


@pytest.mark.integration
class TestDeactivateSSOIntegrationHandler:
    @pytest.fixture
    def handler(self, sso_repo, permission_checker_stub, event_bus_stub):
        return DeactivateSSOIntegrationHandler(
            sso_repo=sso_repo,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_deactivate(self, handler, make_sso_integration, sso_repo) -> None:
        sso = await make_sso_integration()
        cmd = DeactivateSSOIntegrationCommand(
            caller_id=str(Id.generate()),
            org_id=str(sso.org_id),
            integration_id=str(sso.id),
        )
        await handler.handle(cmd)
        found = await sso_repo.get_by_id(sso.id)
        assert found is not None
        assert found.is_active is False
