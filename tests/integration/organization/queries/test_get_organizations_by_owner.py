"""Интеграционные тесты GetOrganizationsByOwnerHandler (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.organization_dto import OrganizationListDTO
from app.context.organization.application.queries.get_organizations_by_owner import (
    GetOrganizationsByOwnerHandler,
    GetOrganizationsByOwnerQuery,
)


@pytest.mark.integration
class TestGetOrganizationsByOwnerHandler:
    @pytest.fixture
    def handler(self, org_repo, permission_checker_stub) -> GetOrganizationsByOwnerHandler:
        return GetOrganizationsByOwnerHandler(org_repo=org_repo, org_permission_checker=permission_checker_stub)

    async def test_returns_orgs_for_owner(self, handler, make_org) -> None:
        owner_id = Id.generate()
        org = await make_org(owner_id=owner_id)
        query = GetOrganizationsByOwnerQuery(caller_id=str(Id.generate()), owner_id=str(owner_id))
        result = await handler.handle(query)
        assert isinstance(result, OrganizationListDTO)
        assert any(i.id == str(org.id) for i in result.items)

    async def test_empty_for_unknown_owner(self, handler) -> None:
        query = GetOrganizationsByOwnerQuery(caller_id=str(Id.generate()), owner_id=str(Id.generate()))
        result = await handler.handle(query)
        assert result.total == 0
