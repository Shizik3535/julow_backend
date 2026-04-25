"""Интеграционные тесты GetOrgMemberHandler (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.org_member_dto import OrgMemberDTO
from app.context.organization.application.queries.get_org_member import (
    GetOrgMemberHandler,
    GetOrgMemberQuery,
)
from app.context.organization.domain.exceptions.org_membership_exceptions import OrgMemberNotFoundException


@pytest.mark.integration
class TestGetOrgMemberHandler:
    @pytest.fixture
    def handler(self, membership_repo, permission_checker_stub) -> GetOrgMemberHandler:
        return GetOrgMemberHandler(membership_repo=membership_repo, org_permission_checker=permission_checker_stub)

    async def test_returns_member_dto(self, handler, make_org_with_membership) -> None:
        data = await make_org_with_membership()
        query = GetOrgMemberQuery(caller_id=str(Id.generate()), org_id=str(data["org"].id), user_id=str(data["owner_id"]))
        result = await handler.handle(query)
        assert isinstance(result, OrgMemberDTO)
        assert result.user_id == str(data["owner_id"])

    async def test_not_found_raises(self, handler, make_org_with_membership) -> None:
        data = await make_org_with_membership()
        query = GetOrgMemberQuery(caller_id=str(Id.generate()), org_id=str(data["org"].id), user_id=str(Id.generate()))
        with pytest.raises(OrgMemberNotFoundException):
            await handler.handle(query)
