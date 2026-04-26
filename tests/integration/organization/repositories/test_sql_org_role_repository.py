"""Интеграционные тесты SqlOrgRoleRepository (реальная PostgreSQL)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.aggregates.org_role import OrgRole
from app.context.organization.domain.value_objects.org_role_scope import OrgRoleScope
from app.context.organization.infrastructure.persistence.repositories.sql_org_role_repository import (
    SqlOrgRoleRepository,
)


@pytest.mark.integration
class TestSqlOrgRoleRepositoryAdd:
    """Тесты добавления."""

    async def test_add_and_get_by_id(self, org_role_repo: SqlOrgRoleRepository, make_org_role) -> None:
        role = await make_org_role(name="test-role")
        found = await org_role_repo.get_by_id(role.id)
        assert found is not None
        assert found.id == role.id

    async def test_add_persists_attributes(self, org_role_repo: SqlOrgRoleRepository, make_org_role) -> None:
        role = await make_org_role(name="custom", permissions=["members.read"], scope=OrgRoleScope.ORG, description="desc")
        found = await org_role_repo.get_by_id(role.id)
        assert found is not None
        assert found.name == "custom"
        assert "members.read" in found.permissions
        assert found.scope == OrgRoleScope.ORG
        assert found.description == "desc"


@pytest.mark.integration
class TestSqlOrgRoleRepositorySearch:
    """Тесты поиска."""

    async def test_get_by_name_found(self, org_role_repo: SqlOrgRoleRepository, make_org_role) -> None:
        role = await make_org_role(name="findable-role")
        found = await org_role_repo.get_by_name("findable-role")
        assert found is not None
        assert found.id == role.id

    async def test_get_by_name_not_found(self, org_role_repo: SqlOrgRoleRepository) -> None:
        found = await org_role_repo.get_by_name("nonexistent-role-xyz")
        assert found is None

    async def test_get_system_roles(self, org_role_repo: SqlOrgRoleRepository, make_org_role) -> None:
        role = await make_org_role()
        role.is_system = True
        role.clear_domain_events()
        await org_role_repo.update(role)

        system_roles = await org_role_repo.get_system_roles()
        assert len(system_roles) >= 1

    async def test_get_by_org(self, org_role_repo: SqlOrgRoleRepository, make_org_role, make_org) -> None:
        org = await make_org()
        role = await make_org_role(org_id=org.id)
        found = await org_role_repo.get_by_org(org.id)
        assert len(found) >= 1
        assert any(r.id == role.id for r in found)

    async def test_get_by_org_and_name_found(
        self, org_role_repo: SqlOrgRoleRepository, make_org_role, make_org
    ) -> None:
        org = await make_org()
        role = await make_org_role(org_id=org.id, name="specific-name")
        found = await org_role_repo.get_by_org_and_name(org.id, "specific-name")
        assert found is not None
        assert found.id == role.id

    async def test_get_by_org_and_name_not_found(
        self, org_role_repo: SqlOrgRoleRepository, make_org
    ) -> None:
        org = await make_org()
        found = await org_role_repo.get_by_org_and_name(org.id, "nonexistent")
        assert found is None

    async def test_search_with_filters(self, org_role_repo: SqlOrgRoleRepository, make_org_role) -> None:
        role = await make_org_role(name="searchable-role")
        results = await org_role_repo.search(filters={"name": "searchable-role"})
        assert len(results) >= 1


@pytest.mark.integration
class TestSqlOrgRoleRepositoryUpdate:
    """Тесты обновления."""

    async def test_update_permissions(self, org_role_repo: SqlOrgRoleRepository, make_org_role) -> None:
        role = await make_org_role(permissions=["org.read"])
        role.update(permissions=["members.*", "teams.*"])
        role.clear_domain_events()
        await org_role_repo.update(role)

        found = await org_role_repo.get_by_id(role.id)
        assert found is not None
        assert found.permissions == ["members.*", "teams.*"]

    async def test_update_description(self, org_role_repo: SqlOrgRoleRepository, make_org_role) -> None:
        role = await make_org_role()
        role.update(description="new description")
        role.clear_domain_events()
        await org_role_repo.update(role)

        found = await org_role_repo.get_by_id(role.id)
        assert found is not None
        assert found.description == "new description"


@pytest.mark.integration
class TestSqlOrgRoleRepositoryDelete:
    """Тесты удаления."""

    async def test_delete(self, org_role_repo: SqlOrgRoleRepository, make_org_role) -> None:
        role = await make_org_role()
        await org_role_repo.delete(role.id)
        found = await org_role_repo.get_by_id(role.id)
        assert found is None
