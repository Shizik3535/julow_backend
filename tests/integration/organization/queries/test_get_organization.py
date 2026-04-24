"""Интеграционные тесты GetOrganizationHandler (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.organization_dto import OrganizationDTO
from app.context.organization.application.queries.get_organization import (
    GetOrganizationHandler,
    GetOrganizationQuery,
)
from app.context.organization.domain.exceptions.organization_exceptions import OrganizationNotFoundException


@pytest.mark.integration
class TestGetOrganizationHandler:
    @pytest.fixture
    def handler(self, org_repo) -> GetOrganizationHandler:
        return GetOrganizationHandler(org_repo=org_repo)

    async def test_returns_dto(self, handler, make_org) -> None:
        org = await make_org(name="TestOrg")
        query = GetOrganizationQuery(org_id=str(org.id))
        result = await handler.handle(query)
        assert isinstance(result, OrganizationDTO)
        assert result.name == "TestOrg"
        assert result.status == "active"

    async def test_not_found_raises(self, handler) -> None:
        query = GetOrganizationQuery(org_id=str(Id.generate()))
        with pytest.raises(OrganizationNotFoundException):
            await handler.handle(query)
