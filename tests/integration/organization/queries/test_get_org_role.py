"""Интеграционные тесты GetOrgRoleHandler (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.org_role_dto import OrgRoleDTO
from app.context.organization.application.queries.get_org_role import (
    GetOrgRoleHandler,
    GetOrgRoleQuery,
)
from app.context.organization.domain.exceptions.org_role_exceptions import OrgRoleNotFoundException


@pytest.mark.integration
class TestGetOrgRoleHandler:
    @pytest.fixture
    def handler(self, org_role_repo, permission_checker_stub) -> GetOrgRoleHandler:
        return GetOrgRoleHandler(role_repo=org_role_repo, org_permission_checker=permission_checker_stub)

    async def test_returns_role_dto(self, handler, make_org_role) -> None:
        role = await make_org_role(name="viewer")
        query = GetOrgRoleQuery(caller_id=str(Id.generate()), org_id=str(role.org_id) if role.org_id else str(Id.generate()), role_id=str(role.id))
        result = await handler.handle(query)
        assert isinstance(result, OrgRoleDTO)
        assert result.name == "viewer"

    async def test_not_found_raises(self, handler) -> None:
        query = GetOrgRoleQuery(caller_id=str(Id.generate()), org_id=str(Id.generate()), role_id=str(Id.generate()))
        with pytest.raises(OrgRoleNotFoundException):
            await handler.handle(query)
