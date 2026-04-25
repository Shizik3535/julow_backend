"""Интеграционные тесты GetOrgRolesHandler (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.application.dto.org_role_dto import OrgRoleListDTO
from app.context.organization.application.queries.get_org_roles import (
    GetOrgRolesHandler,
    GetOrgRolesQuery,
)


@pytest.mark.integration
class TestGetOrgRolesHandler:
    @pytest.fixture
    def handler(self, org_role_repo, org_repo, permission_checker_stub) -> GetOrgRolesHandler:
        return GetOrgRolesHandler(role_repo=org_role_repo, org_repo=org_repo, org_permission_checker=permission_checker_stub)

    async def test_returns_roles_for_org(self, handler, make_org_with_membership) -> None:
        data = await make_org_with_membership()
        query = GetOrgRolesQuery(caller_id=str(Id.generate()), org_id=str(data["org"].id))
        result = await handler.handle(query)
        assert isinstance(result, OrgRoleListDTO)
        assert result.total >= 1

    async def test_system_only(self, handler, make_org_with_membership) -> None:
        data = await make_org_with_membership()
        query = GetOrgRolesQuery(caller_id=str(Id.generate()), org_id=str(data["org"].id), system_only=True)
        result = await handler.handle(query)
        assert all(r.is_system for r in result.items)

    async def test_unknown_org_raises_not_found(self, handler) -> None:
        from app.context.organization.domain.exceptions.organization_exceptions import OrganizationNotFoundException

        query = GetOrgRolesQuery(caller_id=str(Id.generate()), org_id=str(Id.generate()))
        with pytest.raises(OrganizationNotFoundException):
            await handler.handle(query)
