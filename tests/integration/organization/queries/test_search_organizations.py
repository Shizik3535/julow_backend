"""Интеграционные тесты SearchOrganizationsHandler (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.organization_dto import OrganizationListDTO
from app.context.organization.application.queries.search_organizations import (
    SearchOrganizationsHandler,
    SearchOrganizationsQuery,
)


@pytest.mark.integration
class TestSearchOrganizationsHandler:
    @pytest.fixture
    def handler(self, org_repo, permission_checker_stub) -> SearchOrganizationsHandler:
        return SearchOrganizationsHandler(org_repo=org_repo, org_permission_checker=permission_checker_stub)

    async def test_search_with_name_filter(self, handler, make_org) -> None:
        await make_org(name="UniqueSearchName")
        query = SearchOrganizationsQuery(caller_id=str(Id.generate()), filters={"name": "UniqueSearchName"})
        result = await handler.handle(query)
        assert isinstance(result, OrganizationListDTO)
        assert result.total >= 1

    async def test_search_no_filters(self, handler, make_org) -> None:
        await make_org()
        query = SearchOrganizationsQuery(caller_id=str(Id.generate()))
        result = await handler.handle(query)
        assert result.total >= 1

    async def test_search_empty_result(self, handler) -> None:
        query = SearchOrganizationsQuery(caller_id=str(Id.generate()), filters={"name": "nonexistent-xyz-999"})
        result = await handler.handle(query)
        assert result.total == 0
