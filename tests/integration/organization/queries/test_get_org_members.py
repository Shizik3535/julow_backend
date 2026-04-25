"""Интеграционные тесты GetOrgMembersHandler (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.org_member_dto import OrgMemberListDTO
from app.context.organization.application.queries.get_org_members import (
    GetOrgMembersHandler,
    GetOrgMembersQuery,
)


@pytest.mark.integration
class TestGetOrgMembersHandler:
    @pytest.fixture
    def handler(self, membership_repo, org_repo, permission_checker_stub) -> GetOrgMembersHandler:
        return GetOrgMembersHandler(membership_repo=membership_repo, org_repo=org_repo, org_permission_checker=permission_checker_stub)

    async def test_returns_members_list(self, handler, make_org_with_membership) -> None:
        data = await make_org_with_membership()
        query = GetOrgMembersQuery(caller_id=str(Id.generate()), org_id=str(data["org"].id))
        result = await handler.handle(query)
        assert isinstance(result, OrgMemberListDTO)
        assert result.total >= 1

    async def test_not_found_raises_for_unknown_org(self, handler) -> None:
        from app.context.organization.domain.exceptions.organization_exceptions import OrganizationNotFoundException

        query = GetOrgMembersQuery(caller_id=str(Id.generate()), org_id=str(Id.generate()))
        with pytest.raises(OrganizationNotFoundException):
            await handler.handle(query)
