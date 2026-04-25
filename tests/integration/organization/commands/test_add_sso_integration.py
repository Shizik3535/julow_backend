"""Интеграционные тесты AddSSOIntegrationHandler (реальные repos + stubs)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.commands.add_sso_integration import (
    AddSSOIntegrationCommand,
    AddSSOIntegrationHandler,
)
from app.context.organization.application.dto.sso_integration_dto import SSOIntegrationDTO


@pytest.mark.integration
class TestAddSSOIntegrationHandler:
    @pytest.fixture
    def handler(self, sso_repo, org_repo, encryption_stub, permission_checker_stub, event_bus_stub):
        return AddSSOIntegrationHandler(
            sso_repo=sso_repo,
            org_repo=org_repo,
            encryption_port=encryption_stub,
            org_permission_checker=permission_checker_stub,
            event_bus=event_bus_stub,
        )

    async def test_add_sso(self, handler, make_org) -> None:
        org = await make_org()
        cmd = AddSSOIntegrationCommand(
            caller_id=str(Id.generate()),
            org_id=str(org.id),
            provider="saml",
            entity_id="entity-123",
            sso_url="https://sso.example.com",
            certificate="my-cert-data",
            added_by=str(Id.generate()),
        )
        result = await handler.handle(cmd)
        assert isinstance(result, SSOIntegrationDTO)
        assert result.provider == "saml"
        assert result.entity_id == "entity-123"

    async def test_certificate_is_encrypted(self, handler, make_org, sso_repo) -> None:
        org = await make_org()
        cmd = AddSSOIntegrationCommand(
            caller_id=str(Id.generate()),
            org_id=str(org.id),
            provider="oidc",
            entity_id="entity-oidc",
            sso_url="https://oidc.example.com",
            certificate="secret-cert",
            added_by=str(Id.generate()),
        )
        result = await handler.handle(cmd)
        sso = await sso_repo.get_by_id(Id.from_string(result.id))
        assert sso is not None
        assert sso.certificate.startswith("enc:")
