"""Интеграционные тесты UpdateSSOIntegrationHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.update_sso_integration import (
    UpdateSSOIntegrationCommand,
    UpdateSSOIntegrationHandler,
)


@pytest.mark.integration
class TestUpdateSSOIntegrationHandler:
    @pytest.fixture
    def handler(self, sso_repo, encryption_stub, event_bus_stub):
        return UpdateSSOIntegrationHandler(
            sso_repo=sso_repo,
            encryption_port=encryption_stub,
            event_bus=event_bus_stub,
        )

    async def test_update_entity_id(self, handler, make_sso_integration, sso_repo) -> None:
        sso = await make_sso_integration()
        cmd = UpdateSSOIntegrationCommand(
            integration_id=str(sso.id),
            entity_id="new-entity-id",
        )
        await handler.handle(cmd)
        found = await sso_repo.get_by_id(sso.id)
        assert found is not None
        assert found.entity_id == "new-entity-id"

    async def test_update_certificate_encrypts(self, handler, make_sso_integration, sso_repo) -> None:
        sso = await make_sso_integration()
        cmd = UpdateSSOIntegrationCommand(
            integration_id=str(sso.id),
            certificate="new-secret-cert",
        )
        await handler.handle(cmd)
        found = await sso_repo.get_by_id(sso.id)
        assert found is not None
        assert found.certificate.startswith("enc:")
