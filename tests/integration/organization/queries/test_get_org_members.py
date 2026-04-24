"""Интеграционные тесты GetOrgMembersHandler (реальные repos)."""

import pytest

from app.context.organization.application.dto.org_member_dto import OrgMemberListDTO
from app.context.organization.application.queries.get_org_members import (
    GetOrgMembersHandler,
    GetOrgMembersQuery,
)


@pytest.mark.integration
class TestGetOrgMembersHandler:
    @pytest.fixture
    def handler(self, membership_repo) -> GetOrgMembersHandler:
        return GetOrgMembersHandler(membership_repo=membership_repo)

    async def test_returns_members_list(self, handler, make_org_with_membership) -> None:
        data = await make_org_with_membership()
        query = GetOrgMembersQuery(org_id=str(data["org"].id))
        result = await handler.handle(query)
        assert isinstance(result, OrgMemberListDTO)
        assert result.total >= 1

    async def test_empty_for_unknown_org(self, handler) -> None:
        from app.shared.domain.value_objects.id_vo import Id

        query = GetOrgMembersQuery(org_id=str(Id.generate()))
        result = await handler.handle(query)
        assert result.total == 0
