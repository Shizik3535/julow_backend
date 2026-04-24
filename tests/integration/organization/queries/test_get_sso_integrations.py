"""Интеграционные тесты GetSSOIntegrationsHandler (реальные repos)."""

import pytest

from app.context.organization.application.dto.sso_integration_dto import SSOIntegrationListDTO
from app.context.organization.application.queries.get_sso_integrations import (
    GetSSOIntegrationsHandler,
    GetSSOIntegrationsQuery,
)


@pytest.mark.integration
class TestGetSSOIntegrationsHandler:
    @pytest.fixture
    def handler(self, sso_repo) -> GetSSOIntegrationsHandler:
        return GetSSOIntegrationsHandler(sso_repo=sso_repo)

    async def test_returns_sso_list(self, handler, make_sso_integration, make_org) -> None:
        org = await make_org()
        sso = await make_sso_integration(org_id=org.id)
        query = GetSSOIntegrationsQuery(org_id=str(org.id))
        result = await handler.handle(query)
        assert isinstance(result, SSOIntegrationListDTO)
        assert any(i.id == str(sso.id) for i in result.items)

    async def test_empty_for_unknown_org(self, handler) -> None:
        from app.shared.domain.value_objects.id_vo import Id

        query = GetSSOIntegrationsQuery(org_id=str(Id.generate()))
        result = await handler.handle(query)
        assert result.total == 0
